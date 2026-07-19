output "bucket_ids" {
  description = "Map of bucket logical names to bucket IDs."
  value       = { for key, bucket in aws_s3_bucket.buckets : key => bucket.id }
}

output "bucket_arns" {
  description = "Map of bucket logical names to bucket ARNs."
  value       = { for key, bucket in aws_s3_bucket.buckets : key => bucket.arn }
}

output "bucket_names" {
  description = "Map of bucket logical names to bucket names."
  value       = { for key, bucket in aws_s3_bucket.buckets : key => bucket.bucket }
}

output "frontend_bucket_name" {
  description = "Frontend S3 bucket name."
  value       = try(aws_s3_bucket.buckets["frontend"].bucket, null)
}

output "frontend_bucket_regional_domain_name" {
  description = "Frontend S3 bucket regional domain name."
  value       = try(aws_s3_bucket.buckets["frontend"].bucket_regional_domain_name, null)
}

output "application_bucket_name" {
  description = "Application storage S3 bucket name."
  value       = try(aws_s3_bucket.buckets["application"].bucket, null)
}
