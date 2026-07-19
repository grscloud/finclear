locals {
  lambda_log_group_arn_prefix = "arn:aws:logs:${var.aws_region}:${var.aws_account_id}:log-group:/aws/lambda/${var.name_prefix}-"
}
