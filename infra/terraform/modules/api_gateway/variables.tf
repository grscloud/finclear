variable "name_prefix" {
  description = "Resource name prefix."
  type        = string
}

variable "lambda_invoke_arn" {
  description = "Lambda invoke ARN."
  type        = string
}

variable "stage_name" {
  description = "API Gateway stage name."
  type        = string
  default     = "$default"
}

variable "cors_allow_origins" {
  description = "CORS allowed origins."
  type        = list(string)
}

variable "cors_allow_methods" {
  description = "CORS allowed methods."
  type        = list(string)
  default     = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
}

variable "cors_allow_headers" {
  description = "CORS allowed headers."
  type        = list(string)
  default     = ["Authorization", "Content-Type", "X-Requested-With"]
}

variable "cors_expose_headers" {
  description = "CORS exposed headers."
  type        = list(string)
  default     = []
}

variable "cors_max_age" {
  description = "CORS max age in seconds."
  type        = number
  default     = 300
}

variable "throttling_burst_limit" {
  description = "API throttling burst limit."
  type        = number
  default     = 5000
}

variable "throttling_rate_limit" {
  description = "API throttling rate limit."
  type        = number
  default     = 10000
}

variable "log_retention_in_days" {
  description = "CloudWatch log retention in days."
  type        = number
  default     = 3
}

variable "tags" {
  description = "Tags applied to API Gateway resources."
  type        = map(string)
  default     = {}
}
