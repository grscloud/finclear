variable "buckets" {
  description = "Map of bucket configurations."
  type = map(object({
    bucket_name = string
    tags        = optional(map(string), {})
  }))
}

variable "tags" {
  description = "Common tags applied to S3 buckets."
  type        = map(string)
  default     = {}
}
