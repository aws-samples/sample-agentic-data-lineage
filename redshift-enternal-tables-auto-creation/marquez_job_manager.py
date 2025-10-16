#!/usr/bin/env python3
"""
Marquez Job Manager
Used to query all jobs, keep the latest set of jobs, and delete expired jobs
from the same node
"""

import logging
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any, Dict, List

import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class MarquezJobManager:
    """Marquez Job Manager"""

    def __init__(self, base_url: str, api_key: str = None):
        """
        Initialize Marquez Job Manager

        Args:
            base_url: Marquez API base URL
            api_key: API key (optional)
        """
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()

        if api_key:
            self.session.headers.update({"Authorization": f"Bearer {api_key}"})

        self.session.headers.update(
            {"Content-Type": "application/json", "Accept": "application/json"}
        )

    def get_all_jobs(
        self, namespace: str = None, limit: int = 1000, offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get all jobs

        Args:
            namespace: Namespace filter (optional)
            limit: Limit per page
            offset: Offset

        Returns:
            List of jobs
        """
        try:
            url = f"{self.base_url}/api/v1/jobs"
            params = {"limit": limit, "offset": offset}

            if namespace:
                params["namespace"] = namespace

            response = self.session.get(url, params=params)
            response.raise_for_status()

            data = response.json()
            jobs = data.get("jobs", [])

            logger.info(f"Retrieved {len(jobs)} jobs")
            return jobs

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get jobs: {e}")
            raise

    def get_job_runs(
        self, namespace: str, job_name: str, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get all run records for specified job

        Args:
            namespace: Namespace
            job_name: Job name
            limit: Limit count

        Returns:
            List of job run records
        """
        try:
            from urllib.parse import quote

            # URL encode namespace and job_name to handle special characters
            encoded_namespace = quote(namespace, safe="")
            encoded_job_name = quote(job_name, safe="")

            url = (
                f"{self.base_url}/api/v1/namespaces/{encoded_namespace}/"
                f"jobs/{encoded_job_name}/runs"
            )
            params = {"limit": limit}

            response = self.session.get(url, params=params)
            response.raise_for_status()

            data = response.json()
            runs = data.get("runs", [])

            logger.debug(f"Job {namespace}.{job_name} has {len(runs)} run records")
            return runs

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get job run records: {namespace}.{job_name} - {e}")
            return []

    def delete_job_run(self, namespace: str, job_name: str, run_id: str) -> bool:
        """
        Delete specified job run record

        Args:
            namespace: Namespace
            job_name: Job name
            run_id: Run ID

        Returns:
            Whether deletion was successful
        """
        try:
            from urllib.parse import quote

            # URL encode namespace and job_name to handle special characters
            encoded_namespace = quote(namespace, safe="")
            encoded_job_name = quote(job_name, safe="")
            encoded_run_id = quote(run_id, safe="")

            url = (
                f"{self.base_url}/api/v1/namespaces/{encoded_namespace}/"
                f"jobs/{encoded_job_name}/runs/{encoded_run_id}"
            )
            response = self.session.delete(url)
            response.raise_for_status()

            logger.info(
                f"Successfully deleted job run record: {namespace}.{job_name}#{run_id}"
            )
            return True

        except requests.exceptions.RequestException as e:
            logger.error(
                f"Failed to delete job run record: "
                f"{namespace}.{job_name}#{run_id} - {e}"
            )
            return False

    def delete_job(self, namespace: str, job_name: str) -> bool:
        """
        Delete entire job

        Args:
            namespace: Namespace
            job_name: Job name

        Returns:
            Whether deletion was successful
        """
        try:
            from urllib.parse import quote

            # URL encode namespace and job_name to handle special characters
            encoded_namespace = quote(namespace, safe="")
            encoded_job_name = quote(job_name, safe="")

            url = (
                f"{self.base_url}/api/v1/namespaces/{encoded_namespace}/"
                f"jobs/{encoded_job_name}"
            )
            response = self.session.delete(url)
            response.raise_for_status()

            logger.info(f"Successfully deleted job: {namespace}.{job_name}")
            return True

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to delete job: {namespace}.{job_name} - {e}")
            return False

    def group_jobs_by_dataset(
        self, jobs: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Group jobs by dataset - dataset-centric grouping strategy

        Args:
            jobs: List of jobs

        Returns:
            Dictionary of jobs grouped by dataset, key is dataset identifier,
            value is list of jobs processing that dataset
        """
        grouped_jobs = defaultdict(list)

        for job in jobs:
            # Get job's output datasets
            outputs = job.get("outputs", [])

            if outputs:
                # If job has outputs, group by output dataset
                for output in outputs:
                    dataset_key = self._extract_dataset_key(output)
                    if dataset_key:
                        grouped_jobs[dataset_key].append(job)
            else:
                # If no outputs, try to group by input dataset
                inputs = job.get("inputs", [])
                if inputs:
                    for input_ds in inputs:
                        dataset_key = self._extract_dataset_key(input_ds)
                        if dataset_key:
                            grouped_jobs[dataset_key].append(job)
                else:
                    # If neither inputs nor outputs, group by job name
                    # (fallback strategy)
                    job_namespace = job.get("namespace", "")
                    if isinstance(job_namespace, dict):
                        job_namespace = job_namespace.get("name", "")
                    elif not isinstance(job_namespace, str):
                        job_namespace = str(job_namespace)

                    job_name = job.get("name", "")
                    fallback_key = f"{job_namespace}::{job_name}"
                    grouped_jobs[fallback_key].append(job)

        logger.info(
            f"Jobs grouped by dataset completed, {len(grouped_jobs)} datasets total"
        )
        return dict(grouped_jobs)

    def _extract_dataset_key(self, dataset: Dict[str, Any]) -> str:
        """
        Extract unique identifier from dataset information

        Args:
            dataset: Dataset information dictionary

        Returns:
            Unique identifier of dataset
        """
        if isinstance(dataset, dict):
            namespace = dataset.get("namespace", "")
            name = dataset.get("name", "")
            if namespace and name:
                return f"{namespace}::{name}"
        elif isinstance(dataset, str):
            # If dataset is string format, use directly
            return dataset

        return ""

    def group_jobs_by_node(
        self, jobs: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Group jobs by node (namespace + job name prefix) - compatible with old method

        Args:
            jobs: List of jobs

        Returns:
            Dictionary of jobs grouped by node
        """
        grouped_jobs = defaultdict(list)

        for job in jobs:
            # Handle different namespace formats
            namespace = job.get("namespace", "")
            if isinstance(namespace, dict):
                namespace = namespace.get("name", "")
            elif not isinstance(namespace, str):
                namespace = str(namespace)

            job_name = job.get("name", "")

            # Extract node identifier (can adjust grouping logic based on actual needs)
            # Assumes job name format: node_name_timestamp or node_name_version
            node_key = self._extract_node_key(namespace, job_name)
            grouped_jobs[node_key].append(job)

        logger.info(f"Jobs grouped by node completed, {len(grouped_jobs)} nodes total")
        return dict(grouped_jobs)

    def _extract_node_key(self, namespace: str, job_name: str) -> str:
        """
        Extract node identifier from namespace and job name

        Args:
            namespace: Namespace
            job_name: Job name

        Returns:
            Node identifier
        """
        # Handle nativespark type job names
        if job_name.startswith("nativespark_"):
            # For nativespark_xxx_jr_hash format job names
            # Extract base name, remove hash part after jr_
            parts = job_name.split("_jr_")
            if len(parts) >= 2:
                base_name = parts[0]  # e.g.: nativespark_glue_customers
                return f"{namespace}::{base_name}"

        # Handle other format job names
        parts = job_name.split("_")
        if len(parts) > 1:
            # Check if last part looks like timestamp or version number
            last_part = parts[-1]
            # If last part is number (timestamp) or version number starting
            # with v, remove it
            if (last_part.isdigit() and len(last_part) >= 6) or last_part.startswith(
                "v"
            ):
                node_name = "_".join(parts[:-1])
            else:
                node_name = job_name
        else:
            node_name = job_name

        return f"{namespace}::{node_name}"

    def find_latest_jobs_per_node(
        self, grouped_jobs: Dict[str, List[Dict[str, Any]]]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Find the latest job for each node

        Args:
            grouped_jobs: Jobs grouped by node

        Returns:
            Latest job for each node
        """
        latest_jobs = {}

        for node_key, jobs in grouped_jobs.items():
            if not jobs:
                continue

            # Sort by creation time, find the latest job
            latest_job = max(
                jobs, key=lambda x: self._parse_datetime(x.get("createdAt", ""))
            )
            latest_jobs[node_key] = latest_job

            logger.debug(
                f"Latest job for node {node_key}: {latest_job.get('name', '')}"
            )

        logger.info(f"Found latest jobs for {len(latest_jobs)} nodes")
        return latest_jobs

    def _parse_datetime(self, datetime_str: str) -> datetime:
        """
        Parse datetime string

        Args:
            datetime_str: Datetime string

        Returns:
            datetime object
        """
        try:
            # Try to parse ISO format datetime
            if datetime_str:
                # Handle possible timezone information
                if datetime_str.endswith("Z"):
                    datetime_str = datetime_str[:-1] + "+00:00"
                return datetime.fromisoformat(datetime_str.replace("Z", "+00:00"))
            else:
                return datetime.min.replace(tzinfo=timezone.utc)
        except ValueError:
            logger.warning(f"Unable to parse datetime: {datetime_str}")
            return datetime.min.replace(tzinfo=timezone.utc)

    def cleanup_old_jobs(
        self,
        namespace: str = None,
        keep_latest_count: int = 1,
        dry_run: bool = True,
        group_by_dataset: bool = True,
    ) -> Dict[str, Any]:
        """
        Clean up expired jobs, only keep the latest specified number of jobs
        for each dataset

        Args:
            namespace: Namespace filter (optional)
            keep_latest_count: Number of latest jobs to keep for each dataset
            dry_run: Whether it's dry run mode
            group_by_dataset: Whether to group by dataset (True) or by node (False)

        Returns:
            Cleanup result statistics
        """
        group_type = "dataset" if group_by_dataset else "node"
        logger.info(
            f"Starting to clean up expired jobs (grouped by {group_type}, "
            f"keep latest {keep_latest_count}, dry run: {dry_run})"
        )

        # Get all jobs
        all_jobs = self.get_all_jobs(namespace=namespace)

        if not all_jobs:
            logger.info("No jobs found")
            return {"total_jobs": 0, "deleted_jobs": 0, "kept_jobs": 0}

        # Group by dataset or node
        if group_by_dataset:
            grouped_jobs = self.group_jobs_by_dataset(all_jobs)
        else:
            grouped_jobs = self.group_jobs_by_node(all_jobs)

        deleted_count = 0
        kept_count = 0

        for group_key, jobs in grouped_jobs.items():
            # Sort by creation time (latest first)
            sorted_jobs = sorted(
                jobs,
                key=lambda x: self._parse_datetime(x.get("createdAt", "")),
                reverse=True,
            )

            # Keep the latest specified number of jobs
            jobs_to_keep = sorted_jobs[:keep_latest_count]
            jobs_to_delete = sorted_jobs[keep_latest_count:]

            kept_count += len(jobs_to_keep)

            if len(jobs_to_delete) > 0:
                logger.info(
                    f"{group_type} {group_key}: keep {len(jobs_to_keep)} jobs, "
                    f"delete {len(jobs_to_delete)} jobs"
                )

            # Delete expired jobs
            for job in jobs_to_delete:
                # Handle different namespace formats
                job_namespace = job.get("namespace", "")
                if isinstance(job_namespace, dict):
                    job_namespace = job_namespace.get("name", "")
                elif not isinstance(job_namespace, str):
                    job_namespace = str(job_namespace)

                job_name = job.get("name", "")

                if not dry_run:
                    if self.delete_job(job_namespace, job_name):
                        deleted_count += 1
                else:
                    logger.info(
                        f"[Dry run] Will delete job: {job_namespace}.{job_name}"
                    )
                    deleted_count += 1

        result = {
            "total_jobs": len(all_jobs),
            "deleted_jobs": deleted_count,
            "kept_jobs": kept_count,
            "groups_processed": len(grouped_jobs),
            "group_type": group_type,
        }

        logger.info(f"Cleanup completed: {result}")
        return result

    def cleanup_old_job_runs(
        self, namespace: str = None, keep_latest_runs: int = 5, dry_run: bool = True
    ) -> Dict[str, Any]:
        """
        Clean up expired job run records, only keep the latest specified number
        of run records for each job

        Args:
            namespace: Namespace filter (optional)
            keep_latest_runs: Number of latest run records to keep for each job
            dry_run: Whether it's dry run mode

        Returns:
            Cleanup result statistics
        """
        logger.info(
            f"Starting to clean up expired job run records "
            f"(keep latest {keep_latest_runs}, dry run: {dry_run})"
        )

        # Get all jobs
        all_jobs = self.get_all_jobs(namespace=namespace)

        if not all_jobs:
            logger.info("No jobs found")
            return {"total_runs": 0, "deleted_runs": 0, "kept_runs": 0}

        total_runs = 0
        deleted_runs = 0
        kept_runs = 0

        for job in all_jobs:
            # Handle different namespace formats
            job_namespace = job.get("namespace", "")
            if isinstance(job_namespace, dict):
                job_namespace = job_namespace.get("name", "")
            elif not isinstance(job_namespace, str):
                job_namespace = str(job_namespace)

            job_name = job.get("name", "")

            # Get all run records for the job
            runs = self.get_job_runs(job_namespace, job_name)

            if not runs:
                continue

            total_runs += len(runs)

            # Sort by creation time (latest first)
            sorted_runs = sorted(
                runs,
                key=lambda x: self._parse_datetime(x.get("createdAt", "")),
                reverse=True,
            )

            # Keep the latest specified number of run records
            runs_to_keep = sorted_runs[:keep_latest_runs]
            runs_to_delete = sorted_runs[keep_latest_runs:]

            kept_runs += len(runs_to_keep)

            if runs_to_delete:
                logger.info(
                    f"Job {job_namespace}.{job_name}: keep {len(runs_to_keep)} "
                    f"run records, delete {len(runs_to_delete)} run records"
                )

            # Delete expired run records
            for run in runs_to_delete:
                run_id = run.get("id", "")

                if not dry_run:
                    if self.delete_job_run(job_namespace, job_name, run_id):
                        deleted_runs += 1
                else:
                    logger.info(
                        f"[Dry run] Will delete run record: "
                        f"{job_namespace}.{job_name}#{run_id}"
                    )
                    deleted_runs += 1

        result = {
            "total_runs": total_runs,
            "deleted_runs": deleted_runs,
            "kept_runs": kept_runs,
            "jobs_processed": len(all_jobs),
        }

        logger.info(f"Run record cleanup completed: {result}")
        return result

    def get_job_statistics(self, namespace: str = None) -> Dict[str, Any]:
        """
        Get job statistics

        Args:
            namespace: Namespace filter (optional)

        Returns:
            Statistics information
        """
        all_jobs = self.get_all_jobs(namespace=namespace)
        grouped_jobs = self.group_jobs_by_node(all_jobs)

        stats = {
            "total_jobs": len(all_jobs),
            "total_nodes": len(grouped_jobs),
            "jobs_per_node": {},
            "namespaces": set(),
        }

        for node_key, jobs in grouped_jobs.items():
            stats["jobs_per_node"][node_key] = len(jobs)

            for job in jobs:
                # Handle different namespace formats
                job_namespace = job.get("namespace", "")
                if isinstance(job_namespace, dict):
                    job_namespace = job_namespace.get("name", "")
                elif not isinstance(job_namespace, str):
                    job_namespace = str(job_namespace)

                if job_namespace:
                    stats["namespaces"].add(job_namespace)

        stats["namespaces"] = list(stats["namespaces"])

        return stats


def main():
    """Example usage"""
    import argparse
    import os

    from dotenv import load_dotenv

    load_dotenv()

    parser = argparse.ArgumentParser(description="Marquez Job Manager")
    parser.add_argument(
        "--marquez-url", default=os.getenv("MARQUEZ_URL"), help="Marquez API URL"
    )
    parser.add_argument(
        "--marquez-api-key",
        default=os.getenv("MARQUEZ_API_KEY"),
        help="Marquez API key",
    )
    parser.add_argument("--namespace", help="Namespace filter")
    parser.add_argument(
        "--action",
        choices=["stats", "cleanup-jobs", "cleanup-runs"],
        default="stats",
        help="Operation to execute",
    )
    parser.add_argument(
        "--keep-jobs", type=int, default=1, help="Number of jobs to keep per node"
    )
    parser.add_argument(
        "--keep-runs", type=int, default=5, help="Number of run records to keep per job"
    )
    parser.add_argument("--dry-run", action="store_true", help="Dry run mode")
    parser.add_argument(
        "--group-by-node",
        action="store_true",
        help="Group by node instead of by dataset",
    )

    args = parser.parse_args()

    if not args.marquez_url:
        print("Error: Please provide Marquez URL")
        return

    # Create manager
    manager = MarquezJobManager(args.marquez_url, args.marquez_api_key)

    try:
        if args.action == "stats":
            # Get statistics
            stats = manager.get_job_statistics(args.namespace)
            print("\n=== Job Statistics ===")
            print(f"Total jobs: {stats['total_jobs']}")
            print(f"Total nodes: {stats['total_nodes']}")
            print(f"Namespaces: {', '.join(stats['namespaces'])}")
            print("\nJobs per node:")
            for node, count in stats["jobs_per_node"].items():
                print(f"  {node}: {count}")

        elif args.action == "cleanup-jobs":
            # Clean up expired jobs
            result = manager.cleanup_old_jobs(
                namespace=args.namespace,
                keep_latest_count=args.keep_jobs,
                dry_run=args.dry_run,
                group_by_dataset=not args.group_by_node,  # Default group by dataset
            )
            print("\n=== Job Cleanup Results ===")
            print(f"Total jobs: {result['total_jobs']}")
            print(f"Deleted jobs: {result['deleted_jobs']}")
            print(f"Kept jobs: {result['kept_jobs']}")
            print(f"Processed {result['group_type']}s: {result['groups_processed']}")

        elif args.action == "cleanup-runs":
            # Clean up expired run records
            result = manager.cleanup_old_job_runs(
                namespace=args.namespace,
                keep_latest_runs=args.keep_runs,
                dry_run=args.dry_run,
            )
            print("\n=== Run Record Cleanup Results ===")
            print(f"Total run records: {result['total_runs']}")
            print(f"Deleted run records: {result['deleted_runs']}")
            print(f"Kept run records: {result['kept_runs']}")
            print(f"Processed jobs: {result['jobs_processed']}")

    except Exception as e:
        logger.error(f"Operation failed: {e}")
        raise


if __name__ == "__main__":
    main()
