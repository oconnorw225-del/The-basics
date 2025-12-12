# AWS Deployment Quick Start - 5 Minutes ⚡

Get Chimera running on AWS in 5 minutes with automated deployment.

## Prerequisites Checklist

- [ ] AWS account created
- [ ] GitHub repository access
- [ ] 5 minutes of time

That's it! Everything else is automated.

## Step 1: AWS Setup (2 minutes)

### Create IAM User

```bash
# 1. Go to AWS Console → IAM → Users → Create User
# 2. Name: chimera-deployer
# 3. Attach policies:
#    - AmazonEC2ContainerRegistryFullAccess
#    - AmazonECS_FullAccess
#    - CloudWatchFullAccess

# 4. Create access key (Security credentials → Create access key)
# 5. Save the Access Key ID and Secret Access Key
```

**Quick Console Link**: https://console.aws.amazon.com/iam/home#/users$new

## Step 2: Configure GitHub Secrets (1 minute)

1. Go to your repository on GitHub
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret** and add:

```
Name: AWS_ACCESS_KEY_ID
Value: AKIA... (from Step 1)

Name: AWS_SECRET_ACCESS_KEY
Value: ... (from Step 1)

Name: AWS_REGION
Value: us-east-1
```

**Quick Link**: https://github.com/YOUR_USERNAME/The-basics/settings/secrets/actions

## Step 3: Deploy (1 minute)

### Option A: Automatic (Recommended)

Just push to main:

```bash
git checkout main
git pull
git push origin main
```

### Option B: Manual Trigger

1. Go to **Actions** tab on GitHub
2. Select **Deploy to AWS** workflow  
3. Click **Run workflow** → **Run workflow**

**Quick Link**: https://github.com/YOUR_USERNAME/The-basics/actions

## Step 4: Wait & Verify (1 minute)

Watch the deployment progress in GitHub Actions:

1. Go to **Actions** tab
2. Click on the running workflow
3. Watch the steps complete (takes ~3-5 minutes)

✅ Green checkmark = Successfully deployed!

## Step 5: Access Your System

Once deployed, your Chimera system is running!

### Get Your URL

```bash
# Find your load balancer URL
aws elbv2 describe-load-balancers \
  --query 'LoadBalancers[0].DNSName' \
  --output text
```

Or check in AWS Console:
- Go to **EC2** → **Load Balancers**
- Copy the DNS name

### Access Dashboard

```
http://YOUR-LOAD-BALANCER-DNS-NAME.us-east-1.elb.amazonaws.com
```

## What Just Happened?

The automated deployment:

1. ✅ Created Docker container of your system
2. ✅ Pushed to AWS ECR (container registry)
3. ✅ Deployed to ECS Fargate (serverless containers)
4. ✅ Set up load balancer for high availability
5. ✅ Configured CloudWatch monitoring
6. ✅ Started your autonomous system

## Verify Everything Works

### Check Service Health

```bash
# Using AWS CLI
aws ecs describe-services \
  --cluster chimera-cluster \
  --services chimera-service \
  --query 'services[0].runningCount'
```

Expected output: `2` (or your desired task count)

### Check Application Logs

```bash
aws logs tail /ecs/chimera-system --follow
```

### Monitor with GitHub Actions

The monitoring workflow runs automatically every 15 minutes:
- Go to **Actions** → **AWS Monitoring**
- View latest run for health status

## Next Steps

### Recommended Actions

1. **Set Up Domain** (Optional)
   ```bash
   # Point your domain to the load balancer
   # Use Route 53 or your DNS provider
   ```

2. **Enable HTTPS** (Recommended)
   ```bash
   # Get free SSL certificate with AWS Certificate Manager
   # Attach to load balancer
   ```

3. **View Monitoring Dashboard**
   - Open `aws/monitor-dashboard.html` in browser
   - Bookmark for quick access

