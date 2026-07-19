output "lambda_log_group_name" {
  description = "Lambda CloudWatch log group name."
  value       = aws_cloudwatch_log_group.lambda.name
}

output "lambda_log_group_arn" {
  description = "Lambda CloudWatch log group ARN."
  value       = aws_cloudwatch_log_group.lambda.arn
}
