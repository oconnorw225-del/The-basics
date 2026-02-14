/**
 * Comprehensive Bot System Tests
 */

describe('Bot System', () => {
  describe('Configuration', () => {
    test('should load kill-switch configuration', () => {
      const fs = require('fs');
      const config = JSON.parse(fs.readFileSync('config/kill-switch.json', 'utf8'));
      
      expect(config).toBeDefined();
      expect(config.enabled).toBe(false);
      expect(config.auto_trigger).toBe(false);
      expect(config.manual_override_allowed).toBe(true);
    });

    test('should load bot-limits configuration', () => {
      const fs = require('fs');
      const config = JSON.parse(fs.readFileSync('config/bot-limits.json', 'utf8'));
      
      expect(config).toBeDefined();
      expect(config.ndax_bot).toBeDefined();
      expect(config.quantum_bot).toBeDefined();
      expect(config.shadowforge_bot).toBeDefined();
      expect(config.global_limits).toBeDefined();
    });

    test('should load api-endpoints configuration', () => {
      const fs = require('fs');
      const config = JSON.parse(fs.readFileSync('config/api-endpoints.json', 'utf8'));
      
      expect(config).toBeDefined();
      expect(config.ndax_bot).toBeDefined();
      expect(config.quantum_bot).toBeDefined();
      expect(config.shadowforge_bot).toBeDefined();
    });
  });

  describe('Bot Limits', () => {
    test('should have valid bot limits', () => {
      const fs = require('fs');
      const limits = JSON.parse(fs.readFileSync('config/bot-limits.json', 'utf8'));
      
      expect(limits.ndax_bot.max_daily_loss).toBeGreaterThan(0);
      expect(limits.quantum_bot.max_daily_loss).toBeGreaterThan(0);
      expect(limits.shadowforge_bot.max_daily_loss).toBeGreaterThan(0);
    });

    test('should have global limits', () => {
      const fs = require('fs');
      const limits = JSON.parse(fs.readFileSync('config/bot-limits.json', 'utf8'));
      
      expect(limits.global_limits.total_max_daily_loss).toBeGreaterThan(0);
      expect(limits.global_limits.total_max_exposure).toBeGreaterThan(0);
    });
  });

  describe('API Endpoints', () => {
    test('should have unique ports for each bot', () => {
      const fs = require('fs');
      const endpoints = JSON.parse(fs.readFileSync('config/api-endpoints.json', 'utf8'));
      
      const ports = new Set();
      for (const [key, value] of Object.entries(endpoints)) {
        if (value && value.base_url) {
          const match = value.base_url.match(/:(\d+)/);
          if (match) {
            const port = match[1];
            expect(ports.has(port)).toBe(false);
            ports.add(port);
          }
        }
      }
    });
  });

  describe('Package Configuration', () => {
    test('should have test scripts configured', () => {
      const fs = require('fs');
      const pkg = JSON.parse(fs.readFileSync('package.json', 'utf8'));
      
      expect(pkg.scripts.test).toBeDefined();
      expect(pkg.scripts.test).not.toContain('No tests configured');
      expect(pkg.scripts['test:python']).toBeDefined();
      expect(pkg.scripts['test:all']).toBeDefined();
    });

    test('should have required dependencies', () => {
      const fs = require('fs');
      const pkg = JSON.parse(fs.readFileSync('package.json', 'utf8'));
      
      expect(pkg.devDependencies.jest).toBeDefined();
      expect(pkg.devDependencies['@testing-library/react']).toBeDefined();
    });
  });
});

describe('Security', () => {
  test('should not have hardcoded secrets', () => {
    const fs = require('fs');
    const files = ['bot.js', 'server.js', 'backend/bot-coordinator.py'];
    
    files.forEach(file => {
      if (fs.existsSync(file)) {
        const content = fs.readFileSync(file, 'utf8');
        expect(content).not.toMatch(/password\s*=\s*["'][^"']+["']/i);
        expect(content).not.toMatch(/api.?key\s*=\s*["'][a-zA-Z0-9]{20,}["']/i);
      }
    });
  });

  test('should have kill switch disabled by default', () => {
    const fs = require('fs');
    const config = JSON.parse(fs.readFileSync('config/kill-switch.json', 'utf8'));
    
    expect(config.enabled).toBe(false);
  });
});
