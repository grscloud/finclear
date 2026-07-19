output "state_bucket_name" {
  description = "Terraform state S3 bucket name."
  value       = module.bootstrap.state_bucket_name
}

output "state_bucket_arn" {
  description = "Terraform state S3 bucket ARN."
  value       = module.bootstrap.state_bucket_arn
}

output "lock_table_name" {
  description = "Terraform lock DynamoDB table name."
  value       = module.bootstrap.lock_table_name
}

output "lock_table_arn" {
  description = "Terraform lock DynamoDB table ARN."
  value       = module.bootstrap.lock_table_arn
}
