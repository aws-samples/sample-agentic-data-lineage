#!/usr/bin/env python3
"""
Iceberg to Redshift Lineage Converter
"""

import argparse
import os
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List
from urllib.parse import quote

import boto3
import psycopg2
import requests
import yaml
from dotenv import load_dotenv

load_dotenv()


class RedshiftConnector:
    """Redshift Connector"""

    def __init__(self, config: dict):
        self.config = config
        self.connection = None

    def connect(self):
        """Connect to Redshift"""
        self.connection = psycopg2.connect(
            host=self.config["host"],
            port=self.config["port"],
            database=self.config["database"],
            user=self.config["username"],
            password=self.config["password"],
        )
        self.connection.autocommit = True

    def create_external_schema(
        self, schema_name: str, glue_database: str, iam_role: str
    ) -> str:
        """Create external schema"""
        ddl = f"""CREATE EXTERNAL SCHEMA {schema_name}
FROM DATA CATALOG
DATABASE '{glue_database}'
IAM_ROLE '{iam_role}';"""

        try:
            cursor = self.connection.cursor()
            cursor.execute(ddl)
            cursor.close()
            return ddl
        except Exception as e:
            if "already exists" in str(e).lower():
                return f"-- Schema {schema_name} already exists"
            raise

    def list_tables(self, schema_name: str) -> List[str]:
        """List tables in schema"""
        cursor = self.connection.cursor()
        cursor.execute(
            """
            SELECT tablename FROM SVV_EXTERNAL_TABLES
            WHERE schemaname = %s ORDER BY tablename
        """,
            (schema_name,),
        )
        tables = [row[0] for row in cursor.fetchall()]
        cursor.close()
        return tables

    def disconnect(self):
        """Disconnect from Redshift"""
        if self.connection:
            self.connection.close()


class GlueMetadataExtractor:
    """Glue Metadata Extractor"""

    def __init__(self, aws_profile: str = None):
        session = (
            boto3.Session(profile_name=aws_profile) if aws_profile else boto3.Session()
        )
        self.glue_client = session.client("glue")

    def list_tables(self, database: str) -> List[str]:
        """List all tables in Glue database"""
        tables = []
        paginator = self.glue_client.get_paginator("get_tables")

        for page in paginator.paginate(DatabaseName=database):
            for table in page["TableList"]:
                tables.append(table["Name"])

        return tables

    def get_table_metadata(self, database: str, table: str) -> Dict[str, Any]:
        """Get table metadata"""
        response = self.glue_client.get_table(DatabaseName=database, Name=table)
        table_info = response["Table"]
        storage = table_info.get("StorageDescriptor", {})

        return {
            "database_name": table_info["DatabaseName"],
            "table_name": table_info["Name"],
            "location": storage.get("Location", ""),
            "table_type": table_info.get("TableType", ""),
            "parameters": table_info.get("Parameters", {}),
            "columns": [
                {
                    "name": col.get("Name", ""),
                    "type": col.get("Type", ""),
                    "comment": col.get("Comment", ""),
                }
                for col in storage.get("Columns", [])
            ],
        }

    def extract_namespace(self, metadata: Dict[str, Any]) -> str:
        """Extract namespace from S3 location"""
        location = metadata.get("location", "")
        if location.startswith("s3://"):
            parts = location.split("/")
            if len(parts) >= 3 and parts[2]:
                return f"s3://{parts[2]}"

        raise ValueError(f"Unable to extract namespace from metadata: {location}")

    def extract_dataset(self, metadata: Dict[str, Any]) -> str:
        """Extract dataset name from S3 path"""
        location = metadata.get("location", "")
        if location.startswith("s3://"):
            parts = location.split("/")
            if len(parts) > 3:
                dataset_path = "/".join(parts[3:]).rstrip("/")
                if dataset_path:
                    return dataset_path.replace(".", "_")

        raise ValueError(f"Unable to extract dataset from metadata: {location}")


