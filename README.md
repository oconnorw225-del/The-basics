# the-basics

Automated consolidation of best parts from:
- ndax-quantum-engine
- quantum-engine-dashb
- shadowforge-ai-trader
- repository-web-app
- The-new-ones

## How To Use

1. Push this structure to GitHub.
2. Go to Actions > Consolidate Best Parts > Run workflow.
3. Review and use your unified repo!

## Deployment

### AWS Deployment (Recommended) ⭐

**Get production-ready deployment in 5 minutes with one-click setup:**

#### Option 1: Fully Automated (NEW! 🆕)

1. **Set up AWS IAM user** with required permissions
2. **Add GitHub Secrets**: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION`
3. **Run workflow**: Go to Actions → "🚀 Complete AWS Setup & Deploy" → Run workflow
4. **Done!** Everything is automated - infrastructure, deployment, monitoring

The workflow automatically creates all AWS infrastructure and deploys your system.

#### Option 2: Push to Deploy

1. **Configure GitHub Secrets** (Settings → Secrets → Actions):
   ```
   AWS_ACCESS_KEY_ID=your-key
   AWS_SECRET_ACCESS_KEY=your-secret
   AWS_REGION=us-east-1
   ```

2. **Set up infrastructure once** (manual or using Terraform)
   
3. **Deploy by pushing:**
   ```bash
   git push origin main
   ```

4. **Done!** GitHub Actions automatically deploys with monitoring.

📖 **AWS Quick Start**: [aws/QUICKSTART.md](aws/QUICKSTART.md) - Includes one-click setup instructions  
📖 **Full AWS Guide**: [aws/README_AWS_DEPLOYMENT.md](aws/README_AWS_DEPLOYMENT.md)

### Local Development

See [DEPLOYMENT.md](DEPLOYMENT.md) for local development setup.

## Contents
- `/api` — consolidated APIs
- `/backend` — backend logic
- `/frontend` — UI components
- `/docs` — documentation
- `/tests` — test suites
- `/automation` — scripts for consolidation
- `/backups` — archived original sources
