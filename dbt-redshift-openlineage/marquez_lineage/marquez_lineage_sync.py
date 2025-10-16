#!/usr/bin/env python3
"""
Simplified Marquez Column Lineage Sync Script
"""

import json
import logging
import os
import re
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from urllib.parse import quote

import requests
import yaml


def load_config(config_path: str = "marquez_config.yaml") -> Dict[str, Any]:
    """Load configuration from YAML file"""
    try:
        with open(config_path, "r") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        # Fallback to default configuration
        return {
            "marquez": {"url": "http://marquez-web.kolya.fun"},
            "paths": {
                "manifest": "../dbt_redshift_openlineage/dist/colibri-manifest.json"
            },
            "openlineage": {
                "producer": "dbt_redshift_openlineage_converter",
                "root_namespace": "s3://lh-core-kolya-landing-zone",
                "source_name": "dbt-redshift",
            },
            "logging": {"level": "INFO"},
        }


# Load configuration
config = load_config()

# Configuration variables
MARQUEZ_URL = config["marquez"]["url"]
MANIFEST_PATH = config["paths"]["manifest"]
PRODUCER = config["openlineage"]["producer"]
ROOT_NAMESPACE = config["openlineage"]["root_namespace"]
SOURCE_NAME = config["openlineage"]["source_name"]

# Setup logging
log_level = getattr(logging, config["logging"]["level"].upper())
logging.basicConfig(level=log_level)
logger = logging.getLogger(__name__)


