# AWS Setup Complete Guide

## Overview

This guide provides comprehensive instructions for deploying The-basics system to AWS using ECS Fargate with Terraform.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [AWS Account Setup](#aws-account-setup)
3. [Terraform Configuration](#terraform-configuration)
4. [Deployment Steps](#deployment-steps)
5. [Monitoring and Management](#monitoring-and-management)
6. [Troubleshooting](#troubleshooting)
7. [Cost Estimation](#cost-estimation)

## Prerequisites

### Required Tools

- AWS CLI (v2.x or later)
- Terraform (v1.0 or later)
- Docker
- Git

### Installation

```bash
# AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Terraform
wget https://releases.hashicorp.com/terraform/1.6.0/terraform_1.6.0_linux_amd64.zip
unzip terraform_1.6.0_linux_amd64.zip
sudo mv terraform /usr/local/bin/

# Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```

## AWS Account Setup

### 1. Create AWS Account

If you don't have an AWS account:
1. Go to https://aws.amazon.com/
2. Click "Create an AWS Account"
3. Follow the registration process
4. Add a payment method

### 2. Create IAM User

Create a dedicated IAM user for deployment:

```bash
# Using AWS Console:
# 1. Go to IAM > Users > Add User
# 2. Username: the-basics-deployer
# 3. Access type: Programmatic access
# 4. Attach policies:
#    - AmazonECS_FullAccess
#    - AmazonEC2ContainerRegistryFullAccess
#    - AmazonVPCFullAccess
#    - IAMFullAccess (or use the policy in aws/iam-policy.json)
```

Or use the provided IAM policy:

```bash
aws iam create-policy --policy-name TheBasicsDeploymentPolicy \
  --policy-document file://aws/iam-policy.json

aws iam create-user --user-name the-basics-deployer

aws iam attach-user-policy --user-name the-basics-deployer \
  --policy-arn arn:aws:iam::YOUR_ACCOUNT_ID:policy/TheBasicsDeploymentPolicy

aws iam create-access-key --user-name the-basics-deployer
```

### 3. Configure AWS CLI

```bash
aws configure
# AWS Access Key ID: [Your access key]
# AWS Secret Access Key: [Your secret key]
# Default region name: us-east-1
# Default output format: json
```

## Terraform Configuration

### 1. Initialize Terraform

```bash
cd aws/terraform
terraform init
```

### 2. Configure Variables

Create `terraform.tfvars`:

```hcl
# Project Configuration
project_name = "the-basics"
environment  = "production"
aws_region   = "us-east-1"

# Network Configuration
vpc_cidr = "10.0.0.0/16"

# ECS Configuration
task_cpu    = 512   # 0.5 vCPU
task_memory = 1024  # 1 GB

# Scaling Configuration
desired_count           = 1
autoscaling_min_capacity = 1
autoscaling_max_capacity = 4
autoscaling_cpu_target    = 70
autoscaling_memory_target = 80

# Container Configuration
container_port = 3000

# Health Check Configuration
health_check_path                = "/"
health_check_interval            = 30
health_check_timeout             = 5
health_check_healthy_threshold   = 2
health_check_unhealthy_threshold = 3

# Monitoring
log_retention_days = 7

# Tags
tags = {
  Project     = "the-basics"
  Environment = "production"
  ManagedBy   = "Terraform"
}
```

### 3. Review Infrastructure Plan

```bash
terraform plan
```

This shows what resources will be created:
- VPC with public and private subnets
- Internet Gateway and NAT Gateway
- Application Load Balancer
- ECS Cluster and Service
- ECR Repository
- CloudWatch Log Groups
- IAM Roles and Policies
- Security Groups

## Deployment Steps

### Step 1: Build and Push Docker Image

```bash
# Build Docker image
cd /path/to/The-basics
docker build -t the-basics-system .

# Get ECR login
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

# Create ECR repository (first time only)
aws ecr create-repository --repository-name the-basics-system --region us-east-1

# Tag image
docker tag the-basics-system:latest YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/the-basics-system:latest

# Push image
docker push YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/the-basics-system:latest
```

### Step 2: Deploy Infrastructure

```bash
cd aws/terraform

# Apply Terraform configuration
terraform apply

# Confirm by typing 'yes'
```

Deployment typically takes 5-10 minutes.

### Step 3: Verify Deployment

```bash
# Get load balancer URL
terraform output alb_dns_name

# Check ECS service status
aws ecs describe-services \
  --cluster the-basics-cluster \
  --services the-basics-service \
  --region us-east-1

# View running tasks
aws ecs list-tasks \
  --cluster the-basics-cluster \
  --region us-east-1
```

### Step 4: Access Application

```bash
# Get the ALB DNS name
ALB_DNS=$(terraform output -raw alb_dns_name)

# Test the application
curl http://$ALB_DNS

# Open in browser
echo "Application URL: http://$ALB_DNS"
```

## Monitoring and Management

### CloudWatch Logs

View application logs:

```bash
# Get log streams
aws logs describe-log-streams \
  --log-group-name /ecs/the-basics-system \
  --order-by LastEventTime \
  --descending \
  --max-items 5

# View latest logs
aws logs tail /ecs/the-basics-system --follow
```

### CloudWatch Metrics

Access metrics dashboard:
1. Go to AWS Console > CloudWatch
2. Navigate to Dashboards
3. View ECS metrics for CPU, Memory, Network

Or use the monitoring dashboard:

```bash
# Open the local dashboard
open aws/monitor-dashboard.html

# Or access via web server
cd aws
python3 -m http.server 8080
# Open http://localhost:8080/monitor-dashboard.html
```

### ECS Service Management

```bash
# Update service (after pushing new image)
aws ecs update-service \
  --cluster the-basics-cluster \
  --service the-basics-service \
  --force-new-deployment

# Scale service
aws ecs update-service \
  --cluster the-basics-cluster \
  --service the-basics-service \
  --desired-count 2

# View service events
aws ecs describe-services \
  --cluster the-basics-cluster \
  --services the-basics-service \
  --query 'services[0].events[0:10]'
```

### Auto-Scaling

The deployment includes auto-scaling based on:
- CPU utilization (target: 70%)
- Memory utilization (target: 80%)

View auto-scaling status:

```bash
aws application-autoscaling describe-scalable-targets \
  --service-namespace ecs \
  --resource-ids service/the-basics-cluster/the-basics-service
```

## Troubleshooting

### Common Issues

#### 1. Task Fails to Start

**Symptoms:** Tasks start but immediately stop

**Solutions:**
```bash
# Check task logs
aws logs tail /ecs/the-basics-system --follow

# Check task definition
aws ecs describe-task-definition --task-definition the-basics-task

# Verify IAM roles
aws iam get-role --role-name the-basics-ecs-task-execution-role
```

#### 2. Health Check Failures

**Symptoms:** Load balancer health checks fail

**Solutions:**
- Verify the health check path exists in your application
- Check security group rules allow traffic on container port
- Review task logs for application errors

```bash
# Check target group health
aws elbv2 describe-target-health \
  --target-group-arn $(aws elbv2 describe-target-groups \
    --names the-basics-tg --query 'TargetGroups[0].TargetGroupArn' --output text)
```

#### 3. Cannot Pull Docker Image

**Symptoms:** "CannotPullContainerError"

**Solutions:**
```bash
# Verify ECR permissions
aws ecr get-login-password --region us-east-1

# Check image exists
aws ecr describe-images \
  --repository-name the-basics-system \
  --region us-east-1

# Verify task execution role has ECR permissions
aws iam get-role-policy \
  --role-name the-basics-ecs-task-execution-role \
  --policy-name the-basics-ecs-task-execution-ecr
```

#### 4. Out of Memory

**Symptoms:** Tasks restart frequently, OOMKilled errors

**Solutions:**
```bash
# Increase task memory in terraform.tfvars
task_memory = 2048  # Change from 1024 to 2048

# Apply changes
terraform apply

# Monitor memory usage
aws cloudwatch get-metric-statistics \
  --namespace AWS/ECS \
  --metric-name MemoryUtilization \
  --dimensions Name=ServiceName,Value=the-basics-service Name=ClusterName,Value=the-basics-cluster \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Average
```

### Debugging Steps

1. **Check ECS Service Events**
   ```bash
   aws ecs describe-services \
     --cluster the-basics-cluster \
     --services the-basics-service \
     --query 'services[0].events'
   ```

2. **View Task Details**
   ```bash
   TASK_ARN=$(aws ecs list-tasks --cluster the-basics-cluster --query 'taskArns[0]' --output text)
   aws ecs describe-tasks --cluster the-basics-cluster --tasks $TASK_ARN
   ```

3. **Check Network Configuration**
   ```bash
   # Verify security groups
   aws ec2 describe-security-groups \
     --filters Name=tag:Name,Values=the-basics-*
   
   # Check subnet configuration
   aws ec2 describe-subnets \
     --filters Name=tag:Name,Values=the-basics-*
   ```

## Cost Estimation

Use the cost calculator:

```bash
cd aws
python3 cost-calculator.py
```

### Estimated Monthly Costs (us-east-1)

**Minimal Configuration** (1 task, 0.5 vCPU, 1GB memory):
- ECS Fargate: ~$15/month
- Application Load Balancer: ~$16/month
- NAT Gateway: ~$32/month
- Data Transfer: ~$9/month (estimated 100GB)
- CloudWatch Logs: ~$5/month (estimated 10GB)
- **Total: ~$77/month**

**Production Configuration** (2 tasks, 1 vCPU, 2GB memory):
- ECS Fargate: ~$60/month
- Application Load Balancer: ~$16/month
- NAT Gateway: ~$32/month
- Data Transfer: ~$18/month (estimated 200GB)
- CloudWatch Logs: ~$10/month (estimated 20GB)
- **Total: ~$136/month**

### Cost Optimization Tips

1. **Use Fargate Spot** for non-critical workloads (70% savings)
2. **Reduce NAT Gateway costs** by using VPC endpoints
3. **Implement log retention policies** to reduce CloudWatch costs
4. **Use reserved capacity** for predictable workloads
5. **Enable auto-scaling** to scale down during low-traffic periods

## Cleanup

To remove all AWS resources:

```bash
cd aws/terraform
terraform destroy

# Manually delete ECR images (if needed)
aws ecr batch-delete-image \
  --repository-name the-basics-system \
  --image-ids imageTag=latest

# Delete ECR repository
aws ecr delete-repository \
  --repository-name the-basics-system \
  --force
```

## Additional Resources

- [AWS ECS Documentation](https://docs.aws.amazon.com/ecs/)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [AWS Fargate Pricing](https://aws.amazon.com/fargate/pricing/)
- [CloudWatch Logs](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/)

## Support

For issues specific to this deployment:
1. Check CloudWatch Logs
2. Review ECS service events
3. Verify security group rules
4. Check the troubleshooting section above

For general AWS support:
- [AWS Support Center](https://console.aws.amazon.com/support/)
- [AWS Forums](https://forums.aws.amazon.com/)
