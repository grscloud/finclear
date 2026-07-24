variable "aws_region" {
  description = "AWS region for bootstrap resources."
  type        = string
  default     = "ap-northeast-1"
}

variable "state_bucket_name" {
  description = "S3 bucket name for Terraform remote state."
  type        = string
  default     = "finclear-terraform-state"
}

variable "lock_table_name" {
  description = "DynamoDB table name for Terraform state locking."
  type        = string
  default     = "finclear-terraform-lock"
}

variable "name_prefix" {
  type        = string
  description = "Prefix for naming resources"
}