class MarquezSync:
    def __init__(self, marquez_url: str = None, manifest_path: str = None):
        self.marquez_url = (marquez_url or MARQUEZ_URL).rstrip("/")
        self.manifest_path = manifest_path or MANIFEST_PATH
        self.manifest = None
        self.session = requests.Session()

    def load_manifest(self) -> Dict[str, Any]:
        """Load the colibri manifest file"""
        with open(self.manifest_path, "r") as f:
            self.manifest = json.load(f)
        logger.info(f"Loaded manifest with {len(self.manifest.get('nodes', {}))} nodes")
        return self.manifest

    def create_source(self, source_name: str) -> bool:
        """Create a data source in Marquez"""
        url = f"{self.marquez_url}/api/v1/sources/{quote(source_name, safe='')}"

        # Get Redshift host from environment
        redshift_host = os.getenv("REDSHIFT_HOST", "redshift-cluster")
        if ":" in redshift_host:
            redshift_host = redshift_host.split(":")[0]

        payload = {
            "type": "REDSHIFT",
            "connectionUrl": f"redshift://{redshift_host}:5439/{source_name}",
            "description": f"{source_name} data source",
        }

        try:
            response = self.session.put(url, json=payload)
            response.raise_for_status()
            logger.info(f"✅ Source created: {source_name}")
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Failed to create source: {e}")
            return False

    def create_dataset(
        self,
        namespace: str,
        dataset_name: str,
        source_name: str,
        fields: List[Dict] = None,
    ) -> bool:
        """Create dataset in Marquez"""
        # Ensure source exists
        if not self.create_source(source_name):
            return False

        url = (
            f"{self.marquez_url}/api/v1/namespaces/{quote(namespace, safe='')}"
            f"/datasets/{quote(dataset_name, safe='')}"
        )

        payload = {
            "type": "DB_TABLE",
            "physicalName": dataset_name,
            "sourceName": source_name,
            "fields": fields or [],
        }

        logger.debug(f"Creating dataset with payload: {payload}")
        logger.debug(f"URL: {url}")

        try:
            response = self.session.put(url, json=payload)
            response.raise_for_status()
            logger.info(f"✅ Dataset created: {dataset_name}")
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Failed to create dataset: {e}")
            if hasattr(e, "response") and e.response is not None:
                logger.error(f"Response content: {e.response.text}")
            return False

    def create_dataset_with_details(
        self,
        namespace: str,
        dataset_name: str,
        physical_name: str,
        source_name: str,
        fields: List[Dict] = None,
        description: str = None,
    ) -> bool:
        """Create dataset with detailed parameters (following backup file logic)"""
        # Ensure source exists
        if not self.create_source(source_name):
            raise ValueError(f"Unable to create data source: {source_name}")

        url = (
            f"{self.marquez_url}/api/v1/namespaces/{quote(namespace, safe='')}"
            f"/datasets/{quote(dataset_name, safe='')}"
        )

        payload = {
            "type": "DB_TABLE",
            "physicalName": physical_name,
            "sourceName": source_name,
        }

        if fields:
            payload["fields"] = fields
        if description:
            payload["description"] = description

        logger.debug(f"Creating dataset with detailed payload: {payload}")
        logger.debug(f"URL: {url}")

        try:
            response = self.session.put(url, json=payload)
            response.raise_for_status()
            logger.info(
                f"✅ Dataset created: {dataset_name} with source: {source_name}"
            )
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Failed to create dataset: {e}")
            if hasattr(e, "response") and e.response is not None:
                logger.error(f"Response content: {e.response.text}")
            raise

    def build_column_lineage(self, target_node_id: str) -> Dict[str, Any]:
        """Build column lineage from manifest edges"""
        column_lineage = {}
        edges = self.manifest.get("lineage", {}).get("edges", [])

        for edge in edges:
            if edge["target"] != target_node_id or not edge.get("targetColumn"):
                continue

            target_column = edge["targetColumn"]
            source_node = edge["source"]
            source_column = edge["sourceColumn"]

            # Get source info
            source_info = self.manifest["nodes"].get(source_node, {})
            source_name = f"{source_info.get('database', '')}.{source_info.get('schema', '')}.{source_info.get('name', '')}"

            # Handle wildcard columns - infer from SQL
            if source_column == "*":
                target_info = self.manifest["nodes"].get(target_node_id, {})
                compiled_code = target_info.get("compiledCode", "")
                source_column = self._infer_source_column(target_column, compiled_code)

            if source_column:
                column_lineage[target_column] = {
                    "inputFields": [
                        {
                            "namespace": ROOT_NAMESPACE,
                            "name": source_name,
                            "field": source_column,
                        }
                    ],
                    "transformationType": "IDENTITY",
                }

        return column_lineage

    def _infer_source_column(
        self, target_column: str, compiled_code: str
    ) -> Optional[str]:
        """Infer source column from SQL code"""
        if not compiled_code:
            return None

        # Pattern: "source_col as target_col"
        pattern = rf"(\w+)\s+as\s+{re.escape(target_column)}\b"
        match = re.search(pattern, compiled_code, re.IGNORECASE)
        if match:
            return match.group(1)

        # Common mappings
        mappings = {"customer_id": "id", "order_id": "id", "payment_id": "id"}
        return mappings.get(target_column, target_column)

    def create_openlineage_event(
        self, node_id: str, node_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create OpenLineage event"""
        if node_info.get("nodeType") == "source":
            return None

        # Build dataset name
        dataset_name = f"{node_info.get('database', '')}.{node_info.get('schema', '')}.{node_info.get('name', '')}"

        # Build column lineage
        column_lineage = self.build_column_lineage(node_id)

        # Create schema fields
        fields = []
        for col_name, col_info in node_info.get("columns", {}).items():
            fields.append(
                {
                    "name": col_name,
                    "type": col_info.get("dataType", "string"),
                    "description": col_info.get("description", ""),
                }
            )

        # Build inputs from lineage edges
        inputs = []
        for edge in self.manifest.get("lineage", {}).get("edges", []):
            if edge["target"] == node_id:
                source_node_id = edge["source"]
                source_info = self.manifest["nodes"].get(source_node_id, {})
                if source_info:
                    source_name = f"{source_info.get('database', '')}.{source_info.get('schema', '')}.{source_info.get('name', '')}"
                    inputs.append(
                        {
                            "namespace": ROOT_NAMESPACE,
                            "name": source_name,
                            "facets": {
                                "schema": {
                                    "_producer": PRODUCER,
                                    "_schemaURL": "https://openlineage.io/spec/facets/1-0-0/SchemaDatasetFacet.json",
                                    "fields": [],
                                }
                            },
                        }
                    )

        # Remove duplicates
        unique_inputs = []
        seen = set()
        for inp in inputs:
            key = inp["name"]
            if key not in seen:
                seen.add(key)
                unique_inputs.append(inp)

        event = {
            "eventType": "COMPLETE",
            "eventTime": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "run": {"runId": str(uuid.uuid4())},
            "job": {
                "namespace": ROOT_NAMESPACE,
                "name": f"dbt_run_{node_info.get('name', 'unknown')}",
                "facets": {},
            },
            "inputs": unique_inputs,
            "outputs": [
                {
                    "namespace": ROOT_NAMESPACE,
                    "name": dataset_name,
                    "facets": {
                        "schema": {
                            "_producer": PRODUCER,
                            "_schemaURL": "https://openlineage.io/spec/facets/1-0-0/SchemaDatasetFacet.json",
                            "fields": fields,
                        }
                    },
                }
            ],
            "producer": PRODUCER,
        }

        # Add column lineage if available
        if column_lineage:
            event["job"]["facets"]["columnLineage"] = {
                "_producer": PRODUCER,
                "_schemaURL": "https://openlineage.io/spec/facets/1-0-0/ColumnLineageJobFacet.json",
                "fields": column_lineage,
            }
            event["outputs"][0]["facets"]["columnLineage"] = {
                "_producer": PRODUCER,
                "_schemaURL": "https://openlineage.io/spec/facets/1-0-0/ColumnLineageDatasetFacet.json",
                "fields": column_lineage,
            }

        return event

    def send_event(self, event: Dict[str, Any]) -> bool:
        """Send OpenLineage event to Marquez"""
        # Pre-create dataset with correct source (following backup file logic)
        try:
            if event.get("outputs") and len(event["outputs"]) > 0:
                output = event["outputs"][0]
                target_namespace = output["namespace"]
                target_dataset = output["name"]
                target_fields = output["facets"]["schema"]["fields"]

                # Parse dataset name to get components
                dataset_parts = target_dataset.split(".")
                if len(dataset_parts) >= 3:
                    redshift_database = dataset_parts[0]
                    redshift_schema = dataset_parts[1]
                    table_name = dataset_parts[2]
                else:
                    redshift_database = "unknown"
                    redshift_schema = "unknown"
                    table_name = target_dataset

                # Convert fields format
                dataset_fields = [
                    {"name": field["name"], "type": field["type"]}
                    for field in target_fields
                ]

                # Create target dataset with dbt-redshift source
                self.create_dataset_with_details(
                    namespace=target_namespace,
                    dataset_name=target_dataset,
                    physical_name=f"{redshift_database}.{redshift_schema}.{table_name}",
                    source_name=SOURCE_NAME,
                    fields=dataset_fields,
                    description=f"dbt model: {redshift_schema}.{table_name}",
                )
        except Exception as e:
            logger.warning(f"Dataset pre-creation warning: {e}")

        # Send event
        try:
            url = f"{self.marquez_url}/api/v1/lineage"
            response = self.session.post(
                url, json=event, headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            logger.info(f"✅ Event sent: {event['job']['name']}")
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Failed to send event: {e}")
            if hasattr(e, "response") and e.response is not None:
                logger.error(f"Response content: {e.response.text}")
            return False

    def sync_model(self, model_name: str = None) -> None:
        """Sync lineage for one or all models"""
        if not self.manifest:
            self.load_manifest()

        nodes = self.manifest.get("nodes", {})
        success_count = 0
        total_count = 0

        for node_id, node_info in nodes.items():
            if node_info.get("nodeType") != "model":
                continue

            if model_name and node_info.get("name") != model_name:
                continue

            total_count += 1
            logger.info(f"Processing: {node_info.get('name')}")

            event = self.create_openlineage_event(node_id, node_info)
            if event and self.send_event(event):
                success_count += 1

        logger.info(f"Sync completed: {success_count}/{total_count} successful")

    def delete_dataset(self, namespace: str, dataset_name: str) -> bool:
        """Delete dataset from Marquez"""
        url = (
            f"{self.marquez_url}/api/v1/namespaces/{quote(namespace, safe='')}"
            f"/datasets/{quote(dataset_name, safe='')}"
        )

        try:
            response = self.session.delete(url)
            response.raise_for_status()
            logger.info(f"✅ Dataset deleted: {dataset_name}")
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Failed to delete dataset: {e}")
            return False


def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description="Sync dbt lineage to Marquez")
    parser.add_argument("--model", help="Sync specific model only")
    parser.add_argument(
        "--manifest", default=MANIFEST_PATH, help="Path to colibri manifest file"
    )
    parser.add_argument("--marquez-url", default=MARQUEZ_URL, help="Marquez URL")
    parser.add_argument(
        "--dry-run", action="store_true", help="Print events without sending"
    )
    parser.add_argument("--delete-dataset", help="Delete dataset name")
    parser.add_argument("--delete-namespace", help="Namespace for deletion")

    args = parser.parse_args()

    syncer = MarquezSync(args.marquez_url, args.manifest)

    # Handle delete
    if args.delete_dataset:
        if not args.delete_namespace:
            logger.error("--delete-namespace required with --delete-dataset")
            return
        syncer.delete_dataset(args.delete_namespace, args.delete_dataset)
        return

    # Handle sync
    try:
        syncer.load_manifest()

        if args.dry_run:
            # Print events without sending
            for node_id, node_info in syncer.manifest.get("nodes", {}).items():
                if node_info.get("nodeType") == "model":
                    if not args.model or node_info.get("name") == args.model:
                        event = syncer.create_openlineage_event(node_id, node_info)
                        if event:
                            print(f"--- Event for {node_info.get('name')} ---")
                            print(json.dumps(event, indent=2))
        else:
            syncer.sync_model(args.model)

    except Exception as e:
        logger.error(f"Sync failed: {e}")
        raise


if __name__ == "__main__":
    main()
