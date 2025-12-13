# The-basics

Unified autonomous trading and AI system consolidating best components from multiple repositories.

## 🚀 Quick Start

### AWS Deployment
```bash
# Configure AWS credentials in GitHub Secrets, then:
# Go to Actions > AWS Complete Setup & Deployment > Run workflow
```
See [AWS Quick Start](aws/QUICKSTART.md) for details.

### AI Bot Setup
```bash
npm install
cp .env.example .env
# Configure API keys in .env
node paid-ai-bot/bot.js
```
See [AI Bot Quick Start](QUICKSTART_AI_BOT.md) for details.

### Local Development
```bash
npm install
npm run dev        # Start frontend
npm run unified    # Start autonomous system
```

## 🎯 Core Features

### ✅ Complete AWS Infrastructure
- **Full Terraform IaC**: VPC, ECS, RDS, S3, CloudWatch, Auto Scaling
- **4 Automated Workflows**: 
  - One-click complete AWS setup
  - Continuous deployment pipeline
  - 15-minute health monitoring
  - Infrastructure provisioning
- **Cost Management**: Automated monitoring and optimization
- **Security**: VPC isolation, security groups, IAM roles

### ✅ Paid AI Bot System
- **💳 Stripe Integration**: Subscription-based payment processing
- **🤖 HuggingFace AI**: Text generation, classification, Q&A, summarization, translation
- **🔄 Multi-Provider Task Sourcing**:
  - Custom Queue (internal)
  - Direct Clients
  - Amazon MTurk (human intelligence)
  - Appen (crowd-sourced data)
  - RapidAPI (AI marketplace)
- **📊 Usage Tracking**: Task limits, billing periods, analytics

### ✅ Autonomous Trading System
- **Unified System**: Complete orchestrator with quantum engine integration
- **Chimera Core**: AI-powered decision engine
- **Freelance Automation**: Automated task sourcing and bidding
- **Multi-threaded Execution**: Real-time monitoring and logging

### ✅ Full Stack Application
- **Backend**: FastAPI with async support
- **Frontend**: React with Vite
- **Database**: PostgreSQL support
- **Authentication**: JWT-based security
- **Monitoring**: Comprehensive logging and health checks

## 📁 Repository Structure

```
The-basics/
├── .github/workflows/       # CI/CD pipelines
│   ├── aws-complete-setup.yml      # One-click AWS deployment
│   ├── deploy-to-aws.yml           # Main deployment workflow
│   ├── monitor-aws.yml             # AWS health monitoring
│   ├── setup-aws-infrastructure.yml # Terraform provisioning
│   ├── consolidate.yml             # Repo consolidation
│   └── unified-system.yml          # System tests
│
├── aws/                     # AWS infrastructure
│   ├── terraform/           # Infrastructure as Code
│   │   ├── main.tf         # Main Terraform config
│   │   ├── variables.tf    # Configuration variables
│   │   ├── outputs.tf      # Output values
│   │   └── backend.tf      # State management
│   ├── QUICKSTART.md       # AWS deployment guide
│   └── README.md           # AWS documentation
│
├── paid-ai-bot/            # Premium AI bot system
│   ├── bot.js              # Main server
│   ├── payments.js         # Stripe integration
│   ├── huggingface.js      # AI processing
│   ├── providers/          # Task providers
│   │   ├── customQueue.js
│   │   ├── directClients.js
│   │   ├── mturk.js
│   │   ├── appen.js
│   │   └── rapidapi.js
│   ├── package.json
│   └── README.md
│
├── chimera_core/           # AI decision engine
├── freelance_engine/       # Automated task sourcing
├── backend/                # FastAPI backend
├── frontend/               # React frontend
├── api/                    # API endpoints
├── tests/                  # Test suites
├── testing/                # Test infrastructure
├── automation/             # Automation scripts
│
├── unified_system.py       # Main orchestrator (34KB)
├── demo_chimera.py         # Chimera demo
├── bot.js                  # Discord/trading bot
├── server.js               # Main Node.js server
├── package.json            # Node.js dependencies
├── requirements.txt        # Python dependencies
├── Dockerfile              # Container configuration
├── Procfile                # Process definitions
├── railway.json            # Railway deployment
└── .env.example            # Environment template
```

## 🛠️ Configuration

### Required Environment Variables

#### AWS (for deployment)
```bash
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_REGION=us-east-1
```

#### AI & Payments (for paid-ai-bot)
```bash
STRIPE_SECRET_KEY=sk_...
STRIPE_WEBHOOK_SECRET=whsec_...
HUGGINGFACE_API_KEY=hf_...
```

#### Optional Providers
```bash
MTURK_ACCESS_KEY=...
APPEN_API_KEY=...
RAPIDAPI_KEY=...
```

See [.env.example](.env.example) for complete configuration options.

## 📚 Documentation

- **[AWS Quick Start](aws/QUICKSTART.md)** - Deploy to AWS in minutes
- **[AI Bot Quick Start](QUICKSTART_AI_BOT.md)** - Set up the paid AI bot
- **[AWS Deployment Guide](aws/README_AWS_DEPLOYMENT.md)** - Detailed AWS setup
- **[Paid AI Bot README](paid-ai-bot/README.md)** - Complete bot documentation
- **[Cloud Deployment Guide](CLOUD_DEPLOYMENT_GUIDE.md)** - Multi-cloud deployment
- **[Security Summary](SECURITY_SUMMARY.md)** - Security considerations

## 🔄 Automated Workflows

### Consolidate Best Parts
Automatically consolidates code from source repositories:
1. Go to **Actions** > **Consolidate Best Parts**
2. Click **Run workflow**
3. All source repos are cloned, backed up, and merged

### AWS Complete Setup
One-click deployment to AWS:
1. Configure AWS credentials in GitHub Secrets
2. Go to **Actions** > **AWS Complete Setup & Deployment**
3. Click **Run workflow**
4. Infrastructure provisioned and app deployed

### AWS Monitoring
Continuous health monitoring (every 15 minutes):
- Checks ECS task status
- Monitors RDS health
- Verifies endpoint availability
- Sends alerts on failures

## 🧪 Testing

```bash
# Run all tests
npm test

# Run Python tests
pytest

# Lint code
npm run lint
npm run format:check
```

## 🚀 Deployment Options

### Railway
```bash
railway login
railway init
railway up
```

### Heroku
```bash
heroku create
git push heroku main
```

### AWS (via GitHub Actions)
Configure secrets and run workflow - see [AWS Quick Start](aws/QUICKSTART.md)

### Docker
```bash
docker build -t the-basics .
docker run -p 3000:3000 the-basics
```

## 📊 Pricing Plans (Paid AI Bot)

| Plan | Price | Tasks/Month | Priority |
|------|-------|-------------|----------|
| Basic | $9.99 | 1,000 | Normal |
| Pro | $29.99 | 5,000 | High |
| Enterprise | $99.99 | Unlimited | Urgent |

## 🔒 Security

- Never commit API keys or secrets
- Use environment variables for all credentials
- Enable 2FA on all service accounts
- Review [SECURITY_SUMMARY.md](SECURITY_SUMMARY.md)
- Run security audits regularly

## 🤝 Contributing

This repository consolidates code from:
- ndax-quantum-engine
- quantum-engine-dashb
- shadowforge-ai-trader
- repository-web-app
- The-new-ones

All source repositories are backed up in the consolidation process.

## 📝 License

MIT

## 🆘 Support

- **Issues**: GitHub Issues
- **Documentation**: See `/docs` and individual README files
- **Quick Starts**: See QUICKSTART guides for specific components
