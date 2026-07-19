output "parameter_prefix" {
  description = "SSM parameter path prefix."
  value       = var.parameter_prefix
}

output "parameter_names" {
  description = "Map of logical names to SSM parameter names."
  value       = { for key, param in aws_ssm_parameter.secrets : key => param.name }
}

output "parameter_arns" {
  description = "Map of logical names to SSM parameter ARNs."
  value       = { for key, param in aws_ssm_parameter.secrets : key => param.arn }
}

output "database_password_parameter_name" {
  description = "SSM parameter name for database password."
  value       = aws_ssm_parameter.secrets["database_password"].name
}

output "database_password" {
  description = "Generated database password for RDS provisioning."
  value       = random_password.database.result
  sensitive   = true
}
