export default {
  testEnvironment: 'node',
  transform: {},
  extensionsToTreatAsEsm: ['.jsx'],
  moduleNameMapper: {
    '\\.(css|less|scss|sass)$': 'identity-obj-proxy',
  },
  testMatch: [
    '**/tests/**/*.test.js',
    '**/tests/**/*.test.jsx',
    '**/__tests__/**/*.js',
    '**/__tests__/**/*.jsx'
  ],
  collectCoverageFrom: [
    'backend/**/*.js',
    '!**/node_modules/**',
    '!**/dist/**',
    '!**/coverage/**',
    '!src/**' // Exclude React/JSX files
  ],
  coverageThreshold: {
    global: {
      branches: 0,
      functions: 0,
      lines: 0,
      statements: 0
    }
  },
  testTimeout: 10000
};
