output "function_name" {
  description = "Lambda function name."
  value       = aws_lambda_function.main.function_name
}

output "function_arn" {
  description = "Lambda function ARN."
  value       = aws_lambda_function.main.arn
}

output "function_invoke_arn" {
  description = "Lambda invoke ARN for API Gateway integration."
  value       = aws_lambda_function.main.invoke_arn
}

output "function_qualified_arn" {
  description = "Qualified Lambda function ARN."
  value       = aws_lambda_function.main.qualified_arn
}
