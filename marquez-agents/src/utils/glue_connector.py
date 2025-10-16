"""
AWS Glue Connector Tool
"""

from typing import Any

import boto3
from config import settings


class GlueConnector:
    """AWS Glue Data Catalog Connector"""

    def __init__(self):
        self.glue_client = boto3.client(
            "glue", region_name=settings.get("bedrock.region", "us-west-2")
        )

    def get_databases(self) -> list[str]:
        """Get all database names"""
        try:
            response = self.glue_client.get_databases()
            return [db["Name"] for db in response["DatabaseList"]]
        except Exception as e:
            raise Exception(f"Failed to get Glue databases: {str(e)}") from e

    def get_database_details(self) -> list[dict[str, Any]]:
        """Get database detailed information"""
        try:
            response = self.glue_client.get_databases()
            databases = []

            for db in response["DatabaseList"]:
                databases.append(
                    {
                        "name": db["Name"],
                        "description": db.get("Description", ""),
                        "location_uri": db.get("LocationUri", ""),
                        "parameters": db.get("Parameters", {}),
                    }
                )

            return databases
        except Exception as e:
            raise Exception(f"Failed to get Glue database details: {str(e)}") from e

    def get_tables(self, database_name: str | None = None) -> list[dict[str, Any]]:
        """Get table information"""
        try:
            if database_name:
                # Get tables from specified database
                response = self.glue_client.get_tables(DatabaseName=database_name)
                tables = []

                for table in response["TableList"]:
                    tables.append(
                        {
                            "name": table["Name"],
                            "database": database_name,
                            "location": table.get("StorageDescriptor", {}).get(
                                "Location", ""
                            ),
                            "input_format": table.get("StorageDescriptor", {}).get(
                                "InputFormat", ""
                            ),
                            "output_format": table.get("StorageDescriptor", {}).get(
                                "OutputFormat", ""
                            ),
                            "columns": len(
                                table.get("StorageDescriptor", {}).get("Columns", [])
                            ),
                            "table_type": table.get("TableType", ""),
                            "parameters": table.get("Parameters", {}),
                        }
                    )

                return tables
            else:
                # Get tables from all databases
                databases = self.get_databases()
                all_tables = []

                for db_name in databases:
                    try:
                        tables_response = self.glue_client.get_tables(
                            DatabaseName=db_name
                        )

                        for table in tables_response["TableList"]:
                            all_tables.append(
                                {
                                    "name": table["Name"],
                                    "database": db_name,
                                    "location": table.get("StorageDescriptor", {}).get(
                                        "Location", ""
                                    ),
                                    "input_format": table.get(
                                        "StorageDescriptor", {}
                                    ).get("InputFormat", ""),
                                    "output_format": table.get(
                                        "StorageDescriptor", {}
                                    ).get("OutputFormat", ""),
                                    "columns": len(
                                        table.get("StorageDescriptor", {}).get(
                                            "Columns", []
                                        )
                                    ),
                                    "table_type": table.get("TableType", ""),
                                    "parameters": table.get("Parameters", {}),
                                }
                            )
                    except Exception:
                        # Skip inaccessible databases
                        continue

                return all_tables

        except Exception as e:
            raise Exception(f"Failed to get Glue table information: {str(e)}") from e

    def get_table_details(self, database_name: str, table_name: str) -> dict[str, Any]:
        """Get detailed table information including column information"""
        try:
            response = self.glue_client.get_table(
                DatabaseName=database_name, Name=table_name
            )

            table = response["Table"]
            storage_descriptor = table.get("StorageDescriptor", {})
            columns = storage_descriptor.get("Columns", [])

            return {
                "name": table["Name"],
                "database": database_name,
                "location": storage_descriptor.get("Location", ""),
                "input_format": storage_descriptor.get("InputFormat", ""),
                "output_format": storage_descriptor.get("OutputFormat", ""),
                "table_type": table.get("TableType", ""),
                "parameters": table.get("Parameters", {}),
                "columns": [
                    {
                        "name": col["Name"],
                        "type": col["Type"],
                        "comment": col.get("Comment", ""),
                    }
                    for col in columns
                ],
                "partition_keys": [
                    {
                        "name": pk["Name"],
                        "type": pk["Type"],
                        "comment": pk.get("Comment", ""),
                    }
                    for pk in table.get("PartitionKeys", [])
                ],
            }

        except Exception as e:
            raise Exception(
                f"Failed to get details for table {database_name}.{table_name}: {str(e)}"
            ) from e

    def search_tables(self, search_text: str) -> list[dict[str, Any]]:
        """Search for tables containing specified text in table name"""
        try:
            all_tables = self.get_tables()
            matching_tables = [
                table
                for table in all_tables
                if search_text.lower() in table["name"].lower()
            ]
            return matching_tables
        except Exception as e:
            raise Exception(f"Failed to search tables: {str(e)}") from e

    def get_statistics(self) -> dict[str, Any]:
        """Get Glue data catalog statistics"""
        try:
            databases = self.get_databases()
            total_tables = 0
            database_stats = []

            for db_name in databases:
                try:
                    tables = self.get_tables(db_name)
                    table_count = len(tables)
                    total_tables += table_count

                    database_stats.append(
                        {"database": db_name, "table_count": table_count}
                    )
                except Exception:
                    database_stats.append(
                        {"database": db_name, "table_count": 0, "error": "Inaccessible"}
                    )

            return {
                "total_databases": len(databases),
                "total_tables": total_tables,
                "database_details": database_stats,
            }

        except Exception as e:
            raise Exception(f"Failed to get Glue statistics: {str(e)}") from e


# Create global instance
glue_connector = GlueConnector()
