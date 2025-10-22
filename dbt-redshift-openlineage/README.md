# DBT Redshift OpenLineage Integration

This project demonstrates how to integrate dbt with Redshift and OpenLineage/Marquez to achieve comprehensive data lineage tracking and visualization with column-level granularity.

## Data Attribution

This project uses sample data models and schema structure inspired by the [dbt-labs/jaffle-shop-classic](https://github.com/dbt-labs/jaffle-shop-classic) project, which is licensed under the Apache License 2.0. The jaffle-shop dataset provides a realistic e-commerce data structure for demonstrating data transformation and lineage tracking capabilities.

## Project Structure

```
dbt-redshift-openlineage/
├── dbt_redshift_openlineage/          # dbt project
│   ├── models/                        # dbt models
│   │   ├── staging/                   # data staging layer
│   │   └── mart/                      # data mart layer
│   ├── dist/                          # colibri generated manifest
│   │   └── colibri-manifest.json      # lineage data file
│   ├── dbt_project.yml               # dbt project configuration
│   └── profiles.yml                   # database connection configuration
├── marquez_lineage/                   # lineage sync module
│   ├── marquez_config.yaml            # Marquez configuration
│   └── marquez_lineage_sync.py        # lineage sync script
├── run_dbt_with_sync.sh              # automated run script
└── pyproject.toml                     # Python dependencies configuration
```

## Features

- **dbt Data Transformation**: Use dbt for data modeling and transformation
- **Column-level Lineage Tracking**: Generate detailed column-level lineage relationships through dbt-colibri plugin
- **OpenLineage Integration**: Convert lineage data to OpenLineage standard format with full schema support
- **Marquez Visualization**: Visualize data lineage graphs in Marquez with proper source categorization
- **Automated Workflow**: One-click execution of dbt and lineage data synchronization
- **Smart Column Mapping**: Intelligent inference of column relationships from SQL transformations
- **Configurable Sources**: Flexible source naming and categorization in Marquez
- **Dataset Management**: Built-in dataset creation and deletion capabilities

## Quick Start

### 1. Environment Setup

```bash
# Install Python dependencies
pip install -e .

# Or use uv
uv venv --python 3.13.0
source .venv/bin/activate
uv sync --active
```

### 2. Configure Database Connection

Edit `dbt_redshift_openlineage/profiles.yml`:

```yaml
dbt_redshift_openlineage:
  target: dev
  outputs:
    dev:
      type: redshift
      host: your-redshift-cluster.region.redshift.amazonaws.com
      user: your-username
      password: your-password
      port: 5439
      dbname: your-database
      schema: your-schema
      threads: 1
      connect_timeout: 300
      keepalives_idle: 0
```

### 3. Configure Marquez Connection

Edit `marquez_lineage/marquez_config.yaml`:

```yaml
marquez:
  url: "http://your-marquez-server.com"

openlineage:
  producer: "dbt_redshift_openlineage_converter"
  root_namespace: "s3://your-data-bucket"
```

### 4. Run the Project

#### Option 1: Automated Run (Recommended)

```bash
# Run dbt and automatically sync lineage data to Marquez
./run_dbt_with_sync.sh
```

#### Option 2: Step-by-step Run

```bash
# 1. Run dbt
cd dbt_redshift_openlineage
dbt run

# 2. Sync lineage data
cd ../marquez_lineage
python3 marquez_lineage_sync.py
```

## Core Components

### dbt-colibri

Use the [dbt-colibri](https://github.com/DataEngineering-LATAM/dbt-colibri) plugin to generate column-level lineage data:

```bash
# Generate lineage data
cd dbt_redshift_openlineage
dbt run-operation colibri_lineage
```

### Lineage Sync Script

`marquez_lineage_sync.py` script features:

- **Advanced Column Lineage Inference**: Comprehensive SQL pattern matching to identify complex column dependencies including:
  - Direct column aliasing (`source_col as target_col`)
  - Function transformations (`func(source_col) as target_col`)
  - Arithmetic operations (`source_col / 100 as target_col`)
  - Complex CASE WHEN expressions with multiple source dependencies
  - Aggregation functions with conditional logic (`sum(case when payment_method = 'coupon' then amount else 0 end)`)
- **Multi-Column Dependency Detection**: Accurately identifies fields that depend on multiple source columns (e.g., `coupon_amount` depends on both `payment_method` and `amount`)
- **OpenLineage Compliance**: Convert to OpenLineage standard format with proper schema URLs and facets
- **Source Management**: Automatically create and manage data sources in Marquez with proper categorization
- **Transformation Type Classification**: Intelligent detection of transformation types (IDENTITY, AGGREGATION, CONDITIONAL, ARITHMETIC, FUNCTION)
- **Flexible Operations**: Support single model or batch synchronization with comprehensive error handling

```bash
# Sync all models
python3 marquez_lineage_sync.py

# Sync single model
python3 marquez_lineage_sync.py --model stg_customers

# Preview mode (do not send to Marquez)
python3 marquez_lineage_sync.py --dry-run --model stg_customers

# Custom configuration
python3 marquez_lineage_sync.py --marquez-url "http://custom-marquez.com" --model orders

# Dataset management
python3 marquez_lineage_sync.py --delete-dataset "dataset_name" --delete-namespace "namespace"
```

## Data Models

### Staging Layer

- `stg_customers`: Customer basic information
- `stg_orders`: Order basic information
- `stg_payments`: Payment basic information

### Mart Layer

- `customers`: Customer dimension table with customer statistics
- `orders`: Order fact table with order and payment information

## Lineage Tracking

The project supports comprehensive lineage relationship tracking with advanced column-level analysis:

### 1. Table-level Lineage
Dependencies between models and their source tables

### 2. Advanced Column-level Lineage
Field-level data flow with intelligent dependency detection:

#### Simple Column Mapping
```sql
-- Direct aliasing: id -> customer_id
select id as customer_id from source
```

#### Function Transformations
```sql
-- Function with aliasing: amount -> converted_amount
select amount / 100 as converted_amount from source
```

#### Complex Multi-Column Dependencies
```sql
-- CASE WHEN with multiple dependencies: payment_method + amount -> coupon_amount
sum(case when payment_method = 'coupon' then amount else 0 end) as coupon_amount
```

**Result**: `coupon_amount` correctly shows dependencies on both:
- `payment_method` (for condition evaluation)
- `amount` (for value calculation)

#### Supported SQL Patterns
- **Direct aliasing**: `source_col as target_col`
- **Function calls**: `func(source_col) as target_col`
- **Arithmetic operations**: `source_col / 100 as target_col`
- **CASE WHEN expressions**: `case when condition_col = 'value' then value_col else 0 end`
- **Aggregation with conditions**: `sum(case when payment_method = 'coupon' then amount else 0 end)`

### 3. Transformation Type Classification
Automatic detection of transformation patterns:
- **IDENTITY**: Direct column mapping
- **AGGREGATION**: SUM, COUNT, AVG, MIN, MAX functions
- **CONDITIONAL**: CASE WHEN expressions
- **ARITHMETIC**: Mathematical operations
- **FUNCTION**: Function transformations

### 4. Data Sources
External data source lineage relationships with proper source categorization

## Configuration

### marquez_config.yaml

```yaml
# Marquez server configuration
marquez:
  url: "http://marquez-web.kolya.fun"

# File path configuration
paths:
  manifest: "../dbt_redshift_openlineage/dist/colibri-manifest.json"

# OpenLineage configuration
openlineage:
  producer: "dbt_redshift_openlineage_converter"
  root_namespace: "s3://lh-core-kolya-landing-zone"
  source_name: "dbt-redshift"  # Configurable source name for dataset categorization

# Logging configuration
logging:
  level: "INFO"
```

### Environment Variables

The script also supports environment variables for sensitive configuration:

```bash
# Redshift connection (used for source creation)
export REDSHIFT_HOST="your-redshift-cluster.region.redshift.amazonaws.com"
export REDSHIFT_USER="your_username"
export REDSHIFT_PASSWORD="your_password"
export REDSHIFT_DATABASE="your_database"
export REDSHIFT_SCHEMA="your_schema"
```

## Troubleshooting

### Common Issues

1. **Manifest file does not exist**
   ```bash
   # Ensure colibri command has been run
   cd dbt_redshift_openlineage
   dbt run-operation colibri_lineage
   ```

2. **Marquez connection failed**
   ```bash
   # Check if Marquez service is running
   curl http://your-marquez-server.com/api/v1/namespaces
   ```

3. **Permission issues**
   ```bash
   # Ensure script has execute permissions
   chmod +x run_dbt_with_sync.sh
   ```

## Development Guide

### Adding New Models

1. Create new SQL files under `dbt_redshift_openlineage/models/`
2. Run `dbt run` to execute the model
3. Run `dbt run-operation colibri_lineage` to generate lineage data
4. Run lineage sync script to update Marquez

### Customizing Lineage Logic

The enhanced `marquez_lineage_sync.py` provides several advanced customization points:

- **`load_config()`**: Custom configuration loading logic
- **`_infer_source_column()`**: Comprehensive SQL pattern matching for single-column inference
- **`_infer_column_dependencies()`**: Multi-column dependency detection for complex expressions
- **`_find_source_tables_for_columns()`**: Intelligent source table resolution based on manifest dependencies
- **`_determine_transformation_type()`**: Automatic classification of transformation patterns
- **`build_column_lineage()`**: Advanced column-level lineage relationship building with fallback mechanisms
- **`create_openlineage_event()`**: OpenLineage event format customization
- **`create_source()`**: Data source creation with Redshift connection details

### Key Improvements in Current Version

- **Enhanced Column Lineage Accuracy**: Comprehensive pattern matching eliminates hardcoded mappings and accurately identifies complex dependencies
- **Multi-Column Dependency Support**: Correctly handles fields like `coupon_amount` that depend on multiple source columns (`payment_method` + `amount`)
- **Robust SQL Analysis**: Advanced regex patterns handle various SQL constructs including CASE WHEN, aggregations, and arithmetic operations
- **Transformation Type Detection**: Automatic classification of transformation patterns (AGGREGATION, CONDITIONAL, ARITHMETIC, FUNCTION, IDENTITY)
- **Fallback Mechanisms**: Multiple inference strategies ensure maximum lineage coverage
- **Comprehensive Error Handling**: Detailed logging and graceful degradation when lineage cannot be determined
- **Flexible Configuration**: Support for both configuration files and command-line overrides
- **Better Source Management**: Automatic creation of properly configured data sources in Marquez

## Related Resources

- [dbt Documentation](https://docs.getdbt.com/)
- [dbt-colibri Plugin](https://github.com/DataEngineering-LATAM/dbt-colibri)
- [OpenLineage Specification](https://openlineage.io/)
- [Marquez Documentation](https://marquezproject.github.io/marquez/)
- [Redshift Documentation](https://docs.aws.amazon.com/redshift/)

## Acknowledgments

- Sample data models and schema structure inspired by [dbt-labs/jaffle-shop-classic](https://github.com/dbt-labs/jaffle-shop-classic)
- dbt-colibri plugin by [DataEngineering-LATAM](https://github.com/DataEngineering-LATAM/dbt-colibri)

## License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file in the root directory for details.

**Third-party Attribution:**
- This project uses concepts and data structure patterns from the jaffle-shop-classic project (Apache License 2.0)
- No direct code copying; only conceptual inspiration for data modeling patterns
