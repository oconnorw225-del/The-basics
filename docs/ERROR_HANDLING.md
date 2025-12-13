# Error Handling Guide

## Overview

The Error Handling System provides comprehensive error management across the entire application, including:
- Automatic error recovery
- Circuit breaker pattern for external services
- Retry logic with exponential backoff
- Error logging and notification
- Graceful degradation

## Components

### ErrorHandler Class

The `ErrorHandler` class is the central component for error management.

```javascript
import ErrorHandler from './core/ErrorHandler.js';

const errorHandler = new ErrorHandler({
  logErrors: true,
  logPath: './logs/errors.log',
  maxRetries: 3,
  retryDelay: 1000,
  circuitBreakerThreshold: 5
});

errorHandler.initialize();
```

## Error Types Handled

### 1. Uncaught Exceptions

Automatically caught and logged. The system will attempt graceful shutdown.

```javascript
// Automatically handled by ErrorHandler
process.on('uncaughtException', (error) => {
  // ErrorHandler manages this
});
```

### 2. Unhandled Promise Rejections

All unhandled promise rejections are caught and logged.

```javascript
// Automatically handled
process.on('unhandledRejection', (reason, promise) => {
  // ErrorHandler manages this
});
```

### 3. API Errors

Use the API error handler for external service calls:

```javascript
try {
  const response = await fetch('https://api.example.com/data');
  errorHandler.recordServiceSuccess('api-example');
} catch (error) {
  await errorHandler.handleApiError(error, {
    service: 'api-example',
    endpoint: '/data',
    method: 'GET'
  });
}
```

### 4. Database Errors

Handle database connection and query errors:

```javascript
try {
  await database.query('SELECT * FROM users');
} catch (error) {
  await errorHandler.handleDatabaseError(error, {
    operation: 'query',
    table: 'users'
  });
}
```

### 5. File System Errors

Handle file operations:

```javascript
try {
  await fs.readFile('/path/to/file');
} catch (error) {
  await errorHandler.handleFileSystemError(error, {
    operation: 'read',
    path: '/path/to/file'
  });
}
```

## Retry Logic

Use the built-in retry mechanism for operations that may fail temporarily:

```javascript
const result = await errorHandler.withRetry(
  async () => {
    return await unreliableOperation();
  },
  {
    maxRetries: 5,
    retryDelay: 2000,
    context: { operation: 'unreliable-op' },
    onRetry: async (error, attempt) => {
      console.log(`Retry attempt ${attempt}: ${error.message}`);
    }
  }
);
```

**Features:**
- Exponential backoff (delay doubles with each retry)
- Customizable retry count and delay
- Optional callback on each retry
- Context tracking for debugging

## Circuit Breaker Pattern

The circuit breaker prevents cascading failures when external services are down.

**States:**
- **Closed**: Normal operation, requests pass through
- **Open**: Too many failures, requests fail fast
- **Half-Open**: Testing if service recovered

```javascript
// Check if circuit is open
if (errorHandler.isCircuitOpen('external-service')) {
  throw new Error('Service temporarily unavailable');
}

try {
  await callExternalService();
  errorHandler.recordServiceSuccess('external-service');
} catch (error) {
  await errorHandler.handleApiError(error, {
    service: 'external-service'
  });
}
```

**Configuration:**
- `circuitBreakerThreshold`: Number of failures before opening (default: 5)
- Circuit auto-resets to half-open after 60 seconds

## Error Statistics

Track error metrics:

```javascript
const stats = errorHandler.getStats();
console.log(stats);
// {
//   totalErrors: 42,
//   uncaughtExceptions: 0,
//   unhandledRejections: 5,
//   apiErrors: 30,
//   databaseErrors: 7,
//   recoveredErrors: 25,
//   fatalErrors: 0
// }
```

## Event Listeners

Subscribe to error events:

```javascript
errorHandler.on('apiError', ({ error, context }) => {
  console.error('API Error:', error.message);
  // Send to monitoring service
});

errorHandler.on('circuitBreakerOpened', ({ serviceName, failures }) => {
  console.warn(`Circuit breaker opened for ${serviceName}`);
  // Alert operations team
});

errorHandler.on('errorLogged', (logEntry) => {
  // Send to external logging service
});
```

