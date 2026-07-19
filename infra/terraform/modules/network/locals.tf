locals {
  public_subnet_map  = { for idx, cidr in var.public_subnet_cidrs : idx => cidr }
  private_subnet_map = { for idx, cidr in var.private_subnet_cidrs : idx => cidr }
}
