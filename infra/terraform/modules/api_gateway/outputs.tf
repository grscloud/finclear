output "api_id" {
  description = "HTTP API ID."
  value       = aws_apigatewayv2_api.main.id
}

output "api_endpoint" {
  description = "HTTP API endpoint URL."
  value       = aws_apigatewayv2_stage.main.invoke_url
}

output "api_arn" {
  description = "HTTP API ARN."
  value       = aws_apigatewayv2_api.main.arn
}

output "execution_arn" {
  description = "HTTP API execution ARN."
  value       = aws_apigatewayv2_api.main.execution_arn
}

output "stage_name" {
  description = "API stage name."
  value       = aws_apigatewayv2_stage.main.name
}

output "api_domain" {
  description = "API Gateway domain for CloudFront origin."
  value       = replace(aws_apigatewayv2_api.main.api_endpoint, "https://", "")
}

output "api_log_group_arn" {
  description = "API Gateway CloudWatch log group ARN."
  value       = aws_cloudwatch_log_group.api.arn
}

output "api_log_group_name" {
  description = "API Gateway CloudWatch log group name."
  value       = aws_cloudwatch_log_group.api.name
}
