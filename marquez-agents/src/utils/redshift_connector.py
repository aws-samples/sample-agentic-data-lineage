"""
Redshift Connector Tool (Direct Connection)
"""

from typing import Any

import psycopg2
from config import settings


class RedshiftConnector:
    """Redshift Database Connector"""

    def __init__(self):
        self.connection = None

    def _check_config(self) -> list[str]:
        """Check required configuration"""
        required_configs = [
            "REDSHIFT_HOST",
            "REDSHIFT_DATABASE",
            "REDSHIFT_USERNAME",
            "REDSHIFT_PASSWORD",
        ]

        missing_configs = []
        for config in required_configs:
            if not hasattr(settings, config) or not getattr(settings, config):
                missing_configs.append(config)

        return missing_configs

    def _execute_query(self, query: str) -> list[dict[str, Any]]:
        """Execute SQL query"""
        # Check configuration
        missing_configs = self._check_config()
        if missing_configs:
            # Return mock data when configuration is missing
            return self._get_mock_data(query)

        try:
            # Direct connection to Redshift
            conn = psycopg2.connect(
                host=settings.REDSHIFT_HOST,
                port=getattr(settings, "REDSHIFT_PORT", 5439),
                database=settings.REDSHIFT_DATABASE,
                user=settings.REDSHIFT_USERNAME,
                password=settings.REDSHIFT_PASSWORD,
                connect_timeout=30,
            )

            cursor = conn.cursor()
            cursor.execute(query)

            # Get column names
            columns = [desc[0] for desc in cursor.description]

            # Get data
            rows = cursor.fetchall()

            # Convert to list of dictionaries
            results = []
            for row in rows:
                results.append(dict(zip(columns, row, strict=False)))

            cursor.close()
            conn.close()

            return results

        except Exception as e:
            # Throw exception when real connection fails, no longer return fake data
            raise Exception(f"Redshift query failed: {str(e)}") from e

    def _get_mock_data(self, query: str) -> list[dict[str, Any]]:
        """Return mock data (only used when configuration is missing)"""
        # Check if configuration is complete
        missing_configs = self._check_config()
        if not missing_configs:
            # If configuration is complete, should not use mock data
            raise Exception(
                "Configuration complete but connection failed, please check network connection and authentication information"
            )

        # Only return mock data when configuration is missing
        return [
            {
                "result": f'Mock data - Missing configuration: {", ".join(missing_configs)}'
            }
        ]

    def get_schemas(self) -> list[dict[str, Any]]:
        """Get all schema information (including regular and external table statistics)"""
        query = """
        WITH all_tables AS (
            SELECT schemaname
            FROM pg_tables
            WHERE schemaname NOT IN ('information_schema', 'pg_catalog')
            UNION ALL
            SELECT schemaname
            FROM SVV_EXTERNAL_TABLES
        )
        SELECT
            schemaname,
            COUNT(*) as table_count
        FROM all_tables
        GROUP BY schemaname
        ORDER BY schemaname
        """

        try:
            results = self._execute_query(query)
            return results
        except Exception as e:
            raise Exception(f"Failed to get Redshift schemas: {str(e)}") from e

    def get_tables(self, schema_name: str | None = None) -> list[dict[str, Any]]:
        """Get table information (including regular and external tables)"""
        if schema_name:
            # Query regular tables
            regular_tables_query = f"""
            SELECT schemaname, tablename, tableowner, 'regular' as table_type
            FROM pg_tables
            WHERE schemaname = '{schema_name}'
            AND schemaname NOT IN ('information_schema', 'pg_catalog')
            """

            # Query external tables (SVV_EXTERNAL_TABLES has no tableowner column, use NULL)
            external_tables_query = f"""
            SELECT schemaname, tablename, NULL as tableowner, 'external' as table_type
            FROM SVV_EXTERNAL_TABLES
            WHERE schemaname = '{schema_name}'
            """

            # Merge queries
            query = f"""
            {regular_tables_query}
            UNION ALL
            {external_tables_query}
            ORDER BY tablename
            """
        else:
            # Query all regular tables
            regular_tables_query = """
            SELECT schemaname, tablename, tableowner, 'regular' as table_type
            FROM pg_tables
            WHERE schemaname NOT IN ('information_schema', 'pg_catalog')
            """

            # Query all external tables (SVV_EXTERNAL_TABLES has no tableowner column, use NULL)
            external_tables_query = """
            SELECT schemaname, tablename, NULL as tableowner, 'external' as table_type
            FROM SVV_EXTERNAL_TABLES
            """

            # Merge queries
            query = f"""
            {regular_tables_query}
            UNION ALL
            {external_tables_query}
            ORDER BY schemaname, tablename
            """

        try:
            results = self._execute_query(query)
            return results
        except Exception as e:
            raise Exception(
                f"Failed to get Redshift table information: {str(e)}"
            ) from e

    def get_table_columns(
        self, schema_name: str, table_name: str
    ) -> list[dict[str, Any]]:
        """Get table column information"""
        query = f"""
        SELECT
            column_name,
            data_type,
            is_nullable,
            column_default,
            character_maximum_length
        FROM information_schema.columns
        WHERE table_schema = '{schema_name}'
        AND table_name = '{table_name}'
        ORDER BY ordinal_position
        """

        try:
            results = self._execute_query(query)
            return results
        except Exception as e:
            raise Exception(
                f"Failed to get column information for table {schema_name}.{table_name}: {str(e)}"
            ) from e

    def search_tables(self, search_text: str) -> list[dict[str, Any]]:
        """Search for tables containing specified text in table name (including regular and external tables)"""
        # Search regular tables
        regular_tables_query = f"""
        SELECT schemaname, tablename, tableowner, 'regular' as table_type
        FROM pg_tables
        WHERE tablename ILIKE '%{search_text}%'
        AND schemaname NOT IN ('information_schema', 'pg_catalog')
        """

        # Search external tables (SVV_EXTERNAL_TABLES has no tableowner column, use NULL)
        external_tables_query = f"""
        SELECT schemaname, tablename, NULL as tableowner, 'external' as table_type
        FROM SVV_EXTERNAL_TABLES
        WHERE tablename ILIKE '%{search_text}%'
        """

        # Merge queries
        query = f"""
        {regular_tables_query}
        UNION ALL
        {external_tables_query}
        ORDER BY schemaname, tablename
        """

        try:
            results = self._execute_query(query)
            return results
        except Exception as e:
            raise Exception(f"Failed to search Redshift tables: {str(e)}") from e

    def get_external_tables(
        self, schema_name: str | None = None
    ) -> list[dict[str, Any]]:
        """Specifically get external table information"""
        if schema_name:
            query = f"""
            SELECT schemaname, tablename, NULL as tableowner, location
            FROM SVV_EXTERNAL_TABLES
            WHERE schemaname = '{schema_name}'
            ORDER BY tablename
            """
        else:
            query = """
            SELECT schemaname, tablename, NULL as tableowner, location
            FROM SVV_EXTERNAL_TABLES
            ORDER BY schemaname, tablename
            """

        try:
            results = self._execute_query(query)
            return results
        except Exception as e:
            raise Exception(
                f"Failed to get Redshift external table information: {str(e)}"
            ) from e

    def get_statistics(self) -> dict[str, Any]:
        """Get Redshift statistics"""
        try:
            schemas = self.get_schemas()
            total_tables = sum(schema.get("table_count", 0) for schema in schemas)

            # Get external table statistics
            external_tables = self.get_external_tables()
            total_external_tables = len(external_tables)

            return {
                "total_schemas": len(schemas),
                "total_tables": total_tables,
                "total_external_tables": total_external_tables,
                "schema_details": schemas,
                "connection_type": (
                    "Direct connection" if not self._check_config() else "Mock data"
                ),
            }

        except Exception as e:
            raise Exception(f"Failed to get Redshift statistics: {str(e)}") from e

    def test_connection(self) -> dict[str, Any]:
        """Test connection"""
        try:
            missing_configs = self._check_config()
            if missing_configs:
                return {
                    "status": "warning",
                    "message": f'Missing configuration, using mock data: {", ".join(missing_configs)}',
                    "connection_type": "mock",
                }

            # Try simple query
            self._execute_query("SELECT 1 as test")

            return {
                "status": "success",
                "message": "Redshift connection successful",
                "connection_type": "direct",
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Connection failed: {str(e)}",
                "connection_type": "failed",
            }


# Create global instance
redshift_connector = RedshiftConnector()
