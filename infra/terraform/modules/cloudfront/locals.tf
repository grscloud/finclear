locals {
  frontend_origin_id = "S3-${var.name_prefix}-frontend"
  api_origin_id      = "APIGateway-${var.name_prefix}-api"
}
