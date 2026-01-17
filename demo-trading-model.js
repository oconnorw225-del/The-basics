/**
 * Demo: TradingModel getModelStats() method
 * Shows how the division by zero fix works
 */

import TradingModel from './src/models/TradingModel.js';

console.log('=== TradingModel getModelStats() Demo ===\n');

// Example 1: Empty model (division by zero case - FIXED!)
console.log('Example 1: Empty training data (division by zero prevented)');
const emptyModel = new TradingModel(0.6);
console.log('Stats:', emptyModel.getModelStats());
console.log('✓ No division by zero error!\n');

// Example 2: Model with training data
console.log('Example 2: Model with training data');
const trainedModel = new TradingModel(0.7);

// Simulate some trading results
trainedModel.addTrainingData({ success: true, trade: 'BTC/USD' });
trainedModel.addTrainingData({ success: true, trade: 'ETH/USD' });
trainedModel.addTrainingData({ success: false, trade: 'LTC/USD' });
trainedModel.addTrainingData({ success: true, trade: 'XRP/USD' });
trainedModel.addTrainingData({ success: false, trade: 'ADA/USD' });

console.log('Stats:', trainedModel.getModelStats());
console.log('Success rate: 3 out of 5 trades = 60%\n');

// Example 3: After clearing data
console.log('Example 3: After clearing all training data');
trainedModel.clearTrainingData();
console.log('Stats:', trainedModel.getModelStats());
console.log('✓ Back to 0.00% without errors!\n');

console.log('=== Demo Complete ===');
