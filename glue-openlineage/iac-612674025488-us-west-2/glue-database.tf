# Glue Database for Iceberg tables
resource "aws_glue_catalog_database" "iceberg_database" {
  name        = "demo_db"
  description = "Database for Iceberg tables"

  tags = local.default_tags
}
