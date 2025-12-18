/**
 * Tests for TradingModel class
 * Specifically testing the getModelStats() method with edge cases
 */

import TradingModel from '../src/models/TradingModel.js';

/**
 * Simple test runner
 */
function assert(condition, message) {
    if (!condition) {
        throw new Error(`Assertion failed: ${message}`);
    }
    console.log(`✓ ${message}`);
}

function assertEqual(actual, expected, message) {
    if (actual !== expected) {
        throw new Error(`Assertion failed: ${message}\n  Expected: ${expected}\n  Actual: ${actual}`);
    }
    console.log(`✓ ${message}`);
}

/**
 * Test 1: getModelStats() with empty training data (division by zero case)
 */
function testEmptyTrainingData() {
    console.log('\nTest 1: getModelStats() with empty training data');
    const model = new TradingModel(0.5);
    const stats = model.getModelStats();
    
    assertEqual(stats.trainingSize, 0, 'Training size should be 0');
    assertEqual(stats.successRate, '0.00%', 'Success rate should be 0.00% when no training data');
    assertEqual(stats.threshold, 0.5, 'Threshold should be 0.5');
    
    console.log('Stats:', stats);
}

/**
 * Test 2: getModelStats() with training data
 */
function testWithTrainingData() {
    console.log('\nTest 2: getModelStats() with training data');
    const model = new TradingModel(0.7);
    
    // Add some training data
    model.addTrainingData({ success: true });
    model.addTrainingData({ success: true });
    model.addTrainingData({ success: false });
    model.addTrainingData({ success: true });
    
    const stats = model.getModelStats();
    
    assertEqual(stats.trainingSize, 4, 'Training size should be 4');
    assertEqual(stats.successRate, '75.00%', 'Success rate should be 75.00% (3/4)');
    assertEqual(stats.threshold, 0.7, 'Threshold should be 0.7');
    
    console.log('Stats:', stats);
}

/**
 * Test 3: getModelStats() with all failures
 */
function testAllFailures() {
    console.log('\nTest 3: getModelStats() with all failures');
    const model = new TradingModel(0.6);
    
    model.addTrainingData({ success: false });
    model.addTrainingData({ success: false });
    model.addTrainingData({ success: false });
    
    const stats = model.getModelStats();
    
    assertEqual(stats.trainingSize, 3, 'Training size should be 3');
    assertEqual(stats.successRate, '0.00%', 'Success rate should be 0.00%');
    assertEqual(stats.threshold, 0.6, 'Threshold should be 0.6');
    
    console.log('Stats:', stats);
}

/**
 * Test 4: getModelStats() with all successes
 */
function testAllSuccesses() {
    console.log('\nTest 4: getModelStats() with all successes');
    const model = new TradingModel();
    
    model.addTrainingData({ success: true });
    model.addTrainingData({ success: true });
    
    const stats = model.getModelStats();
    
    assertEqual(stats.trainingSize, 2, 'Training size should be 2');
    assertEqual(stats.successRate, '100.00%', 'Success rate should be 100.00%');
    
    console.log('Stats:', stats);
}

/**
 * Test 5: getModelStats() after clearing data
 */
function testClearTrainingData() {
    console.log('\nTest 5: getModelStats() after clearing data');
    const model = new TradingModel();
    
    model.addTrainingData({ success: true });
    model.addTrainingData({ success: true });
    
    let stats = model.getModelStats();
    assertEqual(stats.trainingSize, 2, 'Training size should be 2 before clear');
    
    model.clearTrainingData();
    stats = model.getModelStats();
    
    assertEqual(stats.trainingSize, 0, 'Training size should be 0 after clear');
    assertEqual(stats.successRate, '0.00%', 'Success rate should be 0.00% after clear');
    
    console.log('Stats after clear:', stats);
}

/**
 * Run all tests
 */
async function runTests() {
    console.log('=== Running TradingModel Tests ===');
    
    try {
        testEmptyTrainingData();
        testWithTrainingData();
        testAllFailures();
        testAllSuccesses();
        testClearTrainingData();
        
        console.log('\n=== All tests passed! ✓ ===');
        process.exit(0);
    } catch (error) {
        console.error('\n❌ Test failed:', error.message);
        process.exit(1);
    }
}

// Run tests
runTests();
