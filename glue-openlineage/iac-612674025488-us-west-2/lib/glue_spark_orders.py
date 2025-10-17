import sys
import uuid
from pyspark.sql import SparkSession


spark = SparkSession.builder.getOrCreate()

# Configure Iceberg (runtime modifiable configuration)
spark.conf.set("spark.sql.catalog.glue_catalog", "org.apache.iceberg.spark.SparkCatalog")
spark.conf.set("spark.sql.catalog.glue_catalog.warehouse", "s3://lh-core-kolya-landing-zone/icebergs/")
spark.conf.set("spark.sql.catalog.glue_catalog.catalog-impl", "org.apache.iceberg.aws.glue.GlueCatalog")
spark.conf.set("spark.sql.catalog.glue_catalog.io-impl", "org.apache.iceberg.aws.s3.S3FileIO")

# OpenLineage configuration (all configured in glue job parameters)

def main():
    # Read CSV file from S3
    input_path = "s3://lh-core-kolya-landing-zone/files/raw_orders.csv"
    
    print(f"Starting to read data: {input_path}")
    
    # Read CSV file
    orders_df = spark.read \
        .option("header", "true") \
        .option("inferSchema", "true") \
        .csv(input_path)
                    
    # Write to Iceberg table (will auto-create if table doesn't exist)
    database_name = "demo_db"
    table_name = "orders"
    output_table = f"glue_catalog.{database_name}.{table_name}"
    
    print(f"Starting to write to Iceberg table: {output_table}")
    
    # Write to Iceberg table (will auto-create if table doesn't exist)
    # DataFrameWriterV2 API
    # orders_df.writeTo(output_table) \
    #     .option("write.format.default", "parquet") \
    #     .option("write.parquet.compression-codec", "snappy") \
    #     .createOrReplace()

    # DataFrameWriterV1 API
    orders_df.write \
    .format("iceberg") \
    .option("path", 's3://lh-core-kolya-landing-zone/icebergs/demo.db/orders') \
    .mode("overwrite") \
    .saveAsTable("glue_catalog.demo_db.orders")

if __name__ == "__main__":
    main()