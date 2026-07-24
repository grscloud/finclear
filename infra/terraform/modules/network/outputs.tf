output "vpc_id" {
  description = "VPC ID."
  value       = aws_vpc.main.id
}


output "public_subnet_ids" {
  description = "Public subnet IDs."
  value       = [for subnet in aws_subnet.public : subnet.id]
}


output "private_subnet_ids" {
  description = "Private subnet IDs."
  value       = [for subnet in aws_subnet.private : subnet.id]
}


output "lambda_security_group_id" {
  description = "Lambda security group ID."
  value       = aws_security_group.lambda.id
}


output "rds_security_group_id" {
  description = "RDS security group ID."
  value       = aws_security_group.rds.id
}