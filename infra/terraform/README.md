# FinClear Terraform Infrastructure

Production-ready Terraform configuration for **FinClear**, a SaaS expense management system operated by GRS-CLOUD on AWS.

## Architecture

```text
Internet
   │
   ▼
Route53 (finclear.grs-co.jp)
   │
   ▼
CloudFront
   ├── Default behavior → S3 (Vue frontend)
   └── /api/* behavior  → HTTP API Gateway → Lambda (FastAPI/Mangum)
                                              │
                                              ├── RDS PostgreSQL (private)
                                              └── S3 (application storage)
```

| Component | Technology |
|-----------|------------|
| Frontend | Vue.js → S3 → CloudFront |
| Backend | FastAPI → Mangum → Lambda → HTTP API |
| Database | Amazon RDS PostgreSQL |
| File Storage | Amazon S3 |
| DNS | Amazon Route53 |
| Certificate | AWS ACM (us-east-1 for CloudFront) |
| Monitoring | Amazon CloudWatch |

## Directory Structure

```text
terraform/
├── README.md
├── versions.tf
├── providers.tf
├── variables.tf
├── locals.tf
├── modules/
│   ├── network/
│   ├── iam/
│   ├── rds/
│   ├── s3/
│   ├── lambda/
│   ├── api_gateway/
│   ├── cloudfront/
│   ├── route53/
│   ├── acm/
│   └── cloudwatch/
├── backend/
│   ├── bootstrap/
│   └── main.tf
└── environments/
    ├── dev/
    └── prod/
```

## Prerequisites

- Terraform >= 1.8
- AWS CLI configured with appropriate credentials
- Existing Route53 hosted zone: `grs-co.jp`
- IAM permissions to create VPC, RDS, Lambda, S3, CloudFront, ACM, and related resources

## Installation

1. Clone the repository and change to the Terraform directory:

```bash
cd infra/terraform
```

2. Verify Terraform and AWS CLI:

```bash
terraform version
aws sts get-caller-identity
```

## Deployment Flow

### Step 1: Bootstrap Remote State

Deploy the S3 state bucket and DynamoDB lock table once per AWS account:

```bash
cd backend
terraform init
terraform plan
terraform apply
```

### Step 2: Configure Environment Variables

Edit the target environment `terraform.tfvars` and configure the environment-specific variables.

```bash
# environments/dev/terraform.tfvars
# environments/prod/terraform.tfvars
```

### Step 3: Deploy an Environment

```bash
cd environments/dev   # or environments/prod
terraform init
terraform plan
terraform apply
```

### Step 4: Deploy Application Artifacts

After infrastructure is provisioned:

1. Build and sync the Vue frontend to the frontend S3 bucket (`finclear-{env}-frontend`).
2. Deploy the FastAPI Lambda package to replace the bootstrap handler.
3. Verify HTTPS access at `https://finclear.grs-co.jp`.

## Common Commands

### terraform init

```bash
cd environments/dev
terraform init
```

### terraform plan

```bash
terraform plan -var-file=terraform.tfvars
```

### terraform apply

```bash
terraform apply -var-file=terraform.tfvars
```

### terraform destroy

```bash
terraform destroy -var-file=terraform.tfvars
```

> **Warning:** Production RDS has deletion protection enabled. Disable it in `terraform.tfvars` before destroy if required.

## Environments

| Setting | dev | prod |
|---------|-----|------|
| VPC CIDR | 10.0.0.0/16 | 10.1.0.0/16 |
| RDS deletion protection | false | true |
| State key | dev/terraform.tfstate | prod/terraform.tfstate |

Environment differences are controlled exclusively through `terraform.tfvars` and backend state keys.

## Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `aws_region` | Primary AWS region | `ap-northeast-1` |
| `environment` | Environment name | `dev` / `prod` |
| `project_name` | Resource naming prefix | `finclear` |
| `domain_name` | Application domain | `finclear.grs-co.jp` |
| `hosted_zone_name` | Route53 zone | `grs-co.jp` |
| `vpc_cidr` | VPC CIDR block | environment-specific |
| `public_subnet_cidrs` | Public subnet CIDRs | environment-specific |
| `private_subnet_cidrs` | Private subnet CIDRs | environment-specific |
| `availability_zones` | AZ list | `ap-northeast-1a`, `ap-northeast-1c` |
| `db_name` | PostgreSQL database name | `finclear` |
| `db_username` | PostgreSQL master user | `finclear_admin` |
| `db_instance_class` | RDS instance class | `db.t4g.micro` |
| `db_allocated_storage` | Initial storage (GB) | `20` |
| `db_max_allocated_storage` | Max autoscaling storage (GB) | `100` |
| `db_engine_version` | PostgreSQL version | `16.9` |
| `db_backup_retention_period` | Backup retention (days) | `7` |
| `db_deletion_protection` | RDS deletion protection | `false` (dev) / `true` (prod) |
| `lambda_memory_size` | Lambda memory (MB) | `1024` |
| `lambda_timeout` | Lambda timeout (seconds) | `30` |
| `lambda_runtime` | Lambda runtime | `python3.13` |
| `lambda_architecture` | Lambda architecture | `arm64` |
| `lambda_log_level` | Application log level | `INFO` |
| `cloudfront_price_class` | CloudFront price class | `PriceClass_200` |
| `log_retention_in_days` | CloudWatch retention | `30` |
| `tags` | Additional resource tags | `{}` |

## Outputs

| Output | Description |
|--------|-------------|
| `vpc_id` | VPC identifier |
| `public_subnet_ids` | Public subnet IDs |
| `private_subnet_ids` | Private subnet IDs |
| `lambda_arn` | Lambda function ARN |
| `api_endpoint` | HTTP API invoke URL |
| `cloudfront_domain` | CloudFront distribution domain |
| `bucket_names` | S3 bucket name map |
| `database_endpoint` | RDS connection endpoint |
| `hosted_zone_id` | Route53 hosted zone ID |
| `certificate_arn` | ACM certificate ARN |
| `application_url` | Public application URL |

## Resource Naming

All resources follow:

```text
{project}-{environment}-{resource}
```

Example: `finclear-dev-vpc`, `finclear-prod-lambda`

## Tags

Every resource receives:

```text
Project     = FinClear
ManagedBy   = Terraform
Owner       = GRS-CLOUD
Environment = dev|prod
```

## Security Notes

- RDS and Lambda run in private subnets; RDS is not publicly accessible.
- S3 buckets block public access; frontend access is via CloudFront OAC only.
- IAM policies follow least privilege for Lambda (CloudWatch Logs, S3 access, and VPC ENI).

## License

Internal use — GRS-CLOUD / FinClear.
