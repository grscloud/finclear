#######################################
# VPC Endpoints (S3 Only - Free)
#######################################

# S3 Gateway Endpoint (100% Free)
resource "aws_vpc_endpoint" "s3" {
  count = var.enable_vpc_endpoints ? 1 : 0

  vpc_id       = aws_vpc.main.id
  service_name = "com.amazonaws.${var.aws_region}.s3"

  # Gateway 类型完全免费
  vpc_endpoint_type = "Gateway"

  # 绑定到私有路由表，供私有子网中的 Lambda 直连 S3
  route_table_ids = [
    aws_route_table.private.id
  ]

  tags = merge(var.tags, {
    Name = "${var.name_prefix}-s3-endpoint"
  })
}