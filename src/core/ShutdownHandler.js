/**
 * Graceful Shutdown Handler
 * Manages clean shutdown of all system components
 */

import { EventEmitter } from 'events';

class ShutdownHandler extends EventEmitter {
  constructor(config = {}) {
    super();
    
    this.config = {
      gracePeriod: config.gracePeriod || 30000, // 30 seconds
      forceShutdownDelay: config.forceShutdownDelay || 5000,
      ...config
    };

    this.state = {
      shutdownInitiated: false,
      shutdownReason: null,
      shutdownStartTime: null
    };

    this.shutdownHooks = [];
    this.activeOperations = new Set();
    this.initialized = false;
  }

  /**
   * Initialize shutdown handlers
   */
  initialize() {
    if (this.initialized) {
      return;
    }

    // Handle SIGTERM (normal shutdown, e.g., from systemd)
    process.on('SIGTERM', () => {
      this.initiateShutdown('SIGTERM');
    });

    // Handle SIGINT (Ctrl+C)
    process.on('SIGINT', () => {
      this.initiateShutdown('SIGINT');
    });

    // Handle SIGHUP (reload config)
    process.on('SIGHUP', () => {
      this.handleReload();
    });

    this.initialized = true;
    console.log('✅ ShutdownHandler initialized');
  }

  /**
   * Register a shutdown hook
   * Hooks are executed in reverse order of registration
   */
  registerHook(name, handler, priority = 0) {
    this.shutdownHooks.push({
      name,
      handler,
      priority,
      executed: false
    });

    // Sort by priority (higher priority runs first)
    this.shutdownHooks.sort((a, b) => b.priority - a.priority);

    console.log(`🔗 Registered shutdown hook: ${name} (priority: ${priority})`);
  }

  /**
   * Track an active operation
   */
  trackOperation(operationId, description) {
    this.activeOperations.add({
      id: operationId,
      description,
      startedAt: Date.now()
    });

    return () => this.completeOperation(operationId);
  }

  /**
   * Mark operation as complete
   */
  completeOperation(operationId) {
    for (const op of this.activeOperations) {
      if (op.id === operationId) {
        this.activeOperations.delete(op);
        break;
      }
    }
  }

  /**
   * Check if continuous mode is enabled
   * Uses consistent boolean parsing across the system
   */
  isContinuousMode() {
    return process.env.CONTINUOUS_MODE === 'true' || 
           (process.env.CONTINUOUS_MODE !== 'false' && process.env.CONTINUOUS_MODE !== undefined);
  }

  /**
   * Initiate graceful shutdown
   * In continuous mode, this performs cleanup but doesn't exit
   */
  async initiateShutdown(reason = 'manual') {
    if (this.state.shutdownInitiated) {
      console.log('⚠️ Shutdown already in progress...');
      return;
    }

    this.state.shutdownInitiated = true;
    this.state.shutdownReason = reason;
    this.state.shutdownStartTime = Date.now();

    console.log(`\n🛑 Graceful shutdown initiated: ${reason}`);
    console.log(`⏱️ Grace period: ${this.config.gracePeriod}ms`);

    this.emit('shutdownInitiated', { reason });

    try {
      // Step 1: Stop accepting new requests
      await this.stopAcceptingRequests();

      // Step 2: Wait for in-flight operations with timeout
      await this.waitForOperations();

      // Step 3: Execute shutdown hooks
      await this.executeShutdownHooks();

      // Step 4: Final cleanup
      await this.finalCleanup();

      console.log('✅ Graceful shutdown complete');
      this.emit('shutdownComplete');

      // CONTINUOUS MODE: Don't exit, allow restart/reconnect
      if (this.isContinuousMode()) {
        console.log('🔄 Continuous mode enabled - will restart instead of exiting');
        this.state.shutdownInitiated = false; // Reset for restart
        this.emit('restartInitiated');
        // Let the application handle restart, don't exit
        return;
      }

      // Exit with success code (only in non-continuous mode)
      process.exit(0);

    } catch (error) {
      console.error('❌ Error during shutdown:', error);
      this.emit('shutdownError', error);

      // In continuous mode, retry instead of exit
      if (this.isContinuousMode()) {
        console.log('🔄 Continuous mode - resetting for retry...');
        this.state.shutdownInitiated = false;
        setTimeout(() => {
          this.emit('restartInitiated');
        }, this.config.forceShutdownDelay);
        return;
      }

      // Force shutdown after delay (non-continuous mode only)
      console.log(`⚠️ Forcing shutdown in ${this.config.forceShutdownDelay}ms...`);
      setTimeout(() => {
        process.exit(1);
      }, this.config.forceShutdownDelay);
    }
  }

