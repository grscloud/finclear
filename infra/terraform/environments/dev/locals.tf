locals {
  name_prefix          = "${var.project_name}-${var.environment}"
  lambda_function_name = "${local.name_prefix}-lambda"

  default_tags = merge(
    {
      Project     = "FinClear"
      ManagedBy   = "Terraform"
      Owner       = "GRS-CLOUD"
      Environment = var.environment
    },
    var.tags
  )

  lambda_architectures = [var.lambda_architecture]

  cors_allow_origins = [
    "https://${var.domain_name}",
  ]
}
