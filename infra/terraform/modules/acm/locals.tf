locals {
  validation_records = aws_acm_certificate.main.domain_validation_options
}
