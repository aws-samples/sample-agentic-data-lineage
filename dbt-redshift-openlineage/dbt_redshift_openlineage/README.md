# DBT Redshift OpenLineage - dbt Project

This is the core dbt part of the dbt-redshift-openlineage project, containing data models and transformation logic.

## Quick Start

### Environment Setup

Make sure you have set up the parent project environment first:

```bash
# From the parent directory (dbt-redshift-openlineage/)
cd ..

# Install dependencies
uv venv --python 3.13.0
source .venv/bin/activate
uv sync --active

# Return to dbt project
cd dbt_redshift_openlineage
```

## Project Structure

```
dbt_redshift_openlineage/
├── models/
│   ├── staging/           # data staging layer
│   │   ├── stg_customers.sql
│   │   ├── stg_orders.sql
│   │   └── stg_payments.sql
│   └── mart/              # data mart layer
│       ├── customers.sql
│       └── orders.sql
├── dist/                  # colibri output
│   └── colibri-manifest.json
├── dbt_project.yml        # project configuration
└── profiles.yml           # database connection
```

## Data Models

### Staging Layer (staging/)

**stg_customers**
- Source: `spectrum_iceberg_db.jaffle_shop.customers`
- Function: Customer basic information cleaning

**stg_orders**
- Source: `spectrum_iceberg_db.jaffle_shop.orders`
- Function: Order basic information cleaning

**stg_payments**
- Source: `spectrum_iceberg_db.jaffle_shop.payments`
- Function: Payment basic information cleaning

### Mart Layer (mart/)

**customers**
- Dependencies: `stg_customers`, `stg_orders`, `stg_payments`
- Function: Customer dimension table with customer statistics
- Fields: customer_id, first_name, last_name, first_order, most_recent_order, number_of_orders, total_order_amount

**orders**
- Dependencies: `stg_orders`, `stg_payments`
- Function: Order fact table with order and payment information
- Fields: order_id, customer_id, order_date, status, payment_method, amount

### Database Configuration

Ensure your `profiles.yml` is configured with your Redshift connection details:

```yaml
dbt_redshift_openlineage:
  target: dev
  outputs:
    dev:
      type: redshift
      host: "{{ env_var('REDSHIFT_HOST') }}"
      user: "{{ env_var('REDSHIFT_USER') }}"
      password: "{{ env_var('REDSHIFT_PASSWORD') }}"
      port: 5439
      dbname: "{{ env_var('REDSHIFT_DATABASE', 'dev') }}"
      schema: "{{ env_var('REDSHIFT_SCHEMA', 'dbt_dev') }}"
```

## Usage

### Basic Commands

```bash
# Run all models
dbt run

# Run specific model
dbt run --select customers

# Run tests
dbt test

# Generate documentation
dbt docs generate
dbt docs serve
```

### Lineage Data Generation

```bash
# Generate colibri lineage data
dbt run-operation colibri_lineage

# Check generated file
ls -la dist/colibri-manifest.json
```

### Model Configuration

All model configurations are in `dbt_project.yml`:

```yaml
models:
  dbt_redshift_openlineage:
    staging:
      +materialized: table
      +schema: staging
    mart:
      +materialized: table
      +schema: mart
```

## Data Lineage

The project uses the dbt-colibri plugin to track column-level lineage relationships:

- **Table-level Lineage**: Automatically tracked through `ref()` and `source()` functions
- **Column-level Lineage**: Automatically generated through SQL parsing
- **Transformation Logic**: Records detailed SQL transformation information

## Development Guide

### Adding New Models

1. Create `.sql` files in the appropriate directory
2. Use `{{ ref('model_name') }}` to reference other models
3. Use `{{ source('schema', 'table') }}` to reference source tables
4. Add appropriate configuration and documentation

### Best Practices

- Staging layer only does basic cleaning, no business logic
- Mart layer implements business logic and aggregation
- Use meaningful field names and comments
- Add tests for important fields

## Related Resources

- [dbt Documentation](https://docs.getdbt.com/)
- [dbt-colibri Plugin](https://github.com/DataEngineering-LATAM/dbt-colibri)
- [Main Project README](../README.md)
