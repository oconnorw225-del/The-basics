export default {
  testEnvironment: 'jsdom',
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
    'src/**/*.{js,jsx}',
    'backend/**/*.js',
    '!**/node_modules/**',
    '!**/dist/**',
    '!**/coverage/**'
  ],
  coverageThreshold: {
    global: {
      branches: 70,
      functions: 70,
      lines: 70,
      statements: 70
    }
  },
  setupFilesAfterEnv: ['<rootDir>/tests/setup.js'],
  testTimeout: 10000
};
