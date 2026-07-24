resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = merge(var.tags, {
    Name = "${var.name_prefix}-vpc"
  })
}

resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = merge(var.tags, {
    Name = "${var.name_prefix}-igw"
  })
}

resource "aws_subnet" "public" {
  for_each = { for idx, cidr in var.public_subnet_cidrs : idx => cidr }

  vpc_id                  = aws_vpc.main.id
  cidr_block              = each.value
  availability_zone       = var.availability_zones[tonumber(each.key)]
  map_public_ip_on_launch = true

  tags = merge(var.tags, {
    Name = "${var.name_prefix}-public-subnet-${tonumber(each.key) + 1}"
    Tier = "public"
  })
}

resource "aws_subnet" "private" {
  for_each = { for idx, cidr in var.private_subnet_cidrs : idx => cidr }

  vpc_id            = aws_vpc.main.id
  cidr_block        = each.value
  availability_zone = var.availability_zones[tonumber(each.key)]

  tags = merge(var.tags, {
    Name = "${var.name_prefix}-private-subnet-${tonumber(each.key) + 1}"
    Tier = "private"
  })
}


#######################################
# Route Tables
#######################################

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = merge(var.tags, {
    Name = "${var.name_prefix}-public-rt"
  })
}


# Private subnet intentionally has no Internet route.
# No NAT Gateway.
resource "aws_route_table" "private" {
  vpc_id = aws_vpc.main.id

  tags = merge(var.tags, {
    Name = "${var.name_prefix}-private-rt"
  })
}


resource "aws_route_table_association" "public" {
  for_each = aws_subnet.public

  subnet_id      = each.value.id
  route_table_id = aws_route_table.public.id
}


resource "aws_route_table_association" "private" {
  for_each = aws_subnet.private

  subnet_id      = each.value.id
  route_table_id = aws_route_table.private.id
}


#######################################
# Security Groups
#######################################

# resource "aws_security_group" "lambda" {
#   name        = "${var.name_prefix}-lambda-sg"
#   description = "Security group for Lambda functions"
#   vpc_id      = aws_vpc.main.id


#   egress {
#     description = "HTTPS outbound"
#     from_port   = 443
#     to_port     = 443
#     protocol    = "tcp"
#     cidr_blocks = ["0.0.0.0/0"]
#   }


#   tags = merge(var.tags, {
#     Name = "${var.name_prefix}-lambda-sg"
#   })
# }

# 1. 纯净的安全组主体（不要写任何 ingress / egress 块）
resource "aws_security_group" "lambda" {
  name        = "${var.name_prefix}-lambda-sg"
  description = "Security group for Lambda functions"
  vpc_id      = aws_vpc.main.id

  tags = merge(var.tags, {
    Name = "${var.name_prefix}-lambda-sg"
  })
}

# 2. 将原来的 443 内联规则，抽离成独立的规则资源
resource "aws_vpc_security_group_egress_rule" "lambda_https" {
  security_group_id = aws_security_group.lambda.id
  description       = "HTTPS outbound"
  cidr_ipv4         = "0.0.0.0/0"  # 注意新版资源的参数名是 cidr_ipv4
  ip_protocol       = "tcp"
  from_port         = 443
  to_port           = 443
}

# 3. 保持你原有的 RDS 5432 独立规则不变
resource "aws_vpc_security_group_egress_rule" "lambda_to_rds" {
  security_group_id            = aws_security_group.lambda.id
  referenced_security_group_id = aws_security_group.rds.id
  ip_protocol                  = "tcp"
  from_port                    = 5432
  to_port                      = 5432
  description                  = "PostgreSQL to RDS"
}


resource "aws_security_group" "rds" {
  name        = "${var.name_prefix}-rds-sg"
  description = "Security group for RDS PostgreSQL"
  vpc_id      = aws_vpc.main.id


  ingress {
    description     = "PostgreSQL from Lambda"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.lambda.id]
  }

  ingress {
    description = "PostgreSQL from within VPC (e.g. CloudShell)"
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = [aws_vpc.main.cidr_block] # 使用你 VPC 的 CIDR
  }

  tags = merge(var.tags, {
    Name = "${var.name_prefix}-rds-sg"
  })
}


# resource "aws_vpc_security_group_egress_rule" "lambda_to_rds" {
#   security_group_id            = aws_security_group.lambda.id
#   referenced_security_group_id = aws_security_group.rds.id
#   ip_protocol                  = "tcp"
#   from_port                    = 5432
#   to_port                      = 5432
#   description                  = "PostgreSQL to RDS"
# }