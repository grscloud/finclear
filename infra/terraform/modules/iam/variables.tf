variable "name_prefix" {
  description = "Resource name prefix."
  type        = string
}

variable "aws_region" {
  description = "AWS region."
  type        = string
}

variable "aws_account_id" {
  description = "AWS account ID."
  type        = string
}

variable "ssm_parameter_prefix" {
  description = "SSM parameter path prefix."
  type        = string
}

variable "s3_bucket_arns" {
  description = "S3 bucket ARNs accessible by Lambda."
  type        = list(string)
}

variable "tags" {
  description = "Tags applied to IAM resources."
  type        = map(string)
  default     = {}
}
