output "lambda_execution_role_arn" {
  description = "Lambda execution role ARN."
  value       = aws_iam_role.lambda_execution.arn
}

output "lambda_execution_role_name" {
  description = "Lambda execution role name."
  value       = aws_iam_role.lambda_execution.name
}

output "cloudwatch_logs_policy_arn" {
  description = "CloudWatch Logs policy ARN."
  value       = aws_iam_policy.cloudwatch_logs.arn
}

output "s3_access_policy_arn" {
  description = "S3 access policy ARN."
  value       = aws_iam_policy.s3_access.arn
}
