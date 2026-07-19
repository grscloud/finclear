data "aws_caller_identity" "current" {}

data "aws_route53_zone" "main" {
  name         = var.hosted_zone_name
  private_zone = false
}

module "network" {
  source = "../../modules/network"

  name_prefix          = local.name_prefix
  vpc_cidr             = var.vpc_cidr
  public_subnet_cidrs  = var.public_subnet_cidrs
  private_subnet_cidrs = var.private_subnet_cidrs
  availability_zones   = var.availability_zones
  tags                 = local.default_tags
}

module "ssm" {
  source = "../../modules/ssm"

  name_prefix      = local.name_prefix
  parameter_prefix = local.ssm_prefix
  openai_api_key   = var.openai_api_key
  tags             = local.default_tags
}

module "rds" {
  source = "../../modules/rds"

  name_prefix             = local.name_prefix
  private_subnet_ids      = module.network.private_subnet_ids
  security_group_ids      = [module.network.rds_security_group_id]
  db_name                 = var.db_name
  db_username             = var.db_username
  db_password             = module.ssm.database_password
  engine_version          = var.db_engine_version
  instance_class          = var.db_instance_class
  allocated_storage       = var.db_allocated_storage
  max_allocated_storage   = var.db_max_allocated_storage
  backup_retention_period = var.db_backup_retention_period
  deletion_protection     = var.db_deletion_protection
  tags                    = local.default_tags
}

module "s3" {
  source = "../../modules/s3"

  buckets = {
    frontend = {
      bucket_name = "${local.name_prefix}-frontend"
      tags = {
        Purpose = "Vue frontend build artifacts"
      }
    }
    application = {
      bucket_name = "${local.name_prefix}-app-storage"
      tags = {
        Purpose = "Receipt, invoice, and export files"
      }
    }
  }

  tags = local.default_tags
}

module "iam" {
  source = "../../modules/iam"

  name_prefix          = local.name_prefix
  aws_region           = var.aws_region
  aws_account_id       = data.aws_caller_identity.current.account_id
  ssm_parameter_prefix = local.ssm_prefix
  s3_bucket_arns       = values(module.s3.bucket_arns)
  tags                 = local.default_tags
}

module "cloudwatch" {
  source = "../../modules/cloudwatch"

  name_prefix           = local.name_prefix
  lambda_function_name  = local.lambda_function_name
  log_retention_in_days = var.log_retention_in_days
  tags                  = local.default_tags
}

module "lambda" {
  source = "../../modules/lambda"

  name_prefix        = local.name_prefix
  execution_role_arn = module.iam.lambda_execution_role_arn
  runtime            = var.lambda_runtime
  architectures      = local.lambda_architectures
  memory_size        = var.lambda_memory_size
  timeout            = var.lambda_timeout
  private_subnet_ids = module.network.private_subnet_ids
  security_group_ids = [module.network.lambda_security_group_id]
  database_endpoint  = module.rds.db_address
  database_name      = var.db_name
  database_user      = var.db_username
  ssm_parameter_path = local.ssm_prefix
  bucket_name        = module.s3.application_bucket_name
  log_level          = var.lambda_log_level
  log_group_name     = module.cloudwatch.lambda_log_group_name
  tags               = local.default_tags

  depends_on = [module.cloudwatch]
}

module "api_gateway" {
  source = "../../modules/api_gateway"

  name_prefix           = local.name_prefix
  lambda_invoke_arn     = module.lambda.function_invoke_arn
  cors_allow_origins    = local.cors_allow_origins
  log_retention_in_days = var.log_retention_in_days
  tags                  = local.default_tags
}

resource "aws_lambda_permission" "api_gateway" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = module.lambda.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${module.api_gateway.execution_arn}/*/*"
}

module "acm" {
  source = "../../modules/acm"

  providers = {
    aws = aws.us_east_1
  }

  name_prefix    = local.name_prefix
  domain_name    = var.domain_name
  hosted_zone_id = data.aws_route53_zone.main.zone_id
  tags           = local.default_tags
}

module "cloudfront" {
  source = "../../modules/cloudfront"

  name_prefix                          = local.name_prefix
  domain_name                          = var.domain_name
  acm_certificate_arn                  = module.acm.certificate_arn
  frontend_bucket_id                   = module.s3.bucket_ids["frontend"]
  frontend_bucket_arn                  = module.s3.bucket_arns["frontend"]
  frontend_bucket_regional_domain_name = module.s3.frontend_bucket_regional_domain_name
  api_gateway_domain_name              = module.api_gateway.api_domain
  price_class                          = var.cloudfront_price_class
  tags                                 = local.default_tags
}

module "route53" {
  source = "../../modules/route53"

  hosted_zone_name          = var.hosted_zone_name
  domain_name               = var.domain_name
  cloudfront_domain_name    = module.cloudfront.distribution_domain_name
  cloudfront_hosted_zone_id = module.cloudfront.distribution_hosted_zone_id
}
