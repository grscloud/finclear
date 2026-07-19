data "archive_file" "lambda_package" {
  type        = "zip"
  source_dir  = "${path.module}/lambda_src"
  output_path = "${path.module}/.build/${var.name_prefix}-lambda.zip"
}

resource "aws_lambda_function" "main" {
  function_name = "${var.name_prefix}-lambda"
  role          = var.execution_role_arn
  handler       = local.handler
  runtime       = var.runtime
  architectures = var.architectures

  filename         = data.archive_file.lambda_package.output_path
  source_code_hash = data.archive_file.lambda_package.output_base64sha256

  memory_size = var.memory_size
  timeout     = var.timeout

  vpc_config {
    subnet_ids         = var.private_subnet_ids
    security_group_ids = var.security_group_ids
  }

  environment {
    variables = {
      DATABASE_ENDPOINT  = var.database_endpoint
      DATABASE_NAME      = var.database_name
      DATABASE_USER      = var.database_user
      SSM_PARAMETER_PATH = var.ssm_parameter_path
      BUCKET_NAME        = var.bucket_name
      LOG_LEVEL          = var.log_level
    }
  }

  logging_config {
    log_format = "Text"
    log_group  = var.log_group_name
  }

  tags = merge(var.tags, {
    Name = "${var.name_prefix}-lambda"
  })
}
