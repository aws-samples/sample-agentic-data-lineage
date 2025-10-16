# Glue OpenLineage Integration

This project provides integration between AWS Glue and OpenLineage for data lineage tracking. It primarily simulates ETL jobs on AWS Glue, where Glue jobs need to be triggered manually. Automatic scheduling is not part of this POC scope, so scheduling integration is not included.

## Features

- **AWS Glue Integration**: Extract metadata and lineage information from AWS Glue Data Catalog
- **OpenLineage Compliance**: Generate OpenLineage-compliant events for data lineage tracking
- **Automated Processing**: Batch processing of Glue jobs and datasets
- **Flexible Configuration**: Support for multiple environments and configurations

## Quick Start

### 1. Environment Setup

```bash
# Install Python dependencies
pip install -e .

# Or use uv
uv venv --python 3.14.0
source .venv/bin/activate
uv sync --active
```

### 2. Configuration

Configure your AWS credentials and environment variables:

```bash
# AWS Configuration
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-west-2

# Glue Configuration
export GLUE_DATABASE=your_glue_database
export GLUE_REGION=us-west-2
```

### 3. Usage

```bash
# Process Glue metadata
python process_glue_lineage.py

# Generate OpenLineage events
python generate_openlineage_events.py
```

## Project Structure

```
glue-openlineage/
├── inputs/                    # Input data and configurations
├── iac-612674025488-us-west-2/  # Infrastructure as Code
├── src/                       # Source code (if applicable)
├── pyproject.toml            # Python project configuration
└── README.md                 # This file
```

## Development

The project uses Python 3.13+ and uv as package manager.

```bash
# Activate virtual environment
source .venv/bin/activate

# Install development dependencies
uv sync --active --dev

# Run tests
pytest
```

## License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file in the root directory for details.
