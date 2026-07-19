output "certificate_arn" {
  description = "Validated ACM certificate ARN."
  value       = aws_acm_certificate_validation.main.certificate_arn
}

output "certificate_domain_name" {
  description = "Certificate domain name."
  value       = aws_acm_certificate.main.domain_name
}

output "certificate_status" {
  description = "Certificate status."
  value       = aws_acm_certificate.main.status
}
