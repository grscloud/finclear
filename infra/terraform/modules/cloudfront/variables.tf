variable "name_prefix" {
  description = "Resource name prefix."
  type        = string
}

variable "domain_name" {
  description = "Custom domain name for CloudFront."
  type        = string
}

variable "acm_certificate_arn" {
  description = "ACM certificate ARN in us-east-1."
  type        = string
}

variable "frontend_bucket_id" {
  description = "Frontend S3 bucket ID."
  type        = string
}

variable "frontend_bucket_arn" {
  description = "Frontend S3 bucket ARN."
  type        = string
}

variable "frontend_bucket_regional_domain_name" {
  description = "Frontend S3 bucket regional domain name."
  type        = string
}

variable "api_gateway_domain_name" {
  description = "API Gateway domain name for origin."
  type        = string
}

variable "price_class" {
  description = "CloudFront price class."
  type        = string
  default     = "PriceClass_100"
}

variable "tags" {
  description = "Tags applied to CloudFront resources."
  type        = map(string)
  default     = {}
}
