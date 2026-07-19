# AI Project Specification

## Project

| Item | Value |
|------|------|
| Project | FinClear |
| Product | SaaS Expense Management System |
| Company | GRS-CLOUD |
| Domain | finclear.grs-co.jp |
| Language | Japanese |
| Infrastructure | AWS |
| IaC | Terraform |
| Repository | Terraform only (Do not generate FastAPI or Vue project.) |

---

## Objective

- Generate a production-ready Terraform project.
- The project must be executable.
- Follow enterprise best practices.
- Avoid demo-style code and placeholders.
- Keep all modules reusable.

---

## Architecture

| Component | Technology |
|-----------|------------|
| Frontend | Vue.js → S3 → CloudFront |
| Backend | FastAPI → Mangum → Lambda → HTTP API |
| Database | Amazon RDS PostgreSQL |
| File Storage | Amazon S3 |
| Secret | AWS Systems Manager Parameter Store |
| DNS | Amazon Route53 |
| Certificate | AWS ACM |
| Monitoring | Amazon CloudWatch |

---

## Domain

- Domain: **finclear.grs-co.jp**
- CloudFront uses ACM Certificate.
- DNS managed by Route53.

---

## Terraform

- Terraform >= 1.8
- AWS Provider >= 6.x

### Environments

- dev
- prod

Requirements:

- Shared Modules
- Different tfvars only

### Backend

Bootstrap resources:

- S3 (Terraform State)
- DynamoDB (State Lock)

Remote State required.

---

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
│   ├── ssm/
│   ├── rds/
│   ├── s3/
│   ├── lambda/
│   ├── api_gateway/
│   ├── cloudfront/
│   ├── route53/
│   ├── acm/
│   └── cloudwatch/
├── backend/
│   └── bootstrap/
└── environments/
    ├── dev/
    └── prod/
```

---

## Naming

Format:

```
{project}-{environment}-{resource}
```

Examples:

```
finclear-dev-vpc
finclear-dev-rds
finclear-prod-lambda
```

Never use random names.

---

## Tags

Apply to every resource.

```text
Project     = FinClear
ManagedBy   = Terraform
Owner       = GRS-CLOUD
Environment = dev/prod
```

---

## Network

Create:

- VPC
- Internet Gateway
- 2 Public Subnets
- 2 Private Subnets
- NAT Gateway
- Elastic IP
- Route Tables
- Route Associations
- Security Groups

Requirements:

- 2 Availability Zones
- Lambda → Private Subnet
- RDS → Private Subnet
- Public Access Disabled

---

## Security Groups

### Lambda SG

- HTTPS Outbound
- PostgreSQL → RDS

### RDS SG

- PostgreSQL only from Lambda SG
- No Public Access

---

## IAM

Create:

- Lambda Execution Role
- CloudWatch Logs
- SSM Read
- S3 Access

Requirements:

- Reusable Policies
- Least Privilege Principle

---

## Parameter Store

Create SecureString parameters:

- Database Password
- JWT Secret
- SMTP Password
- Application Secret
- OpenAI API Key

---

## Database

| Item | Value |
|------|------|
| Engine | PostgreSQL |
| Version | Latest Stable |
| Instance | db.t4g.micro |
| AZ | Single |
| Storage | 20GB |
| Auto Scaling | Enabled |
| Backup | 7 Days |
| Deletion Protection | Dev=Off / Prod=On |

Also create:

- DB Subnet Group
- Parameter Group

---

## S3

### Bucket 1

Frontend

- Vue Build

### Bucket 2

Application Storage

- Receipt
- Invoice
- Export

Enable:

- Versioning
- Encryption
- Public Access Block
- Lifecycle Rule

---

## Lambda

| Item | Value |
|------|------|
| Runtime | Python 3.13 |
| Architecture | arm64 |
| Memory | 1024MB |
| Timeout | 30 sec |
| Adapter | Mangum |

Environment Variables:

- Database Endpoint
- Database Name
- Database User
- SSM Parameter Path
- Bucket Name
- Log Level

CloudWatch Logging enabled.

---

## API Gateway

- HTTP API
- Lambda Integration
- Stage
- Default Route
- CORS Enabled

---

## CloudFront

Origins:

- Frontend S3
- API Gateway

Behavior:

- Default → S3
- /api/* → API Gateway

Enable:

- Compression
- HTTPS Redirect
- HTTP2
- PriceClass_200

---

## ACM

- DNS Validation
- Route53 Integration
- Automatic Validation

---

## Route53

Hosted Zone:

```
grs-co.jp
```

Record:

```
finclear.grs-co.jp
```

Alias:

- CloudFront

---

## CloudWatch

Create:

- Lambda Log Groups

Retention:

- 30 Days

Enable:

- API Logging
- Lambda Logging

---

## Outputs

Generate:

- VPC ID
- Subnet IDs
- Lambda ARN
- API Endpoint
- CloudFront Domain
- Bucket Names
- Database Endpoint
- Hosted Zone ID
- Certificate ARN
- Parameter Prefix

---

## Variables

Parameterize:

- Region
- Environment
- Project Name
- CIDR
- Domain
- Subnets
- Database
- Lambda Memory
- Lambda Timeout
- Tags

Do not hardcode values.

---

## README

Include:

- Installation
- terraform init
- terraform plan
- terraform apply
- terraform destroy
- Directory Structure
- Variables
- Outputs
- Architecture
- Deployment Flow

---

## Code Style

Each module contains:

```text
main.tf
variables.tf
outputs.tf
locals.tf
```

Rules:

- Use locals whenever possible.
- Avoid duplicate code.
- Prefer for_each.
- Use dynamic blocks where appropriate.

---

## Quality

The project must:

- Pass `terraform fmt`
- Pass `terraform validate`
- Follow AWS best practices
- Avoid deprecated resources
- Generate production-quality code
- Do not generate demo code