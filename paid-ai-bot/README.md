# Paid AI Bot

Premium AI-powered bot with Stripe payment integration and multi-provider AI task sourcing.

## Features

- **💳 Stripe Payment Integration**: Subscription-based payment processing with webhook support
- **🤖 HuggingFace AI**: Text generation, classification, Q&A, summarization, and translation
- **🔄 Multi-Provider Task Sourcing**: 5 different task providers
  - Custom Queue (internal task management)
  - Direct Clients (direct client relationships)
  - Amazon MTurk (human intelligence tasks)
  - Appen (crowd-sourced data annotation)
  - RapidAPI (AI/ML marketplace APIs)

## Quick Start

### 1. Install Dependencies

```bash
cd paid-ai-bot
npm install
```

### 2. Configure Environment Variables

Create a `.env` file in the project root with:

```bash
# Required
BOT_PORT=9000
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
HUGGINGFACE_API_KEY=hf_...

# Optional - Providers (enable as needed)
HUGGINGFACE_MODEL=gpt2
DIRECT_CLIENT_API_KEY=...
MTURK_ACCESS_KEY=...
MTURK_SECRET_KEY=...
APPEN_API_KEY=...
RAPIDAPI_KEY=...

# Polling configuration
POLL_INTERVAL=30000
```

### 3. Start the Bot

```bash
npm start
```

The bot will be available at `http://localhost:9000`

## API Endpoints

### Health Check
```
GET /health
```
Returns bot status and enabled providers.

### Submit Task
```
POST /api/tasks
Content-Type: application/json

{
  "task": {
    "type": "text_generation",
    "input": "Write a story about AI"
  },
  "provider": "custom",  // optional: custom, direct, mturk, appen, rapidapi
  "priority": "normal"   // optional: normal, high, urgent
}
```

### Get Task Status
```
GET /api/tasks/:taskId
```

### Provider Status
```
GET /api/providers
```

### Stripe Webhook
```
POST /webhook/stripe
```
Handles Stripe subscription events.

## Pricing Plans

### Basic Plan - $9.99/month
- 1,000 tasks per month
- Normal priority processing
- All AI features included

### Pro Plan - $29.99/month
- 5,000 tasks per month
- High priority processing
- All AI features included

### Enterprise Plan - $99.99/month
- Unlimited tasks
- Urgent priority processing
- All AI features included
- Dedicated support

## Architecture

```
paid-ai-bot/
├── bot.js              # Main server with multi-provider polling
├── payments.js         # Stripe integration & subscription management
├── huggingface.js      # HuggingFace AI task processing
├── providers/
│   ├── customQueue.js  # Internal task queue
│   ├── directClients.js # Direct client integration
│   ├── mturk.js        # Amazon MTurk integration
│   ├── appen.js        # Appen integration
│   └── rapidapi.js     # RapidAPI integration
├── package.json
└── README.md
```

## Task Processing Flow

1. **Task Submission**: Client submits task via API or provider polls for new tasks
2. **Queue Management**: Tasks queued based on priority (urgent > high > normal)
3. **AI Processing**: Tasks processed using HuggingFace models
4. **Result Distribution**: Results sent back to originating provider
5. **Usage Tracking**: Task usage tracked against subscription limits

## Provider Configuration

Each provider can be enabled/disabled by setting appropriate environment variables:

- **Custom Queue**: Always enabled (internal)
- **Direct Clients**: Set `DIRECT_CLIENT_API_KEY`
- **MTurk**: Set `MTURK_ACCESS_KEY` and `MTURK_SECRET_KEY`
- **Appen**: Set `APPEN_API_KEY`
- **RapidAPI**: Set `RAPIDAPI_KEY`

## HuggingFace Models

Supported task types:
- `text_generation`: Generate text from prompts
- `text_classification`: Classify text (sentiment, topics, etc.)
- `question_answering`: Answer questions based on context
- `summarization`: Summarize long text
- `translation`: Translate between languages

## Stripe Webhook Events

The bot handles these Stripe events:
- `customer.subscription.created`: New subscription
- `customer.subscription.updated`: Subscription changes
- `customer.subscription.deleted`: Cancellation
- `invoice.payment_succeeded`: Successful payment
- `invoice.payment_failed`: Failed payment

## Development

### Run in Development Mode
```bash
npm run dev
```

### Run Tests
```bash
npm test
```

## Production Deployment

1. Set all required environment variables
2. Configure Stripe webhook endpoint in Stripe Dashboard
3. Use a process manager (PM2, systemd, etc.)
4. Set up monitoring and logging
5. Configure database for persistent storage (replace in-memory maps)

## Security Notes

- Never commit API keys or secrets
- Use environment variables for all sensitive data
- Validate Stripe webhook signatures
- Implement rate limiting in production
- Use HTTPS for all endpoints
- Implement proper authentication/authorization

## Support

For questions or issues, please refer to the main repository documentation.