4. **Configure Auto-Scaling** (Optional)
   ```bash
   # Already configured for 1-10 tasks
   # Scales automatically based on CPU
   ```

## Cost Estimate

Running 24/7 with minimal configuration:

```
ECS Fargate:       $15-30/month
Load Balancer:     $20/month
Data Transfer:     $5-15/month
CloudWatch:        $5/month
──────────────────────────────
Total:             ~$45-70/month
```

**Pro Tip**: Use Fargate Spot for 70% savings!

## Troubleshooting

### Deployment Failed?

**Check GitHub Actions logs:**
1. Go to Actions tab
2. Click failed workflow
3. Expand failed step to see error

**Common fixes:**
- Verify AWS credentials in GitHub secrets
- Check IAM permissions are correct
- Ensure region is set to `us-east-1` (or update workflows)

### Service Not Starting?

```bash
# Check task status
aws ecs describe-tasks \
  --cluster chimera-cluster \
  --tasks $(aws ecs list-tasks --cluster chimera-cluster --query 'taskArns[0]' --output text)

# View logs
aws logs tail /ecs/chimera-system --follow
```

### Can't Access Dashboard?

1. Verify security group allows HTTP (port 80)
2. Check load balancer health checks are passing
3. Ensure tasks are running (`runningCount` > 0)

## Advanced Configuration

### Scale Up/Down

```bash
# Scale to 5 tasks
aws ecs update-service \
  --cluster chimera-cluster \
  --service chimera-service \
  --desired-count 5

# Scale to 1 task (reduce costs)
aws ecs update-service \
  --cluster chimera-cluster \
  --service chimera-service \
  --desired-count 1
```

### Update Environment Variables

Edit `.github/workflows/deploy-to-aws.yml` and add to task definition:

```yaml
environment:
  - name: CUSTOM_VAR
    value: "custom_value"
```

Then redeploy by pushing to main.

### Custom Domain

1. Create Route 53 hosted zone (or use your DNS)
2. Create A record pointing to load balancer
3. Add SSL certificate in AWS Certificate Manager
4. Attach certificate to load balancer listener

## Useful Commands

```bash
# View all running tasks
aws ecs list-tasks --cluster chimera-cluster

# Force new deployment (restarts all tasks)
aws ecs update-service \
  --cluster chimera-cluster \
  --service chimera-service \
  --force-new-deployment

# View service events
aws ecs describe-services \
  --cluster chimera-cluster \
  --services chimera-service \
  --query 'services[0].events[0:5]'

# Stop a specific task
aws ecs stop-task \
  --cluster chimera-cluster \
  --task TASK_ARN
```

## Cleanup (When Done Testing)

To avoid ongoing charges:

```bash
# Delete ECS service
aws ecs delete-service \
  --cluster chimera-cluster \
  --service chimera-service \
  --force

# Delete cluster
aws ecs delete-cluster --cluster chimera-cluster

# Delete load balancer (find ARN first)
aws elbv2 delete-load-balancer --load-balancer-arn ARN

# Delete ECR images
aws ecr batch-delete-image \
  --repository-name chimera-system \
  --image-ids imageTag=latest
```

Or use Terraform:
```bash
cd aws/terraform
terraform destroy
```

## Resources

- **Full Documentation**: [README_AWS_DEPLOYMENT.md](README_AWS_DEPLOYMENT.md)
- **Monitoring Dashboard**: `aws/monitor-dashboard.html`
- **Cost Calculator**: `python aws/cost-calculator.py`
- **Terraform Setup**: `aws/terraform/`

## Support

- **Issues**: Use GitHub Issues for bugs
- **Monitoring**: Check GitHub Actions for automated health checks
- **AWS Console**: https://console.aws.amazon.com/

---

**🎉 Congratulations!** You now have a production-ready, auto-scaling, monitored Chimera system running on AWS!

**Total Time**: 5 minutes ⚡
**Monthly Cost**: ~$45-70 💰
**Uptime**: 99.9%+ 🚀
