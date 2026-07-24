terraform {
  required_version = ">= 1.8"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 6.0"
    }
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = local.default_tags
  }
}

module "bootstrap" {
  source = "./bootstrap"

  state_bucket_name = var.state_bucket_name
  lock_table_name   = var.lock_table_name
  tags              = local.default_tags
  name_prefix       = var.name_prefix
}