class MarquezLineageClient:
    """Marquez Lineage Client"""

    def __init__(self, base_url: str, api_key: str = None):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        if api_key:
            self.session.headers.update({"Authorization": f"Bearer {api_key}"})
        self.session.headers.update(
            {"Content-Type": "application/json", "Accept": "application/json"}
        )

    def create_source(
        self, source_name: str, connection_url: str, description: str = None
    ) -> bool:
        """Create data source"""
        url = f"{self.base_url}/api/v1/sources/{source_name}"

        payload = {"type": "POSTGRESQL", "connectionUrl": connection_url}

        if description:
            payload["description"] = description

        try:
            response = self.session.put(url, json=payload)
            response.raise_for_status()
            print(f"✅ Data source created successfully: {source_name}")
            return True
        except requests.exceptions.RequestException as e:
            if (
                hasattr(e, "response")
                and e.response is not None
                and "already exists" in e.response.text.lower()
            ):
                print(f"ℹ️  Data source already exists: {source_name}")
                return True
            print(f"❌ Failed to create data source: {e}")
            return False

    def create_dataset(
        self,
        namespace: str,
        dataset_name: str,
        dataset_type: str = "DB_TABLE",
        physical_name: str = None,
        source_name: str = None,
        fields: List[Dict[str, str]] = None,
        description: str = None,
    ) -> Dict[str, Any]:
        """
        Create dataset

        Args:
            namespace: Namespace
            dataset_name: Dataset name
            dataset_type: Dataset type (only supports DB_TABLE and STREAM)
            physical_name: Physical name
            source_name: Source name
            fields: Field list [{"name": "field1", "type": "INTEGER"}, ...]
            description: Description
        """
        # Ensure data source exists
        if source_name and not self.create_source(
            source_name, namespace, f"{source_name} data source"
        ):
            raise ValueError(f"Unable to create data source: {source_name}")

        # URL encode namespace and dataset name
        encoded_namespace = quote(namespace, safe="")
        encoded_dataset_name = quote(dataset_name, safe="")
        url = (
            f"{self.base_url}/api/v1/namespaces/{encoded_namespace}/"
            f"datasets/{encoded_dataset_name}"
        )

        payload = {
            "type": dataset_type,
            "physicalName": physical_name or dataset_name,
            "sourceName": source_name or "default",
        }

        if fields:
            payload["fields"] = fields

        if description:
            payload["description"] = description

        try:
            response = self.session.put(url, json=payload)
            response.raise_for_status()

            print(f"✅ Dataset created successfully: {namespace}.{dataset_name}")
            return response.json() if response.text else {"status": "success"}

        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to create dataset: {e}")
            if hasattr(e, "response") and e.response is not None:
                print(f"Response content: {e.response.text}")
            raise

    def send_lineage_event(
        self,
        source_namespace: str,
        source_dataset: str,
        target_namespace: str,
        target_dataset: str,
        job_name: str,
        source_fields: List[Dict],
        target_fields: List[Dict],
        column_lineage: List[Dict],
    ) -> Dict[str, Any]:
        """Send lineage event"""
        # Use Beijing time (UTC+8)
        beijing_tz = timezone(timedelta(hours=8))
        beijing_now = datetime.now(beijing_tz)
        run_id = f"run_{int(beijing_now.timestamp())}"
        event_time = beijing_now.isoformat()

        # Build event
        event = {
            "eventType": "COMPLETE",
            "eventTime": event_time,
            "run": {"runId": run_id},
            "job": {
                "namespace": source_namespace,
                "name": job_name,
                "facets": {
                    "columnLineage": {
                        "_producer": "iceberg_lineage_converter",
                        "_schemaURL": (
                            "https://openlineage.io/spec/facets/1-0-0/"
                            "ColumnLineageJobFacet.json"
                        ),
                        "fields": {
                            field["name"]: {
                                "inputFields": field["inputFields"],
                                "transformationDescription": field.get(
                                    "transformationDescription", ""
                                ),
                                "transformationType": field.get(
                                    "transformationType", "IDENTITY"
                                ),
                            }
                            for field in column_lineage
                        },
                    }
                },
            },
            "inputs": [
                {
                    "namespace": source_namespace,
                    "name": source_dataset,
                    "facets": {
                        "schema": {
                            "_producer": "iceberg_lineage_converter",
                            "_schemaURL": (
                                "https://openlineage.io/spec/facets/1-0-0/"
                                "SchemaDatasetFacet.json"
                            ),
                            "fields": source_fields,
                        }
                    },
                }
            ],
            "outputs": [
                {
                    "namespace": target_namespace,
                    "name": target_dataset,
                    "facets": {
                        "schema": {
                            "_producer": "iceberg_lineage_converter",
                            "_schemaURL": (
                                "https://openlineage.io/spec/facets/1-0-0/"
                                "SchemaDatasetFacet.json"
                            ),
                            "fields": target_fields,
                        },
                        "columnLineage": {
                            "_producer": "iceberg_lineage_converter",
                            "_schemaURL": (
                                "https://openlineage.io/spec/facets/1-0-0/"
                                "ColumnLineageDatasetFacet.json"
                            ),
                            "fields": {
                                field["name"]: {
                                    "inputFields": field["inputFields"],
                                    "transformationDescription": field.get(
                                        "transformationDescription", ""
                                    ),
                                    "transformationType": field.get(
                                        "transformationType", "IDENTITY"
                                    ),
                                }
                                for field in column_lineage
                            },
                        },
                    },
                }
            ],
            "producer": "iceberg_lineage_converter",
        }

        # Send event
        url = f"{self.base_url}/api/v1/lineage"
        response = self.session.post(url, json=event)
        response.raise_for_status()

        return response.json() if response.text else {"status": "success"}


