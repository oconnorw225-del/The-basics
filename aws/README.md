# AWS Deployment Guide for Chimera System

This guide will help you deploy the Chimera unified system to AWS using our automated workflow.

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Setup Instructions](#setup-instructions)
- [Running the Deployment](#running-the-deployment)
- [Accessing Your Application](#accessing-your-application)
- [Monitoring and Logs](#monitoring-and-logs)
- [Cost Management](#cost-management)
- [Teardown Instructions](#teardown-instructions)
- [Troubleshooting](#troubleshooting)

## ✅ Prerequisites

Before deploying to AWS, you need:

1. **AWS Account**: An active AWS account with billing enabled
2. **IAM User**: A user with programmatic access (Access Key ID and Secret Access Key)
3. **Required Permissions**: The IAM user must have the permissions defined in `aws/iam-policy.json`
4. **GitHub Repository Access**: Push access to this repository

### Estimated Costs

Running this infrastructure on AWS will cost approximately:
- **Minimal load**: $20-30/month
- **Moderate load**: $50-100/month
- **High load**: $100-200/month

Main cost drivers:
- NAT Gateway: ~$32/month
- Application Load Balancer: ~$16/month
- ECS Fargate: ~$15-30/month (varies with task count and CPU/memory)
- Data transfer: Variable

## 🔧 Setup Instructions

### Step 1: Create IAM User

1. Log in to AWS Console
2. Navigate to **IAM** → **Users** → **Add users**
3. Create a new user (e.g., `chimera-deployer`)
4. Select **Programmatic access**
5. Attach the policy from `aws/iam-policy.json` or create a custom policy with those permissions
6. Save the **Access Key ID** and **Secret Access Key** (you'll only see these once!)

### Step 2: Configure GitHub Secrets

1. Go to your GitHub repository
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add the following secrets:

   | Secret Name | Value |
   |-------------|-------|
   | `AWS_ACCESS_KEY_ID` | Your AWS Access Key ID |
   | `AWS_SECRET_ACCESS_KEY` | Your AWS Secret Access Key |

### Step 3: (Optional) Configure Environments

For production deployments with additional protection:

1. Go to **Settings** → **Environments**
2. Create environments: `staging` and `production`
3. Add protection rules (e.g., required reviewers for production)

## 🚀 Running the Deployment

### Option 1: Full Deployment (Recommended for First Time)

1. Go to **Actions** tab in GitHub
2. Select **AWS Complete Setup** workflow
3. Click **Run workflow**
4. Configure options:
   - **Environment**: `production` or `staging`
   - **Setup type**: `full`
   - **Auto-destroy**: Leave unchecked
5. Click **Run workflow**

The workflow will:
- ✅ Validate AWS credentials
- ✅ Create complete infrastructure (VPC, ECS, ALB, etc.)
- ✅ Build and deploy your application
- ✅ Provide the application URL

**Duration**: 5-8 minutes

### Option 2: Infrastructure Only

If you only want to set up the infrastructure without deploying the application:

1. Select **Setup type**: `infrastructure-only`
2. Run the workflow

### Option 3: Deploy Only

If infrastructure already exists and you just want to update the application:

1. Select **Setup type**: `deploy-only`
2. Run the workflow

## 🌐 Accessing Your Application

After deployment completes:

1. Check the workflow run summary for the **Application URL**
2. The URL will look like: `http://chimera-alb-123456789.us-east-1.elb.amazonaws.com`
3. Access this URL in your browser
4. It may take 2-3 minutes for the service to become fully available

### Health Check

The application includes a built-in health check endpoint:
```bash
curl http://your-load-balancer-url/
```

## 📊 Monitoring and Logs

### View Logs

**Using AWS CLI:**
```bash
# Follow logs in real-time
aws logs tail /ecs/chimera-system --follow --region us-east-1

# View logs for specific time range
aws logs tail /ecs/chimera-system --since 1h --region us-east-1
```

**Using AWS Console:**
1. Navigate to **CloudWatch** → **Log groups**
2. Find `/ecs/chimera-system`
3. Click to view log streams

### Check Service Status

```bash
# Describe ECS service
aws ecs describe-services \
  --cluster chimera-cluster \
  --services chimera-service \
  --region us-east-1

# List running tasks
aws ecs list-tasks \
  --cluster chimera-cluster \
  --service-name chimera-service \
  --region us-east-1
```

### Monitor Costs

**Using the cost calculator:**
```bash
python aws/cost-calculator.py
```

**Using AWS Console:**
1. Navigate to **AWS Cost Explorer**
2. Filter by tags: `Project=chimera`
3. View daily/monthly costs

## 💰 Cost Management

### Tips to Reduce Costs

1. **Use Staging Environment**: Deploy to staging for testing, keep production minimal
2. **Reduce Task Count**: Set `desired_count = 1` for low-traffic environments
3. **Lower Task Resources**: Use smaller CPU/memory (`task_cpu = 256`, `task_memory = 512`)
4. **Remove NAT Gateway**: For cost savings, use public subnets only (less secure)
5. **Enable Auto-Scaling**: Scale down during off-peak hours

### Cost Alerts

Set up billing alerts in AWS:
1. Go to **AWS Billing** → **Billing preferences**
2. Enable **Receive Billing Alerts**
3. Create CloudWatch billing alarms for your threshold

## 🗑️ Teardown Instructions

To completely remove all AWS resources and stop billing:

### Option 1: Using Terraform (Recommended)

```bash
# Clone the repository
git clone <your-repo-url>
cd The-basics/aws/terraform

# Configure AWS credentials
export AWS_ACCESS_KEY_ID=<your-key>
export AWS_SECRET_ACCESS_KEY=<your-secret>
export AWS_REGION=us-east-1

# Destroy all resources
terraform init
terraform destroy -auto-approve
```

### Option 2: Using AWS Console

1. **ECS Service**: Navigate to ECS → Clusters → chimera-cluster → Delete
2. **Load Balancer**: EC2 → Load Balancers → Select chimera-alb → Delete
3. **Target Groups**: EC2 → Target Groups → Select chimera-tg → Delete
4. **ECR Repository**: ECR → Repositories → chimera-system → Delete
5. **CloudWatch Logs**: CloudWatch → Log groups → /ecs/chimera-system → Delete
6. **NAT Gateway**: VPC → NAT Gateways → Select → Delete
7. **Elastic IP**: VPC → Elastic IPs → Release
8. **VPC**: VPC → Your VPCs → Select chimera-vpc → Delete

**Important**: Delete in this order to avoid dependency errors!

## 🔧 Troubleshooting

### Issue: Workflow fails with "Exit code 254"

**Cause**: Missing IAM permissions

**Solution**:
1. Check that your IAM user has all permissions from `aws/iam-policy.json`
2. Verify AWS secrets are correctly configured in GitHub

### Issue: Health checks failing

**Cause**: Application not responding on expected port

**Solution**:
1. Check CloudWatch logs: `aws logs tail /ecs/chimera-system --follow`
2. Verify the container is starting correctly
3. Ensure port 8080 is exposed in Dockerfile
4. Check security group rules allow traffic

### Issue: "Service has reached a steady state"

**Cause**: ECS tasks are starting but immediately failing

**Solution**:
1. Check task logs in CloudWatch
2. Verify Docker image was built correctly
3. Ensure environment variables are set properly
4. Check task has enough CPU/memory

### Issue: Cannot access application URL

**Cause**: Load balancer or DNS propagation delay

**Solution**:
1. Wait 2-3 minutes for DNS propagation
2. Check load balancer health in EC2 console
3. Verify target group has healthy targets
4. Test directly with load balancer IP

### Issue: High costs

**Cause**: NAT Gateway, ALB running 24/7

**Solution**:
1. Review cost breakdown in Cost Explorer
2. Consider using smaller instance sizes
3. Reduce number of ECS tasks
4. Delete resources when not needed

### Issue: Terraform state lock

**Cause**: Previous deployment interrupted

**Solution**:
```bash
# If using S3 backend
aws dynamodb delete-item \
  --table-name chimera-terraform-locks \
  --key '{"LockID": {"S": "chimera/terraform.tfstate"}}' \
  --region us-east-1
```

## 📚 Additional Resources

- [AWS ECS Best Practices](https://docs.aws.amazon.com/AmazonECS/latest/bestpracticesguide/intro.html)
- [Terraform AWS Provider Documentation](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [AWS Cost Optimization](https://aws.amazon.com/pricing/cost-optimization/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)

## 🆘 Getting Help

If you encounter issues:

1. Check the **Troubleshooting** section above
2. Review workflow logs in GitHub Actions
3. Check CloudWatch logs for application errors
4. Review Terraform output for infrastructure issues
5. Open an issue in this repository with:
   - Error messages
   - Workflow logs
   - Steps to reproduce

## 📝 Notes

- **Region**: By default, resources are deployed to `us-east-1`. To change this, modify `aws_region` in `aws/terraform/variables.tf`
- **Backup**: Terraform state is stored locally by default. For team collaboration, configure S3 backend in `aws/terraform/backend.tf`
- **Security**: Never commit AWS credentials to the repository. Always use GitHub Secrets
- **Production**: For production deployments, consider:
  - Using a custom domain with Route53
  - Enabling HTTPS with ACM certificates
  - Implementing WAF rules
  - Setting up CloudWatch alarms
  - Enabling container insights
  - Using Secrets Manager for sensitive data
