locals {
  name_prefix = "${var.project_name}-${var.environment}"

  default_tags = merge(
    {
      Project     = "FinClear"
      ManagedBy   = "Terraform"
      Owner       = "GRS-CLOUD"
      Environment = var.environment
    },
    var.tags
  )

  ssm_prefix = coalesce(var.ssm_parameter_prefix, "/${var.project_name}/${var.environment}")

  lambda_architectures = [var.lambda_architecture]
}
