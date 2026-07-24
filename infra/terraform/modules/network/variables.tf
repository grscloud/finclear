variable "name_prefix" {
  description = "Resource name prefix."
  type        = string
}


variable "vpc_cidr" {
  description = "VPC CIDR block."
  type        = string
}


variable "public_subnet_cidrs" {
  description = "Public subnet CIDR blocks."
  type        = list(string)
}


variable "private_subnet_cidrs" {
  description = "Private subnet CIDR blocks."
  type        = list(string)
}


variable "availability_zones" {
  description = "Availability zones."
  type        = list(string)
}


variable "enable_vpc_endpoints" {
  description = "Enable VPC endpoints."
  type        = bool
  default     = true
}


variable "tags" {
  description = "Tags applied to network resources."
  type        = map(string)
  default     = {}
}

variable "aws_region" {
  description = "AWS region."
  type        = string
  default     = "ap-northeast-1"
}