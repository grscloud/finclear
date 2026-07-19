variable "name_prefix" {
  description = "Resource name prefix."
  type        = string
}

variable "domain_name" {
  description = "Domain name for the certificate."
  type        = string
}

variable "hosted_zone_id" {
  description = "Route53 hosted zone ID for DNS validation."
  type        = string
}

variable "tags" {
  description = "Tags applied to ACM resources."
  type        = map(string)
  default     = {}
}