class IcebergLineageConverter:
    """Iceberg Lineage Converter"""

    def __init__(self, redshift_config: dict, aws_profile: str = None):
        self.redshift = RedshiftConnector(redshift_config)
        self.glue = GlueMetadataExtractor(aws_profile)
        self.marquez = None

    def setup_marquez(self, marquez_url: str, api_key: str = None):
        """Setup Marquez client"""
        self.marquez = MarquezLineageClient(marquez_url, api_key)

    def create_schema_and_lineage(
        self,
        glue_database: str,
        redshift_schema: str,
        iam_role: str,
        marquez_url: str = None,
        marquez_api_key: str = None,
    ):
        """Create schema and lineage relationships"""
        # Get Glue table list (as source)
        glue_tables = self.glue.list_tables(glue_database)
        print(
            f"📊 Found {len(glue_tables)} tables in Glue database {glue_database}: "
            f"{', '.join(glue_tables)}"
        )

        if not glue_tables:
            print("⚠️  No Glue tables found, exiting")
            return

        # Connect to Redshift
        self.redshift.connect()

        try:
            # Create external schema
            ddl = self.redshift.create_external_schema(
                redshift_schema, glue_database, iam_role
            )
            print(f"\n=== Executed DDL ===\n{ddl}")

            # Create lineage relationships
            if marquez_url:
                self.setup_marquez(marquez_url, marquez_api_key)
                print(f"\n🔗 Starting to create lineage to Marquez ({marquez_url})...")

                for table in glue_tables:
                    self._create_table_lineage(glue_database, redshift_schema, table)

                print(
                    f"\n🎉 Lineage creation completed! "
                    f"Processed {len(glue_tables)} tables"
                )
            else:
                print(
                    "\n✅ External schema creation completed, "
                    "skipping lineage creation"
                )

        finally:
            self.redshift.disconnect()

    def _create_table_lineage(
        self, glue_database: str, redshift_schema: str, table_name: str
    ):
        """Create lineage for a single table"""
        try:
            # Get Glue metadata
            glue_metadata = self.glue.get_table_metadata(glue_database, table_name)

            # Extract identification information
            source_namespace = self.glue.extract_namespace(glue_metadata)
            source_dataset = self.glue.extract_dataset(glue_metadata)

            # Build target information
            redshift_database = self.redshift.config.get("database", "redshift")
            target_dataset = f"{redshift_database}.{redshift_schema}.{table_name}"

            # Build field information and lineage
            source_fields = []
            target_fields = []
            column_lineage = []

            for col in glue_metadata["columns"]:
                field_info = {
                    "name": col["name"],
                    "type": col["type"],
                    "description": col.get("comment", ""),
                }
                source_fields.append(field_info)
                target_fields.append(field_info)

                column_lineage.append(
                    {
                        "name": col["name"],
                        "inputFields": [
                            {
                                "namespace": source_namespace,
                                "name": source_dataset,
                                "field": col["name"],
                            }
                        ],
                        "transformationDescription": (
                            "Direct mapping from Glue table to Redshift "
                            "external table"
                        ),
                        "transformationType": "IDENTITY",
                    }
                )

            # First create source and target datasets
            # 只有在数据集第一次创建时有用
            try:
                # Create target dataset (Redshift)
                self.marquez.create_dataset(
                    namespace=source_namespace,  # Use same namespace
                    dataset_name=target_dataset,
                    dataset_type="DB_TABLE",
                    physical_name=f"{redshift_database}.{redshift_schema}.{table_name}",
                    source_name="redshift-external",
                    fields=target_fields,
                    description=(
                        f"Redshift external table: {redshift_schema}.{table_name}"
                    ),
                )

            except Exception as e:
                print(f"  ⚠️  Dataset creation warning: {e}")

            # Send lineage event
            job_name = f"glue_to_redshift_{table_name}"
            print(
                f"  📊 Sending column-level lineage, "
                f"{len(column_lineage)} field mappings"
            )
            for col_mapping in column_lineage:
                input_field = col_mapping["inputFields"][0]
                print(
                    f"    - {col_mapping['name']}: "
                    f"{input_field['namespace']}.{input_field['name']}."
                    f"{input_field['field']}"
                )

            self.marquez.send_lineage_event(
                source_namespace=source_namespace,
                source_dataset=source_dataset,
                target_namespace=source_namespace,
                target_dataset=target_dataset,
                job_name=job_name,
                source_fields=source_fields,
                target_fields=target_fields,
                column_lineage=column_lineage,
            )

            print(
                f"  ✅ Lineage created: {source_namespace}.{source_dataset} -> "
                f"{source_namespace}.{target_dataset}"
            )

        except Exception as e:
            print(f"  ❌ Failed to create lineage: {table_name} - {e}")


