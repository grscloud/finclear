output "hosted_zone_id" {
  description = "Route53 hosted zone ID."
  value       = aws_route53_zone.main.zone_id
}

output "hosted_zone_name" {
  description = "Route53 hosted zone name."
  value       = aws_route53_zone.main.name
}

output "app_record_fqdn" {
  description = "Application DNS record FQDN."
  value       = aws_route53_record.app.fqdn
}

output "name_servers" {
  description = "Name servers to configure at your domain registrar (お名前.com)"
  value       = aws_route53_zone.main.name_servers
}