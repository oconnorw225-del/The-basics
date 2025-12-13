# Terraform Backend Configuration
# 
# This file configures remote state storage in S3 with DynamoDB locking.
# Uncomment and configure the backend block below to enable remote state.
# 
# Benefits of using remote state:
# - Team collaboration with shared state
# - State locking to prevent concurrent modifications
# - State versioning and backup
# - Encryption at rest
# 
# Prerequisites:
# 1. Create an S3 bucket for state storage:
#    aws s3api create-bucket --bucket chimera-terraform-state-<account-id> --region us-east-1
#    aws s3api put-bucket-versioning --bucket chimera-terraform-state-<account-id> --versioning-configuration Status=Enabled
#    aws s3api put-bucket-encryption --bucket chimera-terraform-state-<account-id> --server-side-encryption-configuration '{"Rules":[{"ApplyServerSideEncryptionByDefault":{"SSEAlgorithm":"AES256"}}]}'
#
# 2. Create a DynamoDB table for state locking:
#    aws dynamodb create-table --table-name chimera-terraform-locks --attribute-definitions AttributeName=LockID,AttributeType=S --key-schema AttributeName=LockID,KeyType=HASH --billing-mode PAY_PER_REQUEST --region us-east-1
#
# 3. Uncomment the backend configuration below and update with your values
# 4. Run: terraform init -migrate-state

# terraform {
#   backend "s3" {
#     bucket         = "chimera-terraform-state-<your-aws-account-id>"
#     key            = "chimera/terraform.tfstate"
#     region         = "us-east-1"
#     encrypt        = true
#     dynamodb_table = "chimera-terraform-locks"
#   }
# }

# Note: By default, Terraform will use local state storage.
# This is acceptable for individual development but not recommended for production teams.
