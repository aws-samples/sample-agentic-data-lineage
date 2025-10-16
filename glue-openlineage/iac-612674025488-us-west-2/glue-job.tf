# Glue Job of customers ingestion
resource "aws_glue_job" "glue_spark_customers_job" {
  name        = "glue_spark_customers"
  role_arn    = aws_iam_role.glue_job_role.arn
  connections = [aws_glue_connection.vpc_connection.name]

  command {
    script_location = "s3://${aws_s3_bucket.datalake_libs_bucket.bucket}/scripts/glue_spark_customers.py"
    python_version  = "3"
  }

  default_arguments = {
    "--enable-continuous-cloudwatch-log" = "true"
    "--continuous-log-logGroup"          = "/aws-glue/jobs/output"
    "--extra-jars"                       = "s3://${aws_s3_bucket.datalake_libs_bucket.bucket}/jars/openlineage-spark_2.12-1.37.0.jar"
    "--user-jars-first"                  = "true"
    "--datalake-formats"                 = "iceberg"
    "--conf"                             = "spark.extraListeners=io.openlineage.spark.agent.OpenLineageSparkListener --conf spark.openlineage.transport.type=http --conf spark.openlineage.transport.url=http://marquez.kolya.fun/ --conf spark.openlineage.transport.endpoint=/api/v1/lineage --conf spark.openlineage.namespace=namespace-2 --conf spark.openlineage.jobName.appendDatasetName=false"
  }

  glue_version      = "5.0"
  max_retries       = 0
  timeout           = 60
  worker_type       = "G.1X"
  number_of_workers = 2

  tags = local.default_tags
}

# Upload the Python script to S3
resource "aws_s3_object" "pyspark_customers_script" {
  bucket = aws_s3_bucket.datalake_libs_bucket.bucket
  key    = "scripts/glue_spark_customers.py"
  source = "${path.module}/lib/glue_spark_customers.py"
  acl    = "private"
  etag   = filemd5("${path.module}/lib/glue_spark_customers.py")

  tags = local.default_tags
}


# Glue Job of orders ingestion
resource "aws_glue_job" "glue_spark_orders_job" {
  name        = "glue_spark_orders"
  role_arn    = aws_iam_role.glue_job_role.arn
  connections = [aws_glue_connection.vpc_connection.name]

  command {
    script_location = "s3://${aws_s3_bucket.datalake_libs_bucket.bucket}/scripts/glue_spark_orders.py"
    python_version  = "3"
  }

  default_arguments = {
    "--enable-continuous-cloudwatch-log" = "true"
    "--continuous-log-logGroup"          = "/aws-glue/jobs/output"
    "--extra-jars"                       = "s3://${aws_s3_bucket.datalake_libs_bucket.bucket}/jars/openlineage-spark_2.12-1.37.0.jar"
    "--user-jars-first"                  = "true"
    "--datalake-formats"                 = "iceberg"
    "--conf"                             = "spark.extraListeners=io.openlineage.spark.agent.OpenLineageSparkListener --conf spark.openlineage.transport.type=http --conf spark.openlineage.transport.url=http://marquez.kolya.fun/ --conf spark.openlineage.transport.endpoint=/api/v1/lineage --conf spark.openlineage.namespace=namespace-2 --conf spark.openlineage.jobName.appendDatasetName=false"
  }

  glue_version      = "5.0"
  max_retries       = 0
  timeout           = 60
  worker_type       = "G.1X"
  number_of_workers = 2

  tags = local.default_tags
}

# Upload the Python script to S3
resource "aws_s3_object" "pyspark_orders_script" {
  bucket = aws_s3_bucket.datalake_libs_bucket.bucket
  key    = "scripts/glue_spark_orders.py"
  source = "${path.module}/lib/glue_spark_orders.py"
  acl    = "private"
  etag   = filemd5("${path.module}/lib/glue_spark_orders.py")

  tags = local.default_tags
}


# Glue Job of payments ingestion
resource "aws_glue_job" "glue_spark_payments_job" {
  name        = "glue_spark_payments"
  role_arn    = aws_iam_role.glue_job_role.arn
  connections = [aws_glue_connection.vpc_connection.name]

  command {
    script_location = "s3://${aws_s3_bucket.datalake_libs_bucket.bucket}/scripts/glue_spark_payments.py"
    python_version  = "3"
  }

  default_arguments = {
    "--enable-continuous-cloudwatch-log" = "true"
    "--continuous-log-logGroup"          = "/aws-glue/jobs/output"
    "--extra-jars"                       = "s3://${aws_s3_bucket.datalake_libs_bucket.bucket}/jars/openlineage-spark_2.12-1.37.0.jar"
    "--user-jars-first"                  = "true"
    "--datalake-formats"                 = "iceberg"
    "--conf"                             = "spark.extraListeners=io.openlineage.spark.agent.OpenLineageSparkListener --conf spark.openlineage.transport.type=http --conf spark.openlineage.transport.url=http://marquez.kolya.fun/ --conf spark.openlineage.transport.endpoint=/api/v1/lineage --conf spark.openlineage.namespace=namespace-2 --conf spark.openlineage.jobName.appendDatasetName=false"
  }

  glue_version      = "5.0"
  max_retries       = 0
  timeout           = 60
  worker_type       = "G.1X"
  number_of_workers = 2

  tags = local.default_tags
}

# Upload the Python script to S3
resource "aws_s3_object" "pyspark_payments_script" {
  bucket = aws_s3_bucket.datalake_libs_bucket.bucket
  key    = "scripts/glue_spark_payments.py"
  source = "${path.module}/lib/glue_spark_payments.py"
  acl    = "private"
  etag   = filemd5("${path.module}/lib/glue_spark_payments.py")

  tags = local.default_tags
}
