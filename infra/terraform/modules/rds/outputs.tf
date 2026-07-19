output "db_instance_id" {
  description = "RDS instance ID."
  value       = aws_db_instance.main.id
}

output "db_instance_arn" {
  description = "RDS instance ARN."
  value       = aws_db_instance.main.arn
}

output "db_endpoint" {
  description = "RDS connection endpoint."
  value       = aws_db_instance.main.endpoint
}

output "db_address" {
  description = "RDS hostname."
  value       = aws_db_instance.main.address
}

output "db_port" {
  description = "RDS port."
  value       = aws_db_instance.main.port
}

output "db_subnet_group_name" {
  description = "DB subnet group name."
  value       = aws_db_subnet_group.main.name
}

output "db_parameter_group_name" {
  description = "DB parameter group name."
  value       = aws_db_parameter_group.main.name
}
