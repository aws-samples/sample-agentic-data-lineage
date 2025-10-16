# Iceberg to Redshift Lineage Converter

This tool maps Iceberg tables from AWS Glue to Amazon Redshift external tables and establishes complete data lineage relationships. The tool requires manual triggering for execution. In production environments, this process can be automated using S3 event notifications to trigger AWS Lambda functions for real-time processing.

## Core Features

- 🔄 **Table Mapping**: Map Iceberg tables from Glue Catalog to Redshift external tables
- 🔗 **Lineage Tracking**: Establish complete lineage relationships from source data to target tables
- 📊 **Metadata Synchronization**: Maintain consistency of field structures and types
- 🛡️ **Direct Access**: Direct connection to Redshift clusters
- 🚀 **Manual Execution**: Requires manual triggering (can be automated via S3 notifications + Lambda in production)

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

### 2. Environment Configuration
Create `.env` file:

```bash
# Redshift connection configuration
REDSHIFT_HOST=your-redshift-cluster.region.redshift.amazonaws.com
REDSHIFT_PORT=5439
REDSHIFT_DATABASE=your_database
REDSHIFT_USERNAME=your_username
REDSHIFT_PASSWORD=your_password

# Marquez configuration
MARQUEZ_URL=""             # e.g. http://your-marquez-server:5000
MARQUEZ_API_KEY=""         # Optional
```

### 3. Configuration File

Create `config.yaml` configuration file:

```yaml
# Glue database configuration file
# List the Glue databases to be processed

databases:
  - demo_db
  - iceberg_db
  - data_lake_db

# Redshift configuration
redshift_schema: spectrum_iceberg_db
```

### 4. Manual Execution

**Note**: This tool requires manual triggering. For production automation, consider using S3 event notifications to trigger AWS Lambda functions.

```bash
# Use default configuration file (config.yaml)
python3 glue_redshift_lineage_converter.py \
  --iam-role arn:aws:iam::[ACCOUNT_ID]:role/glue-openlineage-redshift-spectrum-role \
  --marquez-url http://marquez.example.com

# Use custom configuration file
python3 glue_redshift_lineage_converter.py \
  --config my_config.yaml \
  --iam-role arn:aws:iam::123456789012:role/MyRole

# Override redshift-schema in configuration file
python3 glue_redshift_lineage_converter.py \
  --redshift-schema my_custom_schema \
  --iam-role arn:aws:iam::123456789012:role/MyRole \
  --marquez-url http://marquez.example.com
```

### Production Automation (Optional)

For automated execution in production environments:

1. **S3 Event Notifications**: Configure S3 bucket to send notifications when new Iceberg tables are created
2. **AWS Lambda**: Create Lambda function to execute the converter script
3. **IAM Roles**: Ensure proper permissions for Lambda to access Glue, Redshift, and S3
4. **Event Filtering**: Use S3 event filters to trigger only on relevant table creation events

## Mapping Logic

### Data Source Mapping
```
AWS Glue Table → Redshift External Table
s3://bucket/warehouse/db/table → redshift.schema.table
```

### Lineage Relationships
- **Namespace**: Extract bucket name from S3 location (`s3://bucket-name`)
- **Dataset**: Extract path after bucket (`warehouse/db/table`)
- **Field Mapping**: 1:1 direct mapping, preserving types and comments

---

# Marquez Job Manager

Tool for cleaning and managing duplicate jobs in Marquez, supporting intelligent grouping based on datasets.

## Core Features

- 🎯 **Smart Grouping**: Group by dataset or job name prefix
- 🧹 **Intelligent Cleanup**: Keep only the latest jobs for each dataset/node
- 🔒 **Safe Mode**: Support dry-run mode to preview results
- 📊 **Statistical Analysis**: Provide detailed job and dataset statistics

## Grouping Strategies

### 🎯 Dataset-based Grouping (Recommended)
Data-centric approach, identifying duplicate jobs processing the same dataset:

```
Dataset: s3://bucket::path/to/data
├── 🟢 latest_job (2025-09-07T12:01:22Z) ← Keep
├── 🔴 old_job_v2 (2025-09-07T11:55:23Z) ← Delete
└── 🔴 old_job_v1 (2025-09-07T11:55:17Z) ← Delete
```

**Advantages**: More accurate duplicate identification, maintains lineage integrity

### 🔧 Node-based Grouping (Compatible)
Identify different versions of the same process based on job name prefix:
- `job_name_v1`, `job_name_v2` → `namespace::job_name`
- `nativespark_xxx_jr_hash` → `namespace::nativespark_xxx`

## Quick Usage

```bash
# View statistics
python marquez_job_manager.py --marquez-url http://localhost:5000 --action stats

# Dry-run cleanup (dataset-based, recommended)
python marquez_job_manager.py --marquez-url http://localhost:5000 --action cleanup-jobs --keep-jobs 1 --dry-run

# Execute cleanup
python marquez_job_manager.py --marquez-url http://localhost:5000 --action cleanup-jobs --keep-jobs 1

# Node-based grouping cleanup (compatible mode)
python marquez_job_manager.py --marquez-url http://localhost:5000 --action cleanup-jobs --keep-jobs 1 --group-by-node
```

## Cleanup Effectiveness Comparison

| Grouping Method | Duplicate Detection | Cleanup Precision | Use Case |
|----------------|-------------------|------------------|----------|
| **Dataset-based** | More accurate | Higher | **Recommended: Data-driven** |
| Node-based | Traditional | General | Compatible: Naming convention |

## Python API

```python
from marquez_job_manager import MarquezJobManager

manager = MarquezJobManager("http://localhost:5000")

# Group by dataset (recommended)
dataset_groups = manager.group_jobs_by_dataset(jobs)
result = manager.cleanup_old_jobs(keep_latest_count=1, group_by_dataset=True)

# Group by node (compatible)
node_groups = manager.group_jobs_by_node(jobs)
result = manager.cleanup_old_jobs(keep_latest_count=1, group_by_dataset=False)
```

## License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file in the root directory for details.
