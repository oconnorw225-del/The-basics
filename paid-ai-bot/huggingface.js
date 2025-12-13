/**
 * HuggingFace AI Task Processing
 * Integrates with HuggingFace Inference API for AI-powered task completion
 */

const fetch = require('node-fetch');

const API_URL = 'https://api-inference.huggingface.co/models/';
const API_KEY = process.env.HUGGINGFACE_API_KEY;
const DEFAULT_MODEL = process.env.HUGGINGFACE_MODEL || 'gpt2';

// Model configurations
const MODELS = {
  text_generation: {
    name: 'gpt2',
    url: `${API_URL}gpt2`
  },
  text_classification: {
    name: 'distilbert-base-uncased-finetuned-sst-2-english',
    url: `${API_URL}distilbert-base-uncased-finetuned-sst-2-english`
  },
  question_answering: {
    name: 'distilbert-base-cased-distilled-squad',
    url: `${API_URL}distilbert-base-cased-distilled-squad`
  },
  summarization: {
    name: 'facebook/bart-large-cnn',
    url: `${API_URL}facebook/bart-large-cnn`
  },
  translation: {
    name: 't5-base',
    url: `${API_URL}t5-base`
  }
};

/**
 * Make request to HuggingFace API
 */
async function queryHuggingFace(modelUrl, payload, retries = 3) {
  if (!API_KEY) {
    throw new Error('HUGGINGFACE_API_KEY not configured');
  }

  for (let i = 0; i < retries; i++) {
    try {
      const response = await fetch(modelUrl, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${API_KEY}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        const error = await response.text();
        
        // Model might be loading, wait and retry
        if (response.status === 503) {
          console.log(`Model loading, waiting... (attempt ${i + 1}/${retries})`);
          await new Promise(resolve => setTimeout(resolve, 5000));
          continue;
        }

        throw new Error(`HuggingFace API error: ${response.status} - ${error}`);
      }

      return await response.json();
    } catch (error) {
      if (i === retries - 1) {
        throw error;
      }
      console.error(`Request failed (attempt ${i + 1}/${retries}):`, error.message);
      await new Promise(resolve => setTimeout(resolve, 2000));
    }
  }

  throw new Error('Max retries exceeded');
}

/**
 * Process a task using AI
 */
async function processTask(task) {
  const { type, input, parameters = {} } = task;

  console.log(`Processing ${type} task with HuggingFace...`);

  try {
    let result;

    switch (type) {
      case 'text_generation':
        result = await generateText(input, parameters);
        break;
      
      case 'text_classification':
        result = await classifyText(input, parameters);
        break;
      
      case 'question_answering':
        result = await answerQuestion(input, parameters);
        break;
      
      case 'summarization':
        result = await summarizeText(input, parameters);
        break;
      
      case 'translation':
        result = await translateText(input, parameters);
        break;
      
      default:
        // Default to text generation
        result = await generateText(input, parameters);
    }

    return {
      success: true,
      result,
      timestamp: new Date().toISOString()
    };
  } catch (error) {
    console.error('Task processing error:', error);
    return {
      success: false,
      error: error.message,
      timestamp: new Date().toISOString()
    };
  }
}

/**
 * Generate text using language model
 */
async function generateText(prompt, parameters = {}) {
  const model = MODELS.text_generation;
  const payload = {
    inputs: prompt,
    parameters: {
      max_length: parameters.max_length || 100,
      temperature: parameters.temperature || 0.7,
      top_p: parameters.top_p || 0.9,
      do_sample: parameters.do_sample !== false,
      ...parameters
    }
  };

  const response = await queryHuggingFace(model.url, payload);
  return response[0]?.generated_text || response;
}

/**
 * Classify text (sentiment, topic, etc.)
 */
async function classifyText(text, parameters = {}) {
  const model = MODELS.text_classification;
  const payload = {
    inputs: text,
    parameters
  };

  const response = await queryHuggingFace(model.url, payload);
  return response;
}

/**
 * Answer questions based on context
 */
async function answerQuestion(input, parameters = {}) {
  const { question, context } = input;
  
  if (!question || !context) {
    throw new Error('Both question and context are required');
  }

  const model = MODELS.question_answering;
  const payload = {
    inputs: {
      question,
      context
    },
    parameters
  };

  const response = await queryHuggingFace(model.url, payload);
  return response;
}

/**
 * Summarize text
 */
async function summarizeText(text, parameters = {}) {
  const model = MODELS.summarization;
  const payload = {
    inputs: text,
    parameters: {
      max_length: parameters.max_length || 130,
      min_length: parameters.min_length || 30,
      ...parameters
    }
  };

  const response = await queryHuggingFace(model.url, payload);
  return response[0]?.summary_text || response;
}

/**
 * Translate text
 */
async function translateText(input, parameters = {}) {
  const { text, source_lang, target_lang } = input;
  
  const model = MODELS.translation;
  const prompt = `translate ${source_lang || 'English'} to ${target_lang || 'French'}: ${text}`;
  
  const payload = {
    inputs: prompt,
    parameters: {
      max_length: parameters.max_length || 200,
      ...parameters
    }
  };

  const response = await queryHuggingFace(model.url, payload);
  return response[0]?.translation_text || response;
}

/**
 * Test HuggingFace connection
 */
async function testConnection() {
  try {
    const result = await generateText('Hello, this is a test.', { max_length: 20 });
    console.log('✓ HuggingFace connection successful');
    return true;
  } catch (error) {
    console.error('✗ HuggingFace connection failed:', error.message);
    return false;
  }
}

/**
 * Get available models
 */
function getAvailableModels() {
  return Object.keys(MODELS).map(type => ({
    type,
    name: MODELS[type].name,
    url: MODELS[type].url
  }));
}

module.exports = {
  processTask,
  generateText,
  classifyText,
  answerQuestion,
  summarizeText,
  translateText,
  testConnection,
  getAvailableModels
};