  /**
   * Stop accepting new requests
   */
  async stopAcceptingRequests() {
    console.log('🚫 Stopping new requests...');
    this.emit('stopNewRequests');
    
    // Give signal handlers time to process
    await this.sleep(100);
    
    console.log('✅ No longer accepting new requests');
  }

  /**
   * Wait for active operations to complete
   */
  async waitForOperations() {
    if (this.activeOperations.size === 0) {
      console.log('✅ No active operations');
      return;
    }

    console.log(`⏳ Waiting for ${this.activeOperations.size} active operations...`);
    
    const deadline = Date.now() + this.config.gracePeriod;
    
    while (this.activeOperations.size > 0 && Date.now() < deadline) {
      await this.sleep(100);
    }

    if (this.activeOperations.size > 0) {
      console.warn(`⚠️ ${this.activeOperations.size} operations still active, proceeding anyway`);
      this.activeOperations.forEach(op => {
        console.warn(`  - ${op.description} (running for ${Date.now() - op.startedAt}ms)`);
      });
    } else {
      console.log('✅ All operations completed');
    }
  }

  /**
   * Execute all shutdown hooks
   */
  async executeShutdownHooks() {
    if (this.shutdownHooks.length === 0) {
      console.log('✅ No shutdown hooks registered');
      return;
    }

    console.log(`🔧 Executing ${this.shutdownHooks.length} shutdown hooks...`);

    for (const hook of this.shutdownHooks) {
      if (hook.executed) {
        continue;
      }

      try {
        console.log(`  ▶️ ${hook.name}...`);
        await hook.handler();
        hook.executed = true;
        console.log(`  ✅ ${hook.name} complete`);
      } catch (error) {
        console.error(`  ❌ ${hook.name} failed:`, error.message);
        // Continue with other hooks even if one fails
      }
    }

    console.log('✅ Shutdown hooks executed');
  }

  /**
   * Final cleanup tasks
   */
  async finalCleanup() {
    console.log('🧹 Final cleanup...');

    // Clear all timers and intervals (those tracked by us)
    this.emit('cleanup');

    // Give final cleanup time to complete
    await this.sleep(100);

    console.log('✅ Cleanup complete');
  }

  /**
   * Handle config reload (SIGHUP)
   */
  handleReload() {
    console.log('🔄 Config reload requested (SIGHUP)');
    this.emit('reload');
    
    // Don't exit on reload
    console.log('✅ Config reload signal handled');
  }

  /**
   * Trigger immediate shutdown
   */
  async forceShutdown(reason = 'forced') {
    console.warn(`⚡ Force shutdown: ${reason}`);
    
    this.emit('forceShutdown', { reason });
    
    // Skip graceful shutdown, execute critical hooks only
    const criticalHooks = this.shutdownHooks.filter(h => h.priority >= 100);
    
    for (const hook of criticalHooks) {
      try {
        await Promise.race([
          hook.handler(),
          this.timeout(1000) // 1 second max per hook
        ]);
      } catch (error) {
        console.error(`❌ Critical hook ${hook.name} failed:`, error.message);
      }
    }

    process.exit(1);
  }

  /**
   * Check if shutdown is in progress
   */
  isShuttingDown() {
    return this.state.shutdownInitiated;
  }

  /**
   * Get shutdown state
   */
  getState() {
    return {
      ...this.state,
      activeOperations: this.activeOperations.size,
      shutdownHooks: this.shutdownHooks.length,
      elapsedTime: this.state.shutdownStartTime 
        ? Date.now() - this.state.shutdownStartTime 
        : 0
    };
  }

  /**
   * Helper: sleep for specified milliseconds
   */
  sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * Helper: timeout promise
   */
  timeout(ms) {
    return new Promise((_, reject) => 
      setTimeout(() => reject(new Error('Timeout')), ms)
    );
  }
}

export default ShutdownHandler;
