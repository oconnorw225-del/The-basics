// Jest setup file - Simplified for Node environment

// Mock environment variables
process.env.NODE_ENV = 'test';
process.env.PORT = '3001';
process.env.KILL_SWITCH_ENABLED = 'false';

// Global test timeout
jest.setTimeout(10000);

// Suppress console errors in tests
global.console = {
  ...console,
  error: jest.fn(),
  warn: jest.fn(),
};
