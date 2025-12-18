# GitHub Actions Workflows

This directory contains GitHub Actions workflows for the repository. All workflows are designed to handle missing credentials and resources gracefully.

## Active Workflows

### 🚀 aws-complete-setup.yml
**Trigger**: Manual only (`workflow_dispatch`)

**Purpose**: Complete AWS infrastructure setup and deployment to ECS/Fargate.

**Requirements**:
- AWS credentials configured as repository secrets:
  - `AWS_ACCESS_KEY_ID`
  - `AWS_SECRET_ACCESS_KEY`

**Behavior**:
- ✅ **With AWS credentials**: Runs full deployment workflow
- ✅ **Without AWS credentials**: Exits gracefully with informative message
- All AWS-dependent steps are conditionally executed
- Provides clear instructions for credential configuration

**How to configure AWS credentials**:
1. Go to repository Settings → Secrets and variables → Actions
2. Add `AWS_ACCESS_KEY_ID` secret
3. Add `AWS_SECRET_ACCESS_KEY` secret
4. Manually trigger the workflow from the Actions tab

### 📦 consolidate.yml
**Trigger**: Manual only (`workflow_dispatch`)

**Purpose**: Clone and consolidate code from external source repositories.

**Requirements**:
- Access to external repositories (public or with proper token)

**Behavior**:
- ✅ **When repos accessible**: Clones, archives, consolidates, and commits
- ✅ **When repos unavailable**: Skips gracefully with helpful message
- Tracks number of successfully cloned repositories
- Only runs consolidation if at least one repo was cloned
- Provides workflow summary with troubleshooting info

## Disabled Workflows

The following workflows are disabled (`.disabled` extension) and will not run:

- `monitor-aws.yml.disabled` - AWS monitoring (was scheduled every 15 minutes)
- `deploy-to-aws.yml.disabled` - AWS deployment (was triggered on push to main/production)
- `cleanup-branches.yml.disabled` - Branch cleanup automation
- `cleanup-stale-branches.yml.disabled` - Stale branch cleanup
- `complete-aws-setup.yml.disabled` - Alternative AWS setup
- `setup-aws-infrastructure.yml.disabled` - Infrastructure-only setup
- `unified-system.yml.disabled` - Unified system deployment

**To enable**: Rename by removing the `.disabled` extension.

**⚠️ Warning**: Disabled workflows may require AWS credentials or other resources. Review and update them to handle missing credentials gracefully before enabling.

## Design Principles

All active workflows follow these principles:

1. **Graceful Degradation**: Missing credentials/resources don't cause failures
2. **Clear Messaging**: Helpful error messages explain what's needed
3. **Conditional Execution**: Steps only run when prerequisites are met
4. **Manual Triggers**: No automatic PR/push triggers to avoid false failures
5. **Security First**: No secrets exposed in logs

## Troubleshooting

### AWS workflows skip all steps
**Cause**: AWS credentials not configured

**Solution**: Add `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` secrets

### Consolidate workflow clones 0 repositories
**Cause**: External repositories are private or don't exist

**Solution**: 
1. Verify repositories exist and are accessible
2. For private repos, configure a personal access token with repo permissions
3. Update the workflow to use the token

### Workflow syntax errors
**Validation**: Run `yamllint .github/workflows/*.yml` to check syntax

## Best Practices

When adding new workflows:

1. ✅ Add credential/resource checks at the beginning
2. ✅ Use conditional execution for resource-dependent steps
3. ✅ Provide clear error messages
4. ✅ Exit with success (code 0) when resources unavailable
5. ✅ Use `workflow_dispatch` for manual-only triggers
6. ✅ Test both success and failure scenarios

## Security

- All workflows are scanned with CodeQL for security vulnerabilities
- No secrets should be exposed in workflow logs
- Use GitHub's secret masking for sensitive data
- Follow principle of least privilege for AWS IAM roles

## Support

For issues with workflows:
1. Check the workflow run logs in the Actions tab
2. Review the troubleshooting section above
3. Ensure all required secrets are configured
4. Verify resource availability (AWS account, external repos)

---

**Last Updated**: 2025-12-13
**Status**: ✅ All active workflows handle missing resources gracefully
