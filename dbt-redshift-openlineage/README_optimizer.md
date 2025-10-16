# Marquez Lineage Data Optimization Tool

This tool can optimize lineage JSON data returned by Marquez API, removing redundant fields and keeping only core information, thereby significantly reducing token count.

## Features

- **Significant Compression**: Usually reduces data volume by 60-70%
- **Preserve Core Information**: Only keeps key fields for datasets, jobs, and edge relationships
- **Remove Redundancy**: Removes timestamps, descriptions, facets and other redundant fields
- **Multiple Usage Methods**: Supports URL, file, and pipeline input

## Usage

### 1. Direct API Fetch and Optimization
```bash
python marquez_optimizer.py "http://marquez.example.com/api/v1/lineage?nodeId=dataset:s3://[BUCKET_NAME]:icebergs/iceberg_db/customers&depth=0"
```

### 2. Pipeline Processing
```bash
curl -L -X GET 'http://marquez.example.com/api/v1/lineage?nodeId=dataset:s3://[BUCKET_NAME]:icebergs/iceberg_db/customers&depth=0' \
  -H 'Accept: application/json' | python marquez_optimizer.py
```

### 3. Read from File
```bash
python marquez_optimizer.py lineage_data.json
```

## Output Format

Optimized JSON structure:

```json
{
  "datasets": [
    {
      "id": "dataset:s3://bucket:path/to/data",
      "name": "path/to/data",
      "fields": ["field1", "field2", "field3"]
    }
  ],
  "jobs": [
    {
      "id": "job:namespace:job_name",
      "name": "simplified_job_name",
      "inputs": ["namespace:input_dataset"],
      "outputs": ["namespace:output_dataset"],
      "state": "COMPLETED"
    }
  ],
  "edges": [
    {
      "from": "source_node_id",
      "to": "destination_node_id"
    }
  ]
}
```

## Optimization Results

- **Original Data**: ~4200 characters
- **Optimized**: ~1250 characters
- **Compression Ratio**: About 70% reduction

## Dependencies

- Python 3.6+
- requests (only needed when directly calling API)

```bash
pip install requests
```

## How It Works

The tool optimizes data through the following methods:

1. **Remove Timestamps**: createdAt, updatedAt, startedAt, endedAt, etc.
2. **Remove Descriptions**: description, tags, etc.
3. **Remove Facets**: Complex metadata objects
4. **Simplify Field Information**: Only keep field names, remove types and descriptions
5. **Deduplicate Edge Relationships**: Avoid duplicate lineage relationships
6. **Simplify Job Information**: Only keep core inputs, outputs, and state

This significantly reduces token count, improves LLM processing efficiency, while preserving core information needed for lineage analysis.
