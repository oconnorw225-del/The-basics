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
- **Purpose**: Runs consolidation and validation tasks in parallel
- **Features**:
  - Accepts a task description input parameter
  - **Job 1 - Consolidation & Backup**: Handles repository consolidation
  - **Job 2 - Validation & Testing**: Runs linting, formatting, tests, and build in parallel
  - Provides a summary of both task results
  - Enables autonomous bot to complete tasks efficiently by running independent operations simultaneously

**Usage Example**:
```bash
# Trigger the parallel workflow
gh workflow run parallel-consolidation.yml -f task_description="Consolidate and validate codebase"
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

The `parallel-consolidation.yml` workflow enables the autonomous bot to run multiple independent tasks simultaneously:

1. **Two Independent Jobs**: 
   - `consolidate-and-backup`: Handles repository consolidation and backup creation
   - `validate-and-test`: Runs code quality checks (linting, formatting, tests, build)
   
2. **True Parallelism**: Both jobs start at the same time, reducing overall execution time

3. **Independent Operations**: 
   - Consolidation job modifies repository content
   - Validation job checks code quality without making changes
   - No race conditions or conflicts between jobs

4. **Summary Job**: After both tasks complete, displays comprehensive results

This approach:
- Reduces overall execution time by ~50% compared to sequential execution
- Allows the bot to handle consolidation while simultaneously validating code
- Provides clear status for each parallel task
- Handles failures gracefully with conditional summary messages

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
