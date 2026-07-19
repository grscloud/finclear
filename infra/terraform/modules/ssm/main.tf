resource "random_password" "database" {
  length           = 32
  special          = true
  override_special = "!#$%&*()-_=+[]{}<>:?"
}

resource "random_password" "jwt_secret" {
  length  = 64
  special = false
}

resource "random_password" "smtp_password" {
  length           = 32
  special          = true
  override_special = "!#$%&*()-_=+[]{}<>:?"
}

resource "random_password" "application_secret" {
  length  = 64
  special = false
}

resource "aws_ssm_parameter" "secrets" {
  for_each = local.parameters

  name        = "${var.parameter_prefix}/${each.key}"
  description = each.value.description
  type        = "SecureString"
  value       = each.value.value

  tags = merge(var.tags, {
    Name = "${var.name_prefix}-ssm-${each.key}"
  })
}
