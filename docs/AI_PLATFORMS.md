# AI Platforms Integration Guide

## Overview

The-basics system integrates with multiple AI and crowdsourcing platforms to enable automated task distribution, data annotation, and AI-powered services.

## Supported Platforms

### 1. Amazon Mechanical Turk (MTurk)
### 2. Appen
### 3. RapidAPI
### 4. HuggingFace
### 5. OpenAI

## Platform Details

---

## 1. Amazon Mechanical Turk (MTurk)

### Description
Amazon Mechanical Turk is a crowdsourcing marketplace that enables distributed human intelligence tasks (HITs).

### Use Cases
- Data labeling and annotation
- Content moderation
- Survey responses
- Image/video categorization
- Sentiment analysis

### Setup

#### Prerequisites
- AWS Account
- MTurk Requester account
- Sufficient MTurk balance

#### Configuration

1. **Get MTurk Credentials**
   ```bash
   # Sign in to AWS Console
   # Go to IAM > Users > Create Access Key
   # Save the credentials
   ```

2. **Add to .env**
   ```bash
   MTURK_ACCESS_KEY=your_access_key_here
   MTURK_SECRET_KEY=your_secret_key_here
   MTURK_SANDBOX=true  # Use sandbox for testing
   ```

3. **Enable in features.yaml**
   ```yaml
   features:
     ai_platforms:
       mturk:
         enabled: true
         sandbox_mode: true
         auto_approve_delay: 2592000  # 30 days
         max_assignments: 10
   ```

### API Usage

```javascript
const MTurkProvider = require('./paid-ai-bot/providers/mturk');

const mturk = new MTurkProvider({
  accessKeyId: process.env.MTURK_ACCESS_KEY,
  secretAccessKey: process.env.MTURK_SECRET_KEY,
  region: 'us-east-1',
  sandbox: process.env.MTURK_SANDBOX === 'true'
});

// Create a HIT
const hit = await mturk.createHIT({
  title: 'Classify Images',
  description: 'Categorize images into predefined categories',
  reward: '0.05',
  maxAssignments: 10,
  lifetime: 3600,
  assignmentDuration: 600,
  question: questionXML
});

// Get HIT results
const results = await mturk.getHITResults(hit.HITId);

// Approve assignments
await mturk.approveAssignment(assignmentId);
```

### Cost Estimation
- Base fee: 20% of reward + $0.01 per assignment
- Example: 100 assignments at $0.05 each = $5 + $1 fee + $1 Amazon fee = $7 total

### Best Practices
- Start with sandbox mode for testing
- Use qualification requirements to ensure worker quality
- Set appropriate timeouts and auto-approval delays
- Monitor worker feedback
- Use bonus payments for exceptional work

---

## 2. Appen

### Description
Appen provides high-quality training data for machine learning through a global crowd of over 1 million contributors.

### Use Cases
- Speech and audio transcription
- Image annotation
- Natural language processing
- Search relevance evaluation
- Sentiment analysis

### Setup

#### Prerequisites
- Appen account
- API access enabled
- Project ID

#### Configuration

1. **Get Appen Credentials**
   - Sign up at https://appen.com/
   - Contact support to enable API access
   - Get API key and project ID

2. **Add to .env**
   ```bash
   APPEN_API_KEY=your_api_key_here
   APPEN_PROJECT_ID=your_project_id
   ```

3. **Enable in features.yaml**
   ```yaml
   features:
     ai_platforms:
       appen:
         enabled: true
         auto_submit: false
         quality_threshold: 0.95
   ```

### API Usage

```javascript
const AppenProvider = require('./paid-ai-bot/providers/appen');

const appen = new AppenProvider({
  apiKey: process.env.APPEN_API_KEY,
  projectId: process.env.APPEN_PROJECT_ID
});

// Submit job
const job = await appen.submitJob({
  type: 'image_annotation',
  data: imageUrls,
  instructions: 'Label all visible objects',
  qualityLevel: 'high'
});

// Check job status
const status = await appen.getJobStatus(job.id);

// Get results
const results = await appen.getJobResults(job.id);
```

### Cost Estimation
- Custom pricing based on project complexity
- Typical range: $0.10 - $5.00 per unit
- Higher quality = higher cost
- Volume discounts available

### Best Practices
- Provide clear, detailed instructions
- Use pilot projects to test quality
- Implement quality checkpoints
- Provide feedback to contributors
- Use Appen's quality metrics

---

## 3. RapidAPI

### Description
RapidAPI is a marketplace for APIs, providing access to thousands of AI and machine learning APIs.

### Use Cases
- Text analysis and NLP
- Image recognition
- Language translation
- Data extraction
- Sentiment analysis

### Setup

#### Prerequisites
- RapidAPI account
- Subscription to desired APIs

#### Configuration

1. **Get RapidAPI Credentials**
   - Sign up at https://rapidapi.com/
   - Subscribe to APIs
   - Get API key from dashboard

2. **Add to .env**
   ```bash
   RAPIDAPI_KEY=your_api_key_here
   RAPIDAPI_HOST=api_host_name
   ```

3. **Enable in features.yaml**
   ```yaml
   features:
     ai_platforms:
       rapidapi:
         enabled: true
         rate_limit: 100
         timeout: 30000
   ```

### API Usage

```javascript
const RapidAPIProvider = require('./paid-ai-bot/providers/rapidapi');

const rapidapi = new RapidAPIProvider({
  apiKey: process.env.RAPIDAPI_KEY
});

// Call an API
const result = await rapidapi.call({
  host: 'text-analysis.p.rapidapi.com',
  endpoint: '/sentiment',
  method: 'POST',
  data: {
    text: 'This is amazing!'
  }
});
```

### Cost Estimation
- Varies by API
- Many have free tiers (100-1000 requests/month)
- Paid tiers: $0.001 - $0.10 per request
- Monthly subscriptions available

### Best Practices
- Monitor API usage and quotas
- Implement caching for repeated requests
- Use batch processing when available
- Handle rate limits gracefully
- Test with free tier first

---

## 4. HuggingFace

### Description
HuggingFace provides access to state-of-the-art machine learning models for NLP, computer vision, and more.

### Use Cases
- Text generation
- Question answering
- Translation
- Summarization
- Image classification
- Object detection

### Setup

#### Prerequisites
- HuggingFace account
- API token

#### Configuration

1. **Get HuggingFace Token**
   - Sign up at https://huggingface.co/
   - Go to Settings > Access Tokens
   - Create a new token

2. **Add to .env**
   ```bash
   HUGGINGFACE_API_KEY=hf_your_token_here
   ```

3. **Enable in features.yaml**
   ```yaml
   features:
     ai_platforms:
       huggingface:
         enabled: true
         model_cache: true
         max_concurrent: 3
   ```

### API Usage

```javascript
const HuggingFaceProvider = require('./paid-ai-bot/huggingface');

const hf = new HuggingFaceProvider({
  apiKey: process.env.HUGGINGFACE_API_KEY
});

// Text generation
const generated = await hf.generateText({
  model: 'gpt2',
  prompt: 'Once upon a time',
  maxLength: 100
});

// Sentiment analysis
const sentiment = await hf.analyzeSentiment({
  text: 'I love this product!',
  model: 'distilbert-base-uncased-finetuned-sst-2-english'
});

// Image classification
const classification = await hf.classifyImage({
  imageUrl: 'https://example.com/image.jpg',
  model: 'google/vit-base-patch16-224'
});
```

### Cost Estimation
- Free tier: Limited requests per month
- Paid inference: $0.06 - $9.00 per 1M characters (varies by model)
- Dedicated endpoints: $0.60 - $4.50 per hour

### Best Practices
- Use appropriate model sizes for your task
- Implement result caching
- Use batch inference when possible
- Monitor API usage
- Consider hosting models locally for high volume

---

## 5. OpenAI

### Description
OpenAI provides access to GPT models for advanced natural language processing and generation.

### Use Cases
- Text generation
- Code generation
- Question answering
- Summarization
- Creative writing
- Conversational AI

### Setup

#### Prerequisites
- OpenAI account
- API key
- Sufficient credits

#### Configuration

1. **Get OpenAI API Key**
   - Sign up at https://platform.openai.com/
   - Go to API keys
   - Create new key

2. **Add to .env**
   ```bash
   OPENAI_API_KEY=sk-your_key_here
   ```

3. **Enable in features.yaml**
   ```yaml
   features:
     ai_platforms:
       openai:
         enabled: false  # Disabled by default due to cost
         model: gpt-3.5-turbo
         max_tokens: 2000
   ```

### API Usage

