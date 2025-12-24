/**
 * TradingModel - Machine Learning Model for Trading Predictions
 * Handles training data and provides statistics about model performance
 */

class TradingModel {
  constructor(threshold = 0.5) {
    this.trainingData = []
    this.threshold = threshold
  }

  /**
   * Add training data to the model
   * @param {Object} data - Training data point with success indicator
   */
  addTrainingData(data) {
    this.trainingData.push(data)
  }

  /**
   * Get statistics about the model's training data
   * Handles edge case where trainingData.length is 0 to prevent division by zero
   * @returns {Object} Statistics object with trainingSize, successRate, and threshold
   */
  getModelStats() {
    const totalData = this.trainingData.length
    return {
      trainingSize: totalData,
      successRate:
        totalData === 0
          ? '0.00%'
          : ((this.trainingData.filter(j => j.success).length / totalData) * 100).toFixed(2) + '%',
      threshold: this.threshold,
    }
  }

  /**
   * Clear all training data
   */
  clearTrainingData() {
    this.trainingData = []
  }

  /**
   * Set the model threshold
   * @param {number} threshold - New threshold value
   */
  setThreshold(threshold) {
    this.threshold = threshold
  }
}

export default TradingModel
