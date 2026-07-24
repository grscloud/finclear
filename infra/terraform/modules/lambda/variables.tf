variable "name_prefix" {
  description = "Resource name prefix."
  type        = string
}

variable "execution_role_arn" {
  description = "Lambda execution role ARN."
  type        = string
}

variable "runtime" {
  description = "Lambda runtime."
  type        = string
}

variable "architectures" {
  description = "Lambda architectures."
  type        = list(string)
}

variable "memory_size" {
  description = "Memory size in MB."
  type        = number
}

variable "timeout" {
  description = "Timeout in seconds."
  type        = number
}

variable "private_subnet_ids" {
  description = "Private subnet IDs for VPC config."
  type        = list(string)
}

variable "security_group_ids" {
  description = "Security group IDs for VPC config."
  type        = list(string)
}

variable "database_endpoint" {
  description = "Database endpoint hostname."
  type        = string
}

variable "database_name" {
  description = "Database name."
  type        = string
}

variable "database_user" {
  description = "Database username."
  type        = string
}

variable "database_password" {
  description = "Database password."
  type        = string
  sensitive   = true
}

variable "bucket_name" {
  description = "Application S3 bucket name."
  type        = string
}

variable "log_level" {
  description = "Application log level."
  type        = string
}

variable "log_group_name" {
  description = "CloudWatch log group name for Lambda logging."
  type        = string
}

variable "tags" {
  description = "Tags applied to Lambda resources."
  type        = map(string)
  default     = {}
}
