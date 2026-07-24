variable "name_prefix" {
  description = "Resource name prefix."
  type        = string
}

variable "lambda_function_name" {
  description = "Lambda function name for log group."
  type        = string
}

variable "log_retention_in_days" {
  description = "Log retention period in days."
  type        = number
  default     = 3
}

variable "tags" {
  description = "Tags applied to CloudWatch resources."
  type        = map(string)
  default     = {}
}
