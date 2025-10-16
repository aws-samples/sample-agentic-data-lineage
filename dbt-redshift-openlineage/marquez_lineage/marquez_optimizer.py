#!/usr/bin/env python3
"""
Marquez Lineage Data Optimization Tool

Usage:
1. Direct URL fetch: python marquez_optimizer.py "http://marquez.example.com/api/v1/lineage?..."
2. Pipeline input: curl ... | python marquez_optimizer.py
3. Read from file: python marquez_optimizer.py raw_lineage.json

Function: Remove redundant fields (timestamps, descriptions, facets, etc.), keep only core information of datasets, jobs, and edge relationships
"""

import json
import sys


def simplify_marquez_lineage(data):
    """
    Simplify JSON returned by Marquez Lineage API, keeping only core information
    """
    graph = data.get("graph", [])
    simplified = {"datasets": [], "jobs": [], "edges": []}

    edges_set = set()

    for node in graph:
        node_id = node.get("id")
        node_type = node.get("type")
        node_data = node.get("data", {})

        if node_type == "DATASET":
            dataset = {
                "id": node_id,
                "name": node_data.get("name"),
                "fields": [
                    f.get("name") for f in node_data.get("fields", []) if f.get("name")
                ],
            }
            simplified["datasets"].append(dataset)

        elif node_type == "JOB":
            latest_run = node_data.get("latestRun", {})
            job = {
                "id": node_id,
                "name": node_data.get("simpleName") or node_data.get("name"),
                "inputs": [
                    f"{inp.get('namespace')}:{inp.get('name')}"
                    for inp in node_data.get("inputs", [])
                ],
                "outputs": [
                    f"{out.get('namespace')}:{out.get('name')}"
                    for out in node_data.get("outputs", [])
                ],
                "state": latest_run.get("state"),
            }
            simplified["jobs"].append(job)

        for edge in node.get("inEdges", []):
            edge_tuple = (edge.get("origin"), edge.get("destination"))
            edges_set.add(edge_tuple)

        for edge in node.get("outEdges", []):
            edge_tuple = (edge.get("origin"), edge.get("destination"))
            edges_set.add(edge_tuple)

    simplified["edges"] = [
        {"from": origin, "to": destination} for origin, destination in edges_set
    ]

    return simplified


def main():
    try:
        if len(sys.argv) > 1:
            arg = sys.argv[1]

            if arg.startswith("http"):
                # URL method
                import requests

                print(f"Fetching data: {arg}", file=sys.stderr)
                response = requests.get(
                    arg, headers={"Accept": "application/json"}, timeout=30
                )
                response.raise_for_status()
                raw_data = response.json()
                raw_input = json.dumps(raw_data)
            else:
                # File method
                with open(arg, "r") as f:
                    raw_input = f.read()
                raw_data = json.loads(raw_input)
        else:
            # Standard input method
            raw_input = sys.stdin.read()
            raw_data = json.loads(raw_input)

        # Process data
        simplified = simplify_marquez_lineage(raw_data)

        # Calculate compression effect
        original_size = len(raw_input)
        simplified_json = json.dumps(simplified, ensure_ascii=False)
        simplified_size = len(simplified_json)
        reduction = (1 - simplified_size / original_size) * 100

        print(
            f"Data compression: {original_size} -> {simplified_size} characters (reduced {reduction:.1f}%)",
            file=sys.stderr,
        )
        print(json.dumps(simplified, indent=2, ensure_ascii=False))

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
