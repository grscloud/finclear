variable "name_prefix" {
  description = "Resource name prefix."
  type        = string
}

variable "private_subnet_ids" {
  description = "Private subnet IDs for the DB subnet group."
  type        = list(string)
}

variable "security_group_ids" {
  description = "Security group IDs attached to RDS."
  type        = list(string)
}

variable "db_name" {
  description = "Database name."
  type        = string
}

variable "db_username" {
  description = "Master username."
  type        = string
}

variable "db_password" {
  description = "Master password."
  type        = string
  sensitive   = true
}

variable "engine_version" {
  description = "PostgreSQL engine version."
  type        = string
}

variable "instance_class" {
  description = "RDS instance class."
  type        = string
}

variable "allocated_storage" {
  description = "Initial storage in GB."
  type        = number
}

variable "max_allocated_storage" {
  description = "Maximum autoscaling storage in GB."
  type        = number
}

variable "backup_retention_period" {
  description = "Backup retention in days."
  type        = number
}

variable "deletion_protection" {
  description = "Enable deletion protection."
  type        = bool
}

variable "tags" {
  description = "Tags applied to RDS resources."
  type        = map(string)
  default     = {}
}