```javascript
const { Configuration, OpenAIApi } = require('openai');

const configuration = new Configuration({
  apiKey: process.env.OPENAI_API_KEY
});
const openai = new OpenAIApi(configuration);

// Chat completion
const response = await openai.createChatCompletion({
  model: 'gpt-3.5-turbo',
  messages: [
    { role: 'system', content: 'You are a helpful assistant.' },
    { role: 'user', content: 'Explain quantum computing' }
  ],
  max_tokens: 500
});

// Code generation
const code = await openai.createChatCompletion({
  model: 'gpt-4',
  messages: [
    { role: 'user', content: 'Write a Python function to calculate fibonacci numbers' }
  ]
});
```

### Cost Estimation (GPT-3.5-turbo)
- Input: $0.0015 per 1K tokens
- Output: $0.002 per 1K tokens
- Example: 100K tokens = ~$0.175

### Cost Estimation (GPT-4)
- Input: $0.03 per 1K tokens
- Output: $0.06 per 1K tokens
- Example: 100K tokens = ~$4.50

### Best Practices
- Use GPT-3.5-turbo for most tasks (cheaper)
- Implement prompt caching
- Set appropriate max_tokens limits
- Use streaming for long responses
- Monitor token usage
- Implement fallbacks for rate limits

---

## Integration with Freelance Engine

The AI platforms integrate with the freelance engine orchestrator:

```python
# freelance_engine/orchestrator.py

from platform_connectors import MTurkConnector, AppenConnector, HuggingFaceConnector

class AIOrchestrator:
    def __init__(self):
        self.mturk = MTurkConnector()
        self.appen = AppenConnector()
        self.huggingface = HuggingFaceConnector()
    
    def process_job(self, job_type, data):
        if job_type == 'annotation':
            return self.mturk.create_annotation_task(data)
        elif job_type == 'transcription':
            return self.appen.create_transcription_job(data)
        elif job_type == 'sentiment':
            return self.huggingface.analyze_sentiment(data)
```

## Monitoring and Metrics

Track platform usage:

```javascript
const { FeatureManager } = require('./src/core/feature-manager');
const fm = FeatureManager.getInstance();

// Check if platform is enabled
if (fm.isEnabled('ai_platforms.mturk')) {
  // Use MTurk
}

// Get platform configuration
const config = fm.getConfig('ai_platforms.huggingface');
```

## Error Handling

Use the error handler for platform failures:

```javascript
const { ErrorHandler } = require('./src/core/error-handler');
const errorHandler = ErrorHandler.getInstance();

try {
  const result = await mturk.createHIT(hitData);
} catch (error) {
  errorHandler.reportError('mturk', error, 'error');
  // Fallback to alternative platform
}
```

## Security Considerations

1. **API Keys**: Never commit API keys to version control
2. **Rate Limiting**: Implement rate limiting to avoid excessive costs
3. **Input Validation**: Validate all data before sending to platforms
4. **Encryption**: Use credential manager for encrypted storage
5. **Monitoring**: Monitor API usage and costs regularly

## Cost Management

Set up budget alerts:

```javascript
// In your .env
MAX_MTURK_MONTHLY_COST=100
MAX_OPENAI_MONTHLY_COST=50

// Monitor costs
const credentialManager = require('./src/security/credential-manager');
const cm = credentialManager.getInstance();

// Check budget before API calls
if (monthlySpend >= MAX_COST) {
  errorHandler.degradeGracefully(['ai_platforms.openai']);
}
```

## Support and Resources

- **MTurk**: https://docs.aws.amazon.com/mturk/
- **Appen**: https://appen.com/resources/
- **RapidAPI**: https://docs.rapidapi.com/
- **HuggingFace**: https://huggingface.co/docs
- **OpenAI**: https://platform.openai.com/docs

## Troubleshooting

### Common Issues

1. **Authentication Failures**
   - Verify API keys are correct
   - Check API key permissions
   - Ensure keys are not expired

2. **Rate Limit Errors**
   - Implement exponential backoff
   - Use the recovery system's retry logic
   - Consider upgrading plan

3. **High Costs**
   - Monitor usage with cost tracking
   - Implement caching
   - Use cheaper alternatives when possible
   - Set up budget alerts

4. **Quality Issues**
   - Provide clearer instructions
   - Use qualification requirements
   - Implement quality checks
   - Review and iterate on prompts
