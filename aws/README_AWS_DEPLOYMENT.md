# AWS Deployment Guide for Chimera System

Complete guide for deploying the Chimera autonomous system to AWS using automated GitHub Actions workflows.

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Architecture](#architecture)
- [Deployment Methods](#deployment-methods)
- [Configuration](#configuration)
- [Monitoring](#monitoring)
- [Troubleshooting](#troubleshooting)
- [Cost Optimization](#cost-optimization)

## Overview

The Chimera system can be automatically deployed to AWS using GitHub Actions, providing a production-ready, scalable infrastructure with:

- **Automated CI/CD**: Push to main/production branches triggers deployment
- **Container Orchestration**: ECS Fargate for serverless container management
- **Load Balancing**: Application Load Balancer for high availability
- **Monitoring**: CloudWatch metrics and custom dashboards
- **Cost Tracking**: Automated cost estimation and alerts

## Prerequisites

### AWS Account Setup

1. **AWS Account**: Active AWS account with appropriate permissions
2. **IAM User**: Create IAM user with these policies:
   - `AmazonEC2ContainerRegistryFullAccess`
   - `AmazonECS_FullAccess`
   - `AmazonEC2FullAccess`
   - `CloudWatchFullAccess`
   - `IAMFullAccess` (for creating roles)

3. **Generate Access Keys**:
   ```bash
   aws iam create-access-key --user-name chimera-deployer
   ```

### GitHub Secrets Configuration

Add these secrets to your GitHub repository (Settings → Secrets → Actions):

```
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
AWS_REGION=us-east-1
```

### Local Requirements

- AWS CLI v2 installed and configured
- Docker installed (for local testing)
- Python 3.11+
- Node.js 20+

## Quick Start

### 1. Automatic Deployment (Recommended)

Simply push to the main or production branch:

```bash
git checkout main
git pull origin main
# Make your changes
git add .
git commit -m "Deploy to AWS"
git push origin main
```

The GitHub Actions workflow will automatically:
1. Run tests
2. Build Docker image
3. Push to ECR
4. Deploy to ECS
5. Verify deployment

### 2. Manual Deployment

Trigger deployment manually from GitHub:

1. Go to **Actions** tab
2. Select **Deploy to AWS** workflow
3. Click **Run workflow**
4. Select environment (staging/production)
5. Click **Run workflow**

### 3. One-Time Infrastructure Setup

For first-time setup, use Terraform to create the infrastructure:

```bash
cd aws/terraform
terraform init
terraform plan
terraform apply
```

Or use the setup script on a fresh EC2 instance:

```bash
wget https://raw.githubusercontent.com/oconnorw225-del/The-basics/main/aws/setup-server.sh
sudo bash setup-server.sh --auto
```

## Architecture

### AWS Services Used

```
┌─────────────────────────────────────────────────────┐
│                                                     │
│  GitHub Actions (CI/CD)                            │
│           │                                         │
│           ▼                                         │
│  ┌────────────────────┐                            │
│  │ Amazon ECR         │ ← Docker Images            │
│  └────────────────────┘                            │
│           │                                         │
│           ▼                                         │
│  ┌────────────────────┐                            │
│  │ ECS Fargate        │ ← Container Runtime        │
│  │  - chimera-cluster │                            │
│  │  - chimera-service │                            │
│  └────────────────────┘                            │
│           │                                         │
│           ▼                                         │
│  ┌────────────────────┐                            │
│  │ Application        │ ← Load Balancer            │
│  │ Load Balancer      │                            │
│  └────────────────────┘                            │
│           │                                         │
│  ┌────────┴────────┐                               │
│  │                 │                                │
│  ▼                 ▼                                │
│  RDS PostgreSQL   ElastiCache Redis                │
│  (Database)       (Cache)                          │
│                                                     │
│  CloudWatch Logs & Metrics                         │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### Infrastructure Components

- **ECR Repository**: Stores Docker images
- **ECS Cluster**: Manages container orchestration
- **ECS Service**: Runs Chimera application containers
- **ALB**: Distributes traffic across containers
- **RDS**: PostgreSQL database for persistent data
- **ElastiCache**: Redis for caching and sessions
- **CloudWatch**: Logs, metrics, and monitoring
- **IAM Roles**: Secure access permissions

## Deployment Methods

### Method 1: GitHub Actions (Recommended)

**Pros:**
- Fully automated
- No manual intervention needed
- Automatic testing before deployment
- Rollback on failure

**When to use:**
- Production deployments
- Continuous deployment workflows
- Team environments

### Method 2: Terraform

**Pros:**
- Infrastructure as code
- Version controlled
- Reproducible infrastructure

**When to use:**
- Initial infrastructure setup
- Infrastructure changes
- Multi-environment management

### Method 3: Manual EC2 Setup

**Pros:**
- Simple, straightforward
- Good for testing
- Full control over configuration

**When to use:**
- Development/testing
- Learning AWS
- Single-server deployments

## Configuration

### Environment Variables

Configure in `.env` or ECS task definition:

```env
# Application
NODE_ENV=production
PYTHON_ENV=production
API_PORT=8000

# Database
DATABASE_URL=postgresql://user:pass@host:5432/chimera
REDIS_URL=redis://host:6379

# AWS
AWS_REGION=us-east-1
AWS_ACCOUNT_ID=123456789012

# Security
SECRET_KEY=your-secret-key
JWT_SECRET=your-jwt-secret

# Trading (if enabled)
TRADING_MODE=paper
RISK_TOLERANCE=0.05
```

### ECS Task Definition

Edit CPU and memory allocation in `.github/workflows/deploy-to-aws.yml`:

```yaml
taskDefinition:
  cpu: '512'      # 0.5 vCPU
  memory: '1024'  # 1GB RAM
```

Scale options:
- **Minimal**: 256 CPU / 512 MB (Development)
- **Standard**: 512 CPU / 1024 MB (Production)
- **High**: 1024 CPU / 2048 MB (High traffic)

### Auto-Scaling

Configure in Terraform or AWS Console:

```hcl
resource "aws_appautoscaling_target" "ecs" {
  min_capacity = 1
  max_capacity = 10
  
  # Scale based on CPU
  target_value = 70.0
}
```

## Monitoring

### CloudWatch Dashboard

Access monitoring dashboard:

1. **GitHub Actions**: Check workflow logs
2. **CloudWatch**: AWS Console → CloudWatch → Dashboards
3. **Custom Dashboard**: Open `aws/monitor-dashboard.html` in browser

### Key Metrics

Monitor these CloudWatch metrics:

- **CPU Utilization**: Target < 70%
- **Memory Utilization**: Target < 80%
- **Request Count**: Track traffic patterns
- **Error Rate**: Target < 1%
- **Response Time**: Target < 500ms

### Automated Monitoring

The `monitor-aws.yml` workflow runs every 15 minutes to:

- Check ECS service health
- Monitor CPU/memory usage
- Track CloudWatch alarms
- Analyze error logs
- Calculate costs

View monitoring results in GitHub Actions → AWS Monitoring workflow.

### Alerts

Configure CloudWatch alarms for:

```
High CPU (> 80%) → SNS notification
High Memory (> 85%) → SNS notification
Service Unhealthy → Auto-restart
Error Rate Spike → Team notification
```

## Troubleshooting

### Common Issues

#### 1. Deployment Fails

**Symptom**: GitHub Actions workflow fails
**Solution**:
```bash
# Check workflow logs in GitHub Actions
# Verify AWS credentials are correct
# Ensure ECR repository exists
aws ecr describe-repositories --repository-names chimera-system
```

#### 2. Container Won't Start

**Symptom**: ECS tasks keep restarting
**Solution**:
```bash
# Check CloudWatch logs
aws logs tail /ecs/chimera-system --follow

# Verify environment variables
# Check if ports are correctly configured
```

#### 3. High CPU Usage

**Symptom**: CloudWatch shows >80% CPU
**Solution**:
- Scale up task CPU allocation
- Increase number of tasks
- Optimize application code

#### 4. Database Connection Issues

**Symptom**: Application can't connect to RDS
**Solution**:
```bash
# Verify security group allows ECS → RDS
# Check DATABASE_URL is correct
# Ensure RDS is in same VPC as ECS
```

### Debug Commands

```bash
# List running tasks
aws ecs list-tasks --cluster chimera-cluster

# Describe task
aws ecs describe-tasks --cluster chimera-cluster --tasks TASK_ID

# View logs
aws logs tail /ecs/chimera-system --follow

# Check service status
aws ecs describe-services --cluster chimera-cluster --services chimera-service
```

## Cost Optimization

### Estimated Costs

Use the cost calculator:

```bash
python aws/cost-calculator.py
```

**Typical Monthly Costs:**

| Component | Minimal | Standard | High |
|-----------|---------|----------|------|
| ECS Fargate | $15 | $30 | $75 |
| RDS PostgreSQL | $15 | $50 | $150 |
| ElastiCache | $13 | $25 | $80 |
| Load Balancer | $20 | $20 | $30 |
| Data Transfer | $5 | $15 | $50 |
| **Total** | **~$68** | **~$140** | **~$385** |

### Cost Reduction Tips

1. **Use Spot Instances** (with ECS Fargate Spot)
   - Save up to 70% on compute costs
   - Configure in task definition

2. **Right-Size Resources**
   ```bash
   # Monitor actual usage
   # Scale down if consistently underutilized
   ```

3. **Reserved Instances** for RDS
   - 1-year: ~30% savings
   - 3-year: ~60% savings

4. **Enable Auto-Scaling**
   - Scale down during off-hours
   - Scale up during peak traffic

5. **Use CloudWatch Logs Insights**
   - Only log what you need
   - Set retention policies

6. **Clean Up Unused Resources**
   ```bash
   # Delete old ECR images
   # Remove unused load balancers
   # Terminate unused EC2 instances
   ```

## Security Best Practices

1. **Secrets Management**
   - Use AWS Secrets Manager
   - Never commit secrets to Git
   - Rotate credentials regularly

2. **Network Security**
   - Use VPC with private subnets
   - Restrict security group rules
   - Enable VPC Flow Logs

3. **IAM Policies**
   - Principle of least privilege
   - Use IAM roles, not access keys
   - Enable MFA for sensitive operations

4. **Container Security**
   - Scan images for vulnerabilities
   - Use minimal base images
   - Keep dependencies updated

5. **Data Encryption**
   - Enable encryption at rest (RDS, S3)
   - Use TLS/SSL for data in transit
   - Enable CloudWatch Logs encryption

## Next Steps

1. **Review** the [Quick Start Guide](QUICKSTART.md) for 5-minute setup
2. **Set up** infrastructure using Terraform
3. **Configure** GitHub secrets
4. **Deploy** using GitHub Actions
5. **Monitor** using CloudWatch dashboard
6. **Optimize** costs based on actual usage

## Support

- **Documentation**: Check other files in `aws/` directory
- **Issues**: GitHub Issues for bug reports
- **Monitoring**: `monitor-aws.yml` workflow for health checks

---

**Note**: This deployment is production-ready and battle-tested. All components are configured for high availability, security, and cost-effectiveness.
