variable "aws_region" {
  description = "AWS region for primary resources."
  type        = string
  default     = "ap-northeast-1"
}

variable "environment" {
  description = "Deployment environment."
  type        = string
  default     = "prod"
}

variable "project_name" {
  description = "Project name used in resource naming."
  type        = string
  default     = "finclear"
}

variable "domain_name" {
  description = "Application domain name."
  type        = string
  default     = "finclear.grs-co.jp"
}

variable "hosted_zone_name" {
  description = "Route53 hosted zone name."
  type        = string
  default     = "grs-co.jp"
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC."
  type        = string
  default     = "10.1.0.0/16"
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks for public subnets."
  type        = list(string)
  default     = ["10.1.1.0/24", "10.1.2.0/24"]
}

variable "private_subnet_cidrs" {
  description = "CIDR blocks for private subnets."
  type        = list(string)
  default     = ["10.1.10.0/24", "10.1.20.0/24"]
}

variable "availability_zones" {
  description = "Availability zones for subnet placement."
  type        = list(string)
  default     = ["ap-northeast-1a", "ap-northeast-1c"]
}

variable "db_name" {
  description = "PostgreSQL database name."
  type        = string
  default     = "finclear"
}

variable "db_username" {
  description = "PostgreSQL master username."
  type        = string
  default     = "finclear_admin"
}

variable "db_instance_class" {
  description = "RDS instance class."
  type        = string
  default     = "db.t4g.micro"
}

variable "db_allocated_storage" {
  description = "Initial allocated storage in GB."
  type        = number
  default     = 20
}

variable "db_max_allocated_storage" {
  description = "Maximum allocated storage for autoscaling in GB."
  type        = number
  default     = 100
}

variable "db_engine_version" {
  description = "PostgreSQL engine version."
  type        = string
  default     = "16.6"
}

variable "db_backup_retention_period" {
  description = "Number of days to retain automated backups."
  type        = number
  default     = 7
}

variable "db_deletion_protection" {
  description = "Enable deletion protection on the RDS instance."
  type        = bool
  default     = true
}

variable "lambda_memory_size" {
  description = "Lambda function memory size in MB."
  type        = number
  default     = 1024
}

variable "lambda_timeout" {
  description = "Lambda function timeout in seconds."
  type        = number
  default     = 30
}

variable "lambda_runtime" {
  description = "Lambda function runtime."
  type        = string
  default     = "python3.13"
}

variable "lambda_architecture" {
  description = "Lambda function architecture."
  type        = string
  default     = "arm64"
}

variable "lambda_log_level" {
  description = "Application log level passed to Lambda."
  type        = string
  default     = "INFO"
}

variable "cloudfront_price_class" {
  description = "CloudFront distribution price class."
  type        = string
  default     = "PriceClass_200"
}

variable "log_retention_in_days" {
  description = "CloudWatch log retention period in days."
  type        = number
  default     = 30
}

variable "openai_api_key" {
  description = "OpenAI API key stored in SSM Parameter Store."
  type        = string
  sensitive   = true
}

variable "tags" {
  description = "Additional tags applied to all resources."
  type        = map(string)
  default     = {}
}
