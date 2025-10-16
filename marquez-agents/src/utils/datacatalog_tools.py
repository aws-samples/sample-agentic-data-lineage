"""
Data Catalog Tools Collection
Wrap Glue and Redshift connectors as Strands tools
"""

from strands import tool

from .glue_connector import glue_connector
from .redshift_connector import redshift_connector


# AWS Glue Tools
@tool
def get_glue_databases() -> str:
    """Get AWS Glue database list"""
    try:
        databases = glue_connector.get_databases()
        return f"AWS Glue databases ({len(databases)} total): {', '.join(databases)}"
    except Exception as e:
        return f"Failed to get Glue databases: {str(e)}"


@tool
def get_glue_database_details() -> str:
    """Get AWS Glue database detailed information"""
    try:
        databases = glue_connector.get_database_details()
        result = "AWS Glue database details:\n"
        for db in databases:
            result += f"- {db['name']}: {db.get('description', 'No description')}\n"
        return result
    except Exception as e:
        return f"Failed to get Glue database details: {str(e)}"


@tool
def get_glue_tables(database_name: str = None) -> str:
    """Get AWS Glue table information"""
    try:
        tables = glue_connector.get_tables(database_name)

        if len(tables) > 500:
            return f"Too many query results ({len(tables)} tables), recommend specifying a specific database name for query"

        if database_name:
            result = f"Tables in database {database_name} ({len(tables)} total):\n"
        else:
            result = f"All AWS Glue tables ({len(tables)} total):\n"

        for table in tables[:100]:  # Limit to first 100
            result += f"- {table['database']}.{table['name']} (location: {table['location'][:50]}...)\n"

        if len(tables) > 100:
            result += f"... {len(tables) - 100} more tables not displayed"

        return result
    except Exception as e:
        return f"Failed to get Glue table information: {str(e)}"


@tool
def get_glue_table_details(database_name: str, table_name: str) -> str:
    """Get AWS Glue table detailed information"""
    try:
        table_info = glue_connector.get_table_details(database_name, table_name)

        result = f"Table {database_name}.{table_name} details:\n"
        result += f"- Type: {table_info['table_type']}\n"
        result += f"- Location: {table_info['location']}\n"
        result += f"- Input format: {table_info['input_format']}\n"
        result += f"- Output format: {table_info['output_format']}\n"
        result += f"- Column count: {len(table_info['columns'])}\n"

        if table_info["columns"]:
            result += "- Column information:\n"
            for col in table_info["columns"][:20]:  # Limit to first 20 columns
                result += f"  * {col['name']} ({col['type']})\n"

            if len(table_info["columns"]) > 20:
                result += f"  ... {len(table_info['columns']) - 20} more columns not displayed\n"

        if table_info["partition_keys"]:
            result += "- Partition keys:\n"
            for pk in table_info["partition_keys"]:
                result += f"  * {pk['name']} ({pk['type']})\n"

        return result
    except Exception as e:
        return f"Failed to get table details: {str(e)}"


@tool
def search_glue_tables(search_text: str) -> str:
    """Search AWS Glue tables"""
    try:
        tables = glue_connector.search_tables(search_text)

        if not tables:
            return f"No tables found containing '{search_text}'"

        result = f"Search '{search_text}' found {len(tables)} tables:\n"
        for table in tables[:50]:  # Limit to first 50
            result += f"- {table['database']}.{table['name']}\n"

        if len(tables) > 50:
            result += f"... {len(tables) - 50} more tables not displayed"

        return result
    except Exception as e:
        return f"Failed to search tables: {str(e)}"


@tool
def get_glue_statistics() -> str:
    """Get AWS Glue statistics"""
    try:
        stats = glue_connector.get_statistics()

        result = "AWS Glue data catalog statistics:\n"
        result += f"- Total databases: {stats['total_databases']}\n"
        result += f"- Total tables: {stats['total_tables']}\n"
        result += "- Database details:\n"

        for db_stat in stats["database_details"]:
            if "error" in db_stat:
                result += f"  * {db_stat['database']}: {db_stat['error']}\n"
            else:
                result += (
                    f"  * {db_stat['database']}: {db_stat['table_count']} tables\n"
                )

        return result
    except Exception as e:
        return f"Failed to get Glue statistics: {str(e)}"


# Redshift Tools
@tool
def get_redshift_schemas() -> str:
    """Get Redshift schema information"""
    try:
        schemas = redshift_connector.get_schemas()

        result = f"Redshift database schemas ({len(schemas)} total):\n"
        for schema in schemas:
            result += (
                f"- {schema['schemaname']}: {schema.get('table_count', 0)} tables\n"
            )

        return result
    except Exception as e:
        return f"Failed to get Redshift schemas: {str(e)}"


@tool
def get_redshift_tables(schema_name: str = None) -> str:
    """Get Redshift table information"""
    try:
        tables = redshift_connector.get_tables(schema_name)

        if len(tables) > 500:
            return f"Too many query results ({len(tables)} tables), recommend specifying a specific schema name for query"

        if schema_name:
            result = f"Tables in schema {schema_name} ({len(tables)} total):\n"
        else:
            result = f"All Redshift tables ({len(tables)} total):\n"

        for table in tables[:100]:  # Limit to first 100
            table_type = table.get("table_type", "unknown")
            type_indicator = (
                "📊"
                if table_type == "regular"
                else "🔗" if table_type == "external" else "❓"
            )
            result += f"- {type_indicator} {table['schemaname']}.{table['tablename']} (owner: {table['tableowner']}, type: {table_type})\n"

        if len(tables) > 100:
            result += f"... {len(tables) - 100} more tables not displayed"

        return result
    except Exception as e:
        return f"Failed to get Redshift table information: {str(e)}"


@tool
def get_redshift_table_columns(schema_name: str, table_name: str) -> str:
    """Get Redshift table column information"""
    try:
        columns = redshift_connector.get_table_columns(schema_name, table_name)

        result = f"Column information for table {schema_name}.{table_name} ({len(columns)} columns):\n"
        for col in columns:
            nullable = "nullable" if col.get("is_nullable") == "YES" else "not null"
            result += f"- {col['column_name']} ({col['data_type']}) - {nullable}\n"

        return result
    except Exception as e:
        return f"Failed to get table column information: {str(e)}"


@tool
def search_redshift_tables(search_text: str) -> str:
    """Search Redshift tables"""
    try:
        tables = redshift_connector.search_tables(search_text)

        if not tables:
            return f"No tables found containing '{search_text}'"

        result = f"Search '{search_text}' found {len(tables)} tables:\n"
        for table in tables[:50]:  # Limit to first 50
            table_type = table.get("table_type", "unknown")
            type_indicator = (
                "📊"
                if table_type == "regular"
                else "🔗" if table_type == "external" else "❓"
            )
            result += f"- {type_indicator} {table['schemaname']}.{table['tablename']} (type: {table_type})\n"

        if len(tables) > 50:
            result += f"... {len(tables) - 50} more tables not displayed"

        return result
    except Exception as e:
        return f"Failed to search tables: {str(e)}"


@tool
def get_redshift_external_tables(schema_name: str = None) -> str:
    """Get Redshift external table information"""
    try:
        external_tables = redshift_connector.get_external_tables(schema_name)

        if len(external_tables) > 500:
            return f"Too many query results ({len(external_tables)} external tables), recommend specifying a specific schema name for query"

        if schema_name:
            result = f"External tables in schema {schema_name} ({len(external_tables)} total):\n"
        else:
            result = f"All Redshift external tables ({len(external_tables)} total):\n"

        for table in external_tables[:100]:  # Limit to first 100
            location = table.get("location", "N/A")
            result += f"- 🔗 {table['schemaname']}.{table['tablename']} (owner: {table['tableowner']}, location: {location})\n"

        if len(external_tables) > 100:
            result += (
                f"... {len(external_tables) - 100} more external tables not displayed"
            )

        return result
    except Exception as e:
        return f"Failed to get Redshift external table information: {str(e)}"


@tool
def get_redshift_statistics() -> str:
    """Get Redshift statistics"""
    try:
        stats = redshift_connector.get_statistics()

        result = "Redshift database statistics:\n"
        result += f"- Total schemas: {stats['total_schemas']}\n"
        result += f"- Total tables: {stats['total_tables']}\n"
        result += f"- External tables: {stats.get('total_external_tables', 0)}\n"
        result += f"- Connection type: {stats['connection_type']}\n"
        result += "- Schema details:\n"

        for schema_stat in stats["schema_details"]:
            result += f"  * {schema_stat['schemaname']}: {schema_stat.get('table_count', 0)} tables\n"

        return result
    except Exception as e:
        return f"Failed to get Redshift statistics: {str(e)}"


@tool
def test_redshift_connection() -> str:
    """Test Redshift connection"""
    try:
        result = redshift_connector.test_connection()

        status_emoji = {"success": "✅", "warning": "⚠️", "error": "❌"}

        emoji = status_emoji.get(result["status"], "❓")
        return f"{emoji} {result['message']} (type: {result['connection_type']})"

    except Exception as e:
        return f"❌ Connection test failed: {str(e)}"


# Export all tools
GLUE_TOOLS = [
    get_glue_databases,
    get_glue_database_details,
    get_glue_tables,
    get_glue_table_details,
    search_glue_tables,
    get_glue_statistics,
]

REDSHIFT_TOOLS = [
    get_redshift_schemas,
    get_redshift_tables,
    get_redshift_external_tables,
    get_redshift_table_columns,
    search_redshift_tables,
    get_redshift_statistics,
    test_redshift_connection,
]

DATACATALOG_TOOLS = GLUE_TOOLS + REDSHIFT_TOOLS
