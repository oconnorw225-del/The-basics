# Quick Start Guide: Paid AI Bot

This guide will help you get the Paid AI Bot up and running quickly.

## Overview

The Paid AI Bot is a premium AI-powered system that:
- ✅ Processes AI tasks using HuggingFace models
- ✅ Manages subscriptions via Stripe
- ✅ Sources tasks from 5 different providers
- ✅ Supports multiple AI operations (text generation, classification, Q&A, etc.)

## Prerequisites

- Node.js 16+ installed
- Stripe account (for payment processing)
- HuggingFace account (for AI processing)
- Optional: API keys for task providers (MTurk, Appen, RapidAPI)

## Quick Setup (5 minutes)

### 1. Install Dependencies

```bash
# Install root dependencies
npm install

# Install paid-ai-bot dependencies
cd paid-ai-bot
npm install
cd ..
```

### 2. Configure Environment Variables

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` and add your credentials:

```bash
# Required - Get from Stripe Dashboard
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Required - Get from HuggingFace
HUGGINGFACE_API_KEY=hf_...

# Optional - Configure model
HUGGINGFACE_MODEL=gpt2

# Optional - Enable providers
# MTURK_ACCESS_KEY=...
# APPEN_API_KEY=...
# RAPIDAPI_KEY=...
```

**Get your API keys:**
- Stripe: https://dashboard.stripe.com/apikeys
- HuggingFace: https://huggingface.co/settings/tokens

### 3. Start the Bot

```bash
npm run start
# or directly:
node paid-ai-bot/bot.js
```

The bot will start on `http://localhost:9000`

## Test the Bot

### 1. Check Health

```bash
curl http://localhost:9000/health
```

Expected response:
```json
{
  "status": "healthy",
  "uptime": 5.123,
  "providers": {
    "customQueue": true,
    "directClients": false,
    "mturk": false,
    "appen": false,
    "rapidapi": false
  }
}
```

### 2. Submit a Test Task

```bash
curl -X POST http://localhost:9000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "task": {
      "type": "text_generation",
      "input": "Write a short story about AI"
    },
    "priority": "normal"
  }'
```

Expected response:
```json
{
  "success": true,
  "result": {
    "taskId": "custom_1",
    "status": "queued"
  }
}
```

### 3. Check Task Status

```bash
curl http://localhost:9000/api/tasks/custom_1
```

## Stripe Integration

### 1. Configure Webhook

In your Stripe Dashboard:
1. Go to Developers > Webhooks
2. Click "Add endpoint"
3. URL: `https://your-domain.com/webhook/stripe`
4. Select events:
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.payment_succeeded`
   - `invoice.payment_failed`
5. Copy the webhook secret to `.env`

### 2. Test Webhook Locally

Use Stripe CLI:

```bash
# Install Stripe CLI
# https://stripe.com/docs/stripe-cli

# Forward webhooks to local server
stripe listen --forward-to localhost:9000/webhook/stripe

# In another terminal, trigger test event
stripe trigger customer.subscription.created
```

## Available AI Tasks

### Text Generation

```bash
curl -X POST http://localhost:9000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "task": {
      "type": "text_generation",
      "input": "Once upon a time",
      "parameters": {
        "max_length": 100,
        "temperature": 0.7
      }
    }
  }'
```

### Text Classification

```bash
curl -X POST http://localhost:9000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "task": {
      "type": "text_classification",
      "input": "This product is amazing!"
    }
  }'
```

### Question Answering

```bash
curl -X POST http://localhost:9000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "task": {
      "type": "question_answering",
      "input": {
        "question": "What is AI?",
        "context": "Artificial Intelligence (AI) is the simulation of human intelligence by machines."
      }
    }
  }'
```

### Summarization

```bash
curl -X POST http://localhost:9000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "task": {
      "type": "summarization",
      "input": "Long text to summarize...",
      "parameters": {
        "max_length": 130,
        "min_length": 30
      }
    }
  }'
```

## Pricing Plans

### Basic - $9.99/month
- 1,000 tasks/month
- Normal priority
- All AI features

### Pro - $29.99/month
- 5,000 tasks/month
- High priority
- All AI features

### Enterprise - $99.99/month
- Unlimited tasks
- Urgent priority
- All AI features

## Enable Additional Providers

### Amazon MTurk

1. Sign up at https://requester.mturk.com/
2. Get API credentials
3. Add to `.env`:
```bash
MTURK_ACCESS_KEY=your_key
MTURK_SECRET_KEY=your_secret
```

### Appen

1. Contact Appen for API access
2. Add to `.env`:
```bash
APPEN_API_KEY=your_key
```

### RapidAPI

1. Sign up at https://rapidapi.com/
2. Subscribe to AI APIs
3. Add to `.env`:
```bash
RAPIDAPI_KEY=your_key
```

## Production Deployment

### Railway

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and initialize
railway login
railway init

# Add environment variables
railway variables set STRIPE_SECRET_KEY=sk_live_...
railway variables set HUGGINGFACE_API_KEY=hf_...
railway variables set STRIPE_WEBHOOK_SECRET=whsec_...

# Deploy
railway up
```

### Heroku

```bash
# Create app
heroku create your-ai-bot

# Add environment variables
heroku config:set STRIPE_SECRET_KEY=sk_live_...
heroku config:set HUGGINGFACE_API_KEY=hf_...

# Deploy
git push heroku main
```

### AWS

Use the included GitHub Actions workflows:
1. Configure AWS credentials in GitHub secrets
2. Run "Complete AWS Setup" workflow
3. Bot will be deployed to AWS ECS

## Monitoring

### View Logs

```bash
# Railway
railway logs

# Heroku
heroku logs --tail

# Local
# Logs are output to console
```

### Check Provider Statistics

```bash
curl http://localhost:9000/api/providers
```

## Troubleshooting

### Bot won't start

**Issue**: Missing environment variables

**Solution**: Verify `.env` has required keys:
```bash
STRIPE_SECRET_KEY
HUGGINGFACE_API_KEY
```

### HuggingFace tasks fail

**Issue**: Invalid API key or model loading

**Solution**: 
1. Verify API key is correct
2. Wait a few seconds for model to load
3. Check HuggingFace status page

### Stripe webhooks not working

**Issue**: Webhook secret mismatch

**Solution**:
1. Verify `STRIPE_WEBHOOK_SECRET` matches Stripe Dashboard
2. Use Stripe CLI for local testing
3. Check webhook endpoint is publicly accessible

### Tasks stuck in queue

**Issue**: No providers enabled

**Solution**:
1. Custom queue is always enabled
2. Check provider stats: `curl http://localhost:9000/api/providers`
3. Enable additional providers via environment variables

## Next Steps

- Read [paid-ai-bot/README.md](paid-ai-bot/README.md) for detailed documentation
- Review [Stripe documentation](https://stripe.com/docs)
- Explore [HuggingFace models](https://huggingface.co/models)
- Configure additional providers for more task sources

## Support

For issues or questions:
1. Check troubleshooting section above
2. Review main repository documentation
3. Check GitHub issues

---

**Security Reminder**: Never commit API keys or secrets to version control. Always use environment variables.
