variable "hosted_zone_name" {
  description = "Route53 hosted zone name."
  type        = string
}

variable "domain_name" {
  description = "Application domain record name."
  type        = string
}

variable "cloudfront_domain_name" {
  description = "CloudFront distribution domain name."
  type        = string
}

variable "cloudfront_hosted_zone_id" {
  description = "CloudFront distribution hosted zone ID."
  type        = string
}
