const request = require('supertest');
const app = require('../../server');

describe('Security Headers', () => {
  it('should include security headers', async () => {
    const response = await request(app).get('/');
    
    expect(response.headers['x-content-type-options']).toBe('nosniff');
    expect(response.headers['x-frame-options']).toBeDefined();
    expect(response.headers['x-xss-protection']).toBeDefined();
    expect(response.headers['strict-transport-security']).toBeDefined();
  });
  
  it('should enforce rate limiting', async () => {
    const requests = [];
    for (let i = 0; i < 150; i++) {
      requests.push(request(app).get('/'));
    }
    
    const responses = await Promise.all(requests);
    const tooManyRequests = responses.filter(r => r.status === 429);
    
    expect(tooManyRequests.length).toBeGreaterThan(0);
  });
});
