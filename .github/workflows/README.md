# GitHub Actions Workflows

This directory contains GitHub Actions workflows for automating various tasks in The-basics repository.

## Active Workflows

### Consolidation Workflows

These workflows handle consolidation of code from multiple source repositories:

#### 1. **consolidate.yml** - Consolidate Best Parts
- **Trigger**: Manual via `workflow_dispatch`
- **Purpose**: Consolidates best parts from multiple source repositories into this repository
- **Source Repositories**:
  - `ndax-quantum-engine`
  - `quantum-engine-dashb`
  - `shadowforge-ai-trader`
  - `repository-web-app`
  - `The-new-ones`

#### 2. **consolidate2.yml** - Consolidate Best Parts 2
- **Trigger**: Manual via `workflow_dispatch`
- **Purpose**: Duplicate of consolidate.yml, can run independently
- Performs the same consolidation task as consolidate.yml

#### 3. **parallel-consolidation.yml** - Run Both Consolidation Tasks in Parallel
- **Trigger**: Manual via `workflow_dispatch`
- **Purpose**: Runs both consolidation tasks (Task 1 and Task 2) in parallel
- **Features**:
  - Accepts a task description input parameter
  - Executes two consolidation jobs simultaneously
  - Provides a summary of both task results
  - Enables autonomous bot to complete tasks efficiently

**Usage Example**:
```bash
# Trigger the parallel workflow
gh workflow run parallel-consolidation.yml -f task_description="Run both consolidation tasks"
```

### AWS Deployment Workflows

#### **aws-complete-setup.yml** - AWS Complete Setup & Deployment
- **Trigger**: Manual via `workflow_dispatch`
- **Purpose**: Complete AWS infrastructure setup and application deployment
- **Features**:
  - Validates prerequisites
  - Sets up AWS infrastructure with Terraform
  - Deploys application to ECS Fargate
  - Includes health checks and cost estimation
  - Optional auto-destroy for testing

## How Parallel Execution Works

The `parallel-consolidation.yml` workflow enables the autonomous bot to run multiple tasks simultaneously:

1. **Two Independent Jobs**: `consolidate-task-1` and `consolidate-task-2` run in parallel
2. **No Dependencies**: Both jobs start at the same time
3. **Independent Execution**: Each job clones repositories and runs consolidation independently
4. **Summary Job**: After both tasks complete, a summary job displays the results

This approach:
- Reduces overall execution time
- Allows the bot to handle multiple tasks efficiently
- Provides clear status for each parallel task
- Handles conflicts gracefully with `git push || echo` fallback

## Disabled Workflows

Several workflows are currently disabled (with `.disabled` extension):
- `cleanup-branches.yml.disabled`
- `cleanup-stale-branches.yml.disabled`
- `deploy-to-aws.yml.disabled`
- `monitor-aws.yml.disabled`
- `setup-aws-infrastructure.yml.disabled`
- `unified-system.yml.disabled`

To enable a disabled workflow, remove the `.disabled` extension.

## Permissions

All active workflows require:
- `contents: write` - To commit and push changes
- `actions: write` - To trigger other workflows (where applicable)

## Notes

- All consolidation workflows use the same `automation/consolidate.sh` script
- Backups are created before consolidation
- Git commits are made by "CI Bot" (ci-bot@example.com)
- Push failures are handled gracefully to avoid blocking on conflicts