def load_config(config_file: str) -> Dict[str, Any]:
    """Load YAML configuration file"""
    try:
        with open(config_file, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Configuration file not found: {config_file}")
    except yaml.YAMLError as e:
        raise ValueError(f"Configuration file format error: {e}")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Iceberg to Redshift Lineage Converter"
    )
    parser.add_argument(
        "--config",
        "-c",
        default="config.yaml",
        help="YAML configuration file path (default: config.yaml)",
    )
    parser.add_argument(
        "--redshift-schema",
        help="Redshift external schema name (overrides config file setting)",
    )
    parser.add_argument("--iam-role", required=True, help="IAM role ARN")
    parser.add_argument("--aws-profile", help="AWS Profile name")
    parser.add_argument("--marquez-url", help="Marquez API URL")
    parser.add_argument("--marquez-api-key", help="Marquez API key")

    args = parser.parse_args()

    # Load configuration file
    try:
        config = load_config(args.config)
    except Exception as e:
        print(f"❌ Failed to load configuration file: {e}")
        return 1

    # Get database list
    databases = config.get("databases", [])
    if not databases:
        print("❌ No database list found in configuration file")
        return 1

    # Get Redshift schema (command line argument takes priority)
    redshift_schema = args.redshift_schema or config.get("redshift_schema")
    if not redshift_schema:
        print(
            "❌ Redshift schema not specified, please provide in config file "
            "or command line"
        )
        return 1

    # Redshift configuration
    redshift_config = {
        "host": os.getenv("REDSHIFT_HOST"),
        "port": int(os.getenv("REDSHIFT_PORT", "5439")),
        "database": os.getenv("REDSHIFT_DATABASE"),
        "username": os.getenv("REDSHIFT_USERNAME"),
        "password": os.getenv("REDSHIFT_PASSWORD"),
    }

    # Get Marquez configuration (command line arguments take priority,
    # then environment variables)
    marquez_url = args.marquez_url or os.getenv("MARQUEZ_URL")
    marquez_api_key = args.marquez_api_key or os.getenv("MARQUEZ_API_KEY")

    # Create converter
    converter = IcebergLineageConverter(redshift_config, args.aws_profile)

    print(f"📋 Starting to process {len(databases)} Glue databases:")
    for db in databases:
        print(f"  - {db}")

    if marquez_url:
        print(f"🔗 Marquez URL: {marquez_url}")
    else:
        print("ℹ️  Marquez URL not configured, will skip lineage creation")

    # Process each database
    success_count = 0
    for glue_database in databases:
        print(f"\n🔄 Processing database: {glue_database}")
        try:
            converter.create_schema_and_lineage(
                glue_database=glue_database,
                redshift_schema=redshift_schema,
                iam_role=args.iam_role,
                marquez_url=marquez_url,
                marquez_api_key=marquez_api_key,
            )
            success_count += 1
            print(f"✅ Database processed successfully: {glue_database}")
        except Exception as e:
            print(f"❌ Failed to process database: {glue_database}, error: {e}")

    print(f"\n🎉 Processing completed! Success: {success_count}/{len(databases)}")
    return 0 if success_count == len(databases) else 1


if __name__ == "__main__":
    main()