**Available Events:**
- `initialized` - ErrorHandler initialized
- `uncaughtException` - Uncaught exception occurred
- `unhandledRejection` - Unhandled promise rejection
- `apiError` - API error occurred
- `databaseError` - Database error occurred
- `fileSystemError` - File system error occurred
- `configError` - Configuration error occurred
- `error` - Generic error occurred
- `circuitBreakerOpened` - Circuit breaker opened for a service
- `circuitBreakerClosed` - Circuit breaker closed for a service
- `errorLogged` - Error logged to file

## Best Practices

### 1. Always Initialize Early

Initialize the ErrorHandler as early as possible in your application:

```javascript
import ErrorHandler from './core/ErrorHandler.js';

const errorHandler = new ErrorHandler();
errorHandler.initialize();

// Now start the rest of your app
```

### 2. Use Specific Error Handlers

Use the appropriate error handler for each error type:

```javascript
// ❌ Don't
try {
  await database.query();
} catch (error) {
  console.error(error);
}

// ✅ Do
try {
  await database.query();
} catch (error) {
  await errorHandler.handleDatabaseError(error, {
    operation: 'query',
    table: 'users'
  });
}
```

### 3. Provide Context

Always provide context when handling errors:

```javascript
await errorHandler.handleApiError(error, {
  service: 'stripe',
  endpoint: '/charges',
  method: 'POST',
  userId: user.id,
  amount: charge.amount
});
```

### 4. Use Retry for Transient Failures

Use retry logic for operations that may fail temporarily:

```javascript
// Network requests
// Database connections
// File locks
// External API calls
```

### 5. Don't Retry for Permanent Failures

Don't retry operations that will never succeed:

```javascript
// Authentication failures
// Validation errors
// Authorization errors
// Resource not found errors
```

### 6. Monitor Circuit Breakers

Watch for circuit breaker events and investigate when they open:

```javascript
errorHandler.on('circuitBreakerOpened', ({ serviceName, failures }) => {
  // Alert team
  // Check service health
  // Review logs
});
```

## Error Log Format

Errors are logged in JSON format:

```json
{
  "timestamp": "2025-12-13T21:30:47.256Z",
  "type": "API_ERROR",
  "message": "Request timeout",
  "stack": "Error: Request timeout\n    at ...",
  "context": {
    "service": "stripe",
    "endpoint": "/charges",
    "method": "POST"
  },
  "stats": {
    "totalErrors": 42,
    "apiErrors": 30,
    ...
  }
}
```

## Integration with Other Systems

### With FeatureManager

```javascript
featureManager.on('featureError', async ({ name, error }) => {
  await errorHandler.handleError('FEATURE_ERROR', error, {
    feature: name
  });
});
```

### With HealthMonitor

```javascript
healthMonitor.on('unhealthy', async (metrics) => {
  await errorHandler.handleError('HEALTH_CHECK_FAILED', 
    new Error('System unhealthy'), 
    { metrics }
  );
});
```

## Shutdown

Always shutdown gracefully:

```javascript
await errorHandler.shutdown();
```

This ensures:
- Pending log writes complete
- Event listeners are cleaned up
- Resources are released

## Troubleshooting

### Errors Not Being Logged

1. Check that ErrorHandler is initialized
2. Verify logPath is writable
3. Check logErrors config is true

### Circuit Breaker Always Open

1. Check service is actually available
2. Review circuitBreakerThreshold setting
3. Monitor service success/failure ratio
4. Circuit resets to half-open after 60s

### High Error Rates

1. Check error statistics with `getStats()`
2. Review error logs for patterns
3. Check external service health
4. Review retry configurations

## Example: Complete Integration

```javascript
import ErrorHandler from './core/ErrorHandler.js';
import config from '../config/error-handling.json' assert { type: 'json' };

// Initialize
const errorHandler = new ErrorHandler(config.errorHandler);
errorHandler.initialize();

// Use in application
class APIClient {
  constructor() {
    this.errorHandler = errorHandler;
  }

  async fetchData(endpoint) {
    return await this.errorHandler.withRetry(
      async () => {
        if (this.errorHandler.isCircuitOpen('api')) {
          throw new Error('API circuit breaker open');
        }

        try {
          const response = await fetch(endpoint);
          this.errorHandler.recordServiceSuccess('api');
          return response;
        } catch (error) {
          await this.errorHandler.handleApiError(error, {
            service: 'api',
            endpoint
          });
          throw error;
        }
      },
      {
        maxRetries: 3,
        retryDelay: 1000,
        context: { endpoint }
      }
    );
  }
}

// On shutdown
process.on('SIGTERM', async () => {
  await errorHandler.shutdown();
  process.exit(0);
});
```
