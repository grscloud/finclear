resource "aws_db_subnet_group" "main" {
  name       = "${var.name_prefix}-db-subnet-group"
  subnet_ids = var.private_subnet_ids

  tags = merge(var.tags, {
    Name = "${var.name_prefix}-db-subnet-group"
  })
}

resource "aws_db_parameter_group" "main" {
  name   = "${var.name_prefix}-pg-params"
  family = local.parameter_group_family

  parameter {
    name  = "log_connections"
    value = "1"
  }

  parameter {
    name  = "log_disconnections"
    value = "1"
  }

  tags = merge(var.tags, {
    Name = "${var.name_prefix}-pg-params"
  })
}

resource "aws_db_instance" "main" {
  identifier = "${var.name_prefix}-rds"

  engine         = "postgres"
  engine_version = var.engine_version
  instance_class = var.instance_class

  allocated_storage     = var.allocated_storage
  max_allocated_storage = var.max_allocated_storage
  storage_type          = "gp3"
  storage_encrypted     = true

  db_name  = var.db_name
  username = var.db_username
  password = var.db_password

  db_subnet_group_name   = aws_db_subnet_group.main.name
  parameter_group_name   = aws_db_parameter_group.main.name
  vpc_security_group_ids = var.security_group_ids

  multi_az                  = false
  publicly_accessible       = false
  backup_retention_period   = var.backup_retention_period
  deletion_protection       = var.deletion_protection
  skip_final_snapshot       = !var.deletion_protection
  final_snapshot_identifier = var.deletion_protection ? "${var.name_prefix}-rds-final" : null

  auto_minor_version_upgrade   = true
  copy_tags_to_snapshot        = true
  performance_insights_enabled = false

  tags = merge(var.tags, {
    Name = "${var.name_prefix}-rds"
  })
}
