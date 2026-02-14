import { describe, it, expect, beforeAll, afterAll } from '@jest/globals';
import request from 'supertest';
import { RATE_LIMIT_MAX } from '../../middleware/security.js';

// Import the app factory
async function getApp() {
  const { default: app } = await import('../../server.js');
  return app;
}

describe('Security Headers', () => {
  let app;
  let server;
  
  beforeAll(async () => {
    app = await getApp();
  });
  
  afterAll(async () => {
    // Close server if it was started
    if (server) {
      await new Promise((resolve) => server.close(resolve));
    }
  });
  
  it('should include security headers', async () => {
    const response = await request(app).get('/health');
    
    expect(response.headers['x-content-type-options']).toBe('nosniff');
    expect(response.headers['x-frame-options']).toBeDefined();
    expect(response.headers['strict-transport-security']).toBeDefined();
  });
  
  it('should enforce rate limiting', async () => {
    const EXTRA_REQUESTS = 50;
    const requests = [];
    
    for (let i = 0; i < RATE_LIMIT_MAX + EXTRA_REQUESTS; i++) {
      requests.push(request(app).get('/health'));
    }
    
    const responses = await Promise.all(requests);
    const tooManyRequests = responses.filter(r => r.status === 429);
    
    expect(tooManyRequests.length).toBeGreaterThan(0);
  });
});
