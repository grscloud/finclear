variable "name_prefix" {
  description = "Resource name prefix."
  type        = string
}

variable "parameter_prefix" {
  description = "SSM parameter path prefix."
  type        = string
}

variable "openai_api_key" {
  description = "OpenAI API key stored as SecureString."
  type        = string
  sensitive   = true
}

variable "tags" {
  description = "Tags applied to SSM parameters."
  type        = map(string)
  default     = {}
}
