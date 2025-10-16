# Lakehouse Core

Data lakehouse integration core project

## Project Structure

```
├── iac-[ACCOUNT_ID]-us-west-2/  # AWS Infrastructure code (Terraform)
├── script/                      # Script files
├── test/                       # Test files and configuration
├── pyproject.toml              # Python project configuration
└── README.md                   # Project documentation
```

## Quick Start

### Environment Setup

```bash
# Install Python dependencies
uv venv --python 3.13.0
source .venv/bin/activate
uv sync --active

# Install pre-commit hooks
pre-commit install
```

### Infrastructure Deployment

```bash
# Enter Terraform directory
cd iac-[ACCOUNT_ID]-us-west-2/

# Generate terraform.tfvars from current AWS profile
./generate_tfvars.sh

# Initialize Terraform
terraform init

# View plan
terraform plan

# Deploy
terraform apply
```

**Alternative**: Manually create `terraform.tfvars` from the example:
```bash
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your AWS account and region
```

### Testing

```bash
# Deploy test Pod
kubectl apply -f test/test-pod.yaml

# Enter test environment
kubectl exec -it test-pod -- /bin/bash

# Copy files to Pod
kubectl cp ./your-file.txt test-pod:/tmp/
```

## Development

The project uses Python 3.13+ and uv as package manager.

```bash
# Activate virtual environment
source .venv/bin/activate

# Run pre-commit checks
pre-commit run --all-files
```

## Components

- **Marquez**: Data lineage tracking
- **Karpenter**: Kubernetes node auto-scaling
- **Test Environment**: Kubernetes Pod-based testing environment

## License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file in the root directory for details.
