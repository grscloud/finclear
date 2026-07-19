data "aws_iam_policy_document" "lambda_assume_role" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role" "lambda_execution" {
  name               = "${var.name_prefix}-lambda-role"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json

  tags = var.tags
}

data "aws_iam_policy_document" "cloudwatch_logs" {
  statement {
    sid    = "CloudWatchLogs"
    effect = "Allow"

    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents",
    ]

    resources = [
      "arn:aws:logs:${var.aws_region}:${var.aws_account_id}:log-group:/aws/lambda/${var.name_prefix}-*",
      "arn:aws:logs:${var.aws_region}:${var.aws_account_id}:log-group:/aws/lambda/${var.name_prefix}-*:*",
    ]
  }
}

resource "aws_iam_policy" "cloudwatch_logs" {
  name        = "${var.name_prefix}-lambda-cloudwatch-logs"
  description = "Allow Lambda to write CloudWatch Logs"
  policy      = data.aws_iam_policy_document.cloudwatch_logs.json

  tags = var.tags
}

data "aws_iam_policy_document" "ssm_read" {
  statement {
    sid    = "SSMRead"
    effect = "Allow"

    actions = [
      "ssm:GetParameter",
      "ssm:GetParameters",
      "ssm:GetParametersByPath",
    ]

    resources = [
      "arn:aws:ssm:${var.aws_region}:${var.aws_account_id}:parameter${var.ssm_parameter_prefix}/*",
    ]
  }

  statement {
    sid    = "KMSDecryptForSSM"
    effect = "Allow"

    actions = [
      "kms:Decrypt",
    ]

    resources = ["*"]

    condition {
      test     = "StringEquals"
      variable = "kms:ViaService"
      values   = ["ssm.${var.aws_region}.amazonaws.com"]
    }
  }
}

resource "aws_iam_policy" "ssm_read" {
  name        = "${var.name_prefix}-lambda-ssm-read"
  description = "Allow Lambda to read SSM Parameter Store secrets"
  policy      = data.aws_iam_policy_document.ssm_read.json

  tags = var.tags
}

data "aws_iam_policy_document" "s3_access" {
  statement {
    sid    = "S3ObjectAccess"
    effect = "Allow"

    actions = [
      "s3:GetObject",
      "s3:PutObject",
      "s3:DeleteObject",
      "s3:ListBucket",
    ]

    resources = concat(
      [for bucket in var.s3_bucket_arns : "${bucket}/*"],
      var.s3_bucket_arns,
    )
  }
}

resource "aws_iam_policy" "s3_access" {
  name        = "${var.name_prefix}-lambda-s3-access"
  description = "Allow Lambda to access application S3 buckets"
  policy      = data.aws_iam_policy_document.s3_access.json

  tags = var.tags
}

data "aws_iam_policy_document" "vpc_access" {
  statement {
    sid    = "VPCNetworkInterface"
    effect = "Allow"

    actions = [
      "ec2:CreateNetworkInterface",
      "ec2:DescribeNetworkInterfaces",
      "ec2:DeleteNetworkInterface",
      "ec2:AssignPrivateIpAddresses",
      "ec2:UnassignPrivateIpAddresses",
    ]

    resources = ["*"]
  }
}

resource "aws_iam_policy" "vpc_access" {
  name        = "${var.name_prefix}-lambda-vpc-access"
  description = "Allow Lambda to manage VPC network interfaces"
  policy      = data.aws_iam_policy_document.vpc_access.json

  tags = var.tags
}

resource "aws_iam_role_policy_attachment" "cloudwatch_logs" {
  role       = aws_iam_role.lambda_execution.name
  policy_arn = aws_iam_policy.cloudwatch_logs.arn
}

resource "aws_iam_role_policy_attachment" "ssm_read" {
  role       = aws_iam_role.lambda_execution.name
  policy_arn = aws_iam_policy.ssm_read.arn
}

resource "aws_iam_role_policy_attachment" "s3_access" {
  role       = aws_iam_role.lambda_execution.name
  policy_arn = aws_iam_policy.s3_access.arn
}

resource "aws_iam_role_policy_attachment" "vpc_access" {
  role       = aws_iam_role.lambda_execution.name
  policy_arn = aws_iam_policy.vpc_access.arn
}
