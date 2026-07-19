locals {
  parameter_group_family = "postgres${split(".", var.engine_version)[0]}"
}
