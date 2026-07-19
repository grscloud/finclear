output "vpc_id" {
  description = "VPC ID."
  value       = module.network.vpc_id
}

output "public_subnet_ids" {
  description = "Public subnet IDs."
  value       = module.network.public_subnet_ids
}

output "private_subnet_ids" {
  description = "Private subnet IDs."
  value       = module.network.private_subnet_ids
}

output "lambda_arn" {
  description = "Lambda function ARN."
  value       = module.lambda.function_arn
}

output "api_endpoint" {
  description = "HTTP API endpoint URL."
  value       = module.api_gateway.api_endpoint
}

output "cloudfront_domain" {
  description = "CloudFront distribution domain name."
  value       = module.cloudfront.distribution_domain_name
}

output "bucket_names" {
  description = "S3 bucket names."
  value       = module.s3.bucket_names
}

output "database_endpoint" {
  description = "RDS database endpoint."
  value       = module.rds.db_endpoint
}

output "hosted_zone_id" {
  description = "Route53 hosted zone ID."
  value       = module.route53.hosted_zone_id
}

output "certificate_arn" {
  description = "ACM certificate ARN."
  value       = module.acm.certificate_arn
}

output "parameter_prefix" {
  description = "SSM parameter path prefix."
  value       = module.ssm.parameter_prefix
}

output "application_url" {
  description = "Application URL."
  value       = "https://${var.domain_name}"
}
