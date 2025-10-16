#!/usr/bin/env python3
"""
Advanced AWS Cost Analyzer - Comprehensive cost analysis using boto3
Supports multi-dimensional analysis, trend forecasting, and cost optimization recommendations
"""

import json
import logging
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import boto3
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class CostAnalysisConfig:
    """Cost analysis configuration"""

    deployment_name: str
    workspace: str
    region: str = "us-west-2"
    days_back: int = 30
    forecast_days: int = 30
    currency: str = "USD"


class AdvancedCostAnalyzer:
    """Advanced cost analyzer"""

    def __init__(self, config: CostAnalysisConfig):
        self.config = config
        self.ce_client = boto3.client(
            "ce", region_name="us-east-1"
        )  # Cost Explorer only available in us-east-1
        self.ec2_client = boto3.client("ec2", region_name=config.region)
        self.rds_client = boto3.client("rds", region_name=config.region)
        self.s3_client = boto3.client("s3", region_name=config.region)
        self.cloudwatch_client = boto3.client("cloudwatch", region_name=config.region)

    def get_comprehensive_cost_analysis(self) -> Dict[str, Any]:
        """Get comprehensive cost analysis"""
        logger.info(f"Starting cost analysis for {self.config.deployment_name}")

        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=self.config.days_back)).strftime(
            "%Y-%m-%d"
        )

        # Add diagnostic information
        tag_diagnosis = self._diagnose_tag_usage(start_date, end_date)

        analysis = {
            "metadata": {
                "deployment_name": self.config.deployment_name,
                "workspace": self.config.workspace,
                "analysis_period": {"start": start_date, "end": end_date},
                "generated_at": datetime.now().isoformat(),
            },
            "tag_diagnosis": tag_diagnosis,  # Add tag diagnosis
            "cost_summary": self._get_cost_summary(start_date, end_date),
            "service_breakdown": self._get_service_breakdown(start_date, end_date),
            "daily_trends": self._get_daily_trends(start_date, end_date),
            "resource_analysis": self._get_resource_analysis(),
            "optimization_recommendations": self._get_optimization_recommendations(),
            "forecast": self._get_cost_forecast(end_date),
            "budget_analysis": self._get_budget_analysis(),
            "anomaly_detection": self._detect_cost_anomalies(start_date, end_date),
            "tag_compliance": self._analyze_tag_compliance(),
            "rightsizing_opportunities": self._get_rightsizing_opportunities(),
            "reserved_instance_recommendations": self._get_ri_recommendations(),
            "savings_plans_recommendations": self._get_savings_plans_recommendations(),
        }

        return analysis

    def _diagnose_tag_usage(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """Diagnose tag usage"""
        try:
            logger.info("Diagnosing tag usage...")

            # Get all available tag keys
            response = self.ce_client.get_cost_and_usage(
                TimePeriod={"Start": start_date, "End": end_date},
                Granularity="MONTHLY",
                Metrics=["BlendedCost"],
                GroupBy=[{"Type": "TAG", "Key": "DeploymentName"}],
            )

            available_deployment_names = []
            for result in response.get("ResultsByTime", []):
                for group in result.get("Groups", []):
                    tag_value = group["Keys"][0]
                    cost = float(group["Metrics"]["BlendedCost"]["Amount"])
                    if cost > 0 and tag_value != "No DeploymentName":
                        available_deployment_names.append(
                            {"deployment_name": tag_value, "cost": round(cost, 2)}
                        )

            # Try other common tag keys
            other_tags = {}
            for tag_key in ["Workspace", "Environment", "Project", "Name"]:
                try:
                    tag_response = self.ce_client.get_cost_and_usage(
                        TimePeriod={"Start": start_date, "End": end_date},
                        Granularity="MONTHLY",
                        Metrics=["BlendedCost"],
                        GroupBy=[{"Type": "TAG", "Key": tag_key}],
                    )

                    tag_values = []
                    for result in tag_response.get("ResultsByTime", []):
                        for group in result.get("Groups", []):
                            tag_value = group["Keys"][0]
                            cost = float(group["Metrics"]["BlendedCost"]["Amount"])
                            if cost > 0 and not tag_value.startswith("No "):
                                tag_values.append(
                                    {"value": tag_value, "cost": round(cost, 2)}
                                )

                    if tag_values:
                        other_tags[tag_key] = tag_values[:5]  # Show only top 5

                except Exception:
                    continue

            return {
                "target_deployment_name": self.config.deployment_name,
                "available_deployment_names": available_deployment_names,
                "other_available_tags": other_tags,
                "recommendation": (
                    "Check if resources are properly tagged with DeploymentName"
                    if not available_deployment_names
                    else "Tags found successfully"
                ),
            }

        except Exception as e:
            logger.error(f"Tag diagnosis failed: {str(e)}")
            return {"error": str(e), "recommendation": "Unable to diagnose tag usage"}

    def _get_cost_summary(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """Get cost summary"""
        try:
            # First try to get cost with tag filtering
            logger.info(
                f"Attempting to get cost data with tag filtering (DeploymentName={self.config.deployment_name})"
            )

            response_with_filter = self.ce_client.get_cost_and_usage(
                TimePeriod={"Start": start_date, "End": end_date},
                Granularity="MONTHLY",
                Metrics=["BlendedCost", "UnblendedCost", "UsageQuantity"],
                Filter={
                    "Tags": {
                        "Key": "DeploymentName",
                        "Values": [self.config.deployment_name],
                    }
                },
            )

            total_cost_filtered = 0.0
            unblended_cost_filtered = 0.0

            for result in response_with_filter.get("ResultsByTime", []):
                total_cost_filtered += float(result["Total"]["BlendedCost"]["Amount"])
                unblended_cost_filtered += float(
                    result["Total"]["UnblendedCost"]["Amount"]
                )

            # If filtered result is 0, try to get total account cost as reference
            if total_cost_filtered == 0.0:
                logger.info(
                    "Filtered cost is 0, getting total account cost as reference"
                )

                response_total = self.ce_client.get_cost_and_usage(
                    TimePeriod={"Start": start_date, "End": end_date},
                    Granularity="MONTHLY",
                    Metrics=["BlendedCost", "UnblendedCost"],
                )

                total_cost_account = 0.0
                unblended_cost_account = 0.0

                for result in response_total.get("ResultsByTime", []):
                    total_cost_account += float(
                        result["Total"]["BlendedCost"]["Amount"]
                    )
                    unblended_cost_account += float(
                        result["Total"]["UnblendedCost"]["Amount"]
                    )

                # Calculate average daily cost
                days = (
                    datetime.strptime(end_date, "%Y-%m-%d")
                    - datetime.strptime(start_date, "%Y-%m-%d")
                ).days
                avg_daily_cost = total_cost_account / days if days > 0 else 0

                return {
                    "total_blended_cost": round(total_cost_account, 2),
                    "total_unblended_cost": round(unblended_cost_account, 2),
                    "average_daily_cost": round(avg_daily_cost, 2),
                    "projected_monthly_cost": round(avg_daily_cost * 30, 2),
                    "currency": self.config.currency,
                    "note": f"Account-wide costs (no resources found with DeploymentName={self.config.deployment_name})",
                    "filtered_cost": 0.0,
                    "account_total_cost": round(total_cost_account, 2),
                }
            else:
                # Use filtered cost
                days = (
                    datetime.strptime(end_date, "%Y-%m-%d")
                    - datetime.strptime(start_date, "%Y-%m-%d")
                ).days
                avg_daily_cost = total_cost_filtered / days if days > 0 else 0

                return {
                    "total_blended_cost": round(total_cost_filtered, 2),
                    "total_unblended_cost": round(unblended_cost_filtered, 2),
                    "average_daily_cost": round(avg_daily_cost, 2),
                    "projected_monthly_cost": round(avg_daily_cost * 30, 2),
                    "currency": self.config.currency,
                    "note": f"Costs for resources tagged with DeploymentName={self.config.deployment_name}",
                }

        except Exception as e:
            logger.error(f"Failed to get cost summary: {str(e)}")
            return {}

    def _get_service_breakdown(
        self, start_date: str, end_date: str
    ) -> List[Dict[str, Any]]:
        """Get cost analysis grouped by service"""
        try:
            # First try with tag filtering
            logger.info("Getting cost data grouped by service")

            response = self.ce_client.get_cost_and_usage(
                TimePeriod={"Start": start_date, "End": end_date},
                Granularity="MONTHLY",
                Metrics=["BlendedCost", "UsageQuantity"],
                GroupBy=[{"Type": "DIMENSION", "Key": "SERVICE"}],
                Filter={
                    "Tags": {
                        "Key": "DeploymentName",
                        "Values": [self.config.deployment_name],
                    }
                },
            )

            services = []
            service_totals = defaultdict(float)

            for result in response.get("ResultsByTime", []):
                for group in result.get("Groups", []):
                    service = group["Keys"][0]
                    cost = float(group["Metrics"]["BlendedCost"]["Amount"])
                    usage = float(group["Metrics"]["UsageQuantity"]["Amount"])

                    service_totals[service] += cost

                    services.append(
                        {
                            "service": service,
                            "cost": round(cost, 2),
                            "usage_quantity": round(usage, 2),
                            "currency": group["Metrics"]["BlendedCost"]["Unit"],
                        }
                    )

            # If no tagged services found, get account-level service breakdown
            if not services:
                logger.info(
                    "No tagged services found, getting account-level service breakdown"
                )

                response_all = self.ce_client.get_cost_and_usage(
                    TimePeriod={"Start": start_date, "End": end_date},
                    Granularity="MONTHLY",
                    Metrics=["BlendedCost"],
                    GroupBy=[{"Type": "DIMENSION", "Key": "SERVICE"}],
                )

                for result in response_all.get("ResultsByTime", []):
                    for group in result.get("Groups", []):
                        service = group["Keys"][0]
                        cost = float(group["Metrics"]["BlendedCost"]["Amount"])

                        if cost > 0:  # Only show services with cost
                            services.append(
                                {
                                    "service": service,
                                    "cost": round(cost, 2),
                                    "currency": group["Metrics"]["BlendedCost"]["Unit"],
                                    "note": "Account-wide (not filtered by deployment tag)",
                                }
                            )

            # Sort by cost
            services.sort(key=lambda x: x["cost"], reverse=True)

            return services

        except Exception as e:
            logger.error(f"Failed to get service analysis: {str(e)}")
            return []

    def _get_daily_trends(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Get daily cost trends"""
        try:
            response = self.ce_client.get_cost_and_usage(
                TimePeriod={"Start": start_date, "End": end_date},
                Granularity="DAILY",
                Metrics=["BlendedCost"],
                Filter={
                    "Tags": {
                        "Key": "DeploymentName",
                        "Values": [self.config.deployment_name],
                    }
                },
            )

            daily_costs = []
            for result in response.get("ResultsByTime", []):
                daily_costs.append(
                    {
                        "date": result["TimePeriod"]["Start"],
                        "cost": round(
                            float(result["Total"]["BlendedCost"]["Amount"]), 2
                        ),
                        "currency": result["Total"]["BlendedCost"]["Unit"],
                    }
                )

            # Calculate trend metrics
            if len(daily_costs) >= 7:
                recent_week = daily_costs[-7:]
                previous_week = daily_costs[-14:-7] if len(daily_costs) >= 14 else []

                recent_avg = sum(d["cost"] for d in recent_week) / len(recent_week)
                previous_avg = (
                    sum(d["cost"] for d in previous_week) / len(previous_week)
                    if previous_week
                    else recent_avg
                )

                trend_percentage = (
                    ((recent_avg - previous_avg) / previous_avg * 100)
                    if previous_avg > 0
                    else 0
                )

                for cost in daily_costs:
                    cost["trend_analysis"] = {
                        "recent_week_avg": round(recent_avg, 2),
                        "previous_week_avg": round(previous_avg, 2),
                        "trend_percentage": round(trend_percentage, 2),
                    }

            return daily_costs

        except Exception as e:
            logger.error(f"Failed to get daily trends: {str(e)}")
            return []

    def _get_resource_analysis(self) -> Dict[str, Any]:
        """Get resource analysis"""
        try:
            resources = {
                "ec2_instances": self._analyze_ec2_instances(),
                "rds_instances": self._analyze_rds_instances(),
                "s3_buckets": self._analyze_s3_buckets(),
                "load_balancers": self._analyze_load_balancers(),
            }

            return resources

        except Exception as e:
            logger.error(f"Resource analysis failed: {str(e)}")
            return {}

    def _analyze_ec2_instances(self) -> List[Dict[str, Any]]:
        """Analyze EC2 instances"""
        try:
            response = self.ec2_client.describe_instances(
                Filters=[
                    {
                        "Name": "tag:DeploymentName",
                        "Values": [self.config.deployment_name],
                    },
                    {"Name": "instance-state-name", "Values": ["running", "stopped"]},
                ]
            )

            instances = []
            for reservation in response["Reservations"]:
                for instance in reservation["Instances"]:
                    # Get CloudWatch metrics
                    utilization = self._get_instance_utilization(instance["InstanceId"])

                    instances.append(
                        {
                            "instance_id": instance["InstanceId"],
                            "instance_type": instance["InstanceType"],
                            "state": instance["State"]["Name"],
                            "launch_time": instance["LaunchTime"].isoformat(),
                            "utilization": utilization,
                            "tags": {
                                tag["Key"]: tag["Value"]
                                for tag in instance.get("Tags", [])
                            },
                        }
                    )

            return instances

        except Exception as e:
            logger.error(f"EC2 instance analysis failed: {str(e)}")
            return []

    def _get_instance_utilization(self, instance_id: str) -> Dict[str, float]:
        """getinstanceutilization"""
        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(days=7)

            # CPUutilization
            cpu_response = self.cloudwatch_client.get_metric_statistics(
                Namespace="AWS/EC2",
                MetricName="CPUUtilization",
                Dimensions=[{"Name": "InstanceId", "Value": instance_id}],
                StartTime=start_time,
                EndTime=end_time,
                Period=3600,
                Statistics=["Average"],
            )

            cpu_avg = (
                np.mean([point["Average"] for point in cpu_response["Datapoints"]])
                if cpu_response["Datapoints"]
                else 0
            )

            return {
                "cpu_average": round(cpu_avg, 2),
                "cpu_max": round(
                    max(
                        [point["Average"] for point in cpu_response["Datapoints"]],
                        default=0,
                    ),
                    2,
                ),
            }

        except Exception as e:
            logger.error(f"getinstanceutilizationfailed: {str(e)}")
            return {"cpu_average": 0, "cpu_max": 0}

    def _analyze_rds_instances(self) -> List[Dict[str, Any]]:
        """analyzeRDSinstance"""
        try:
            response = self.rds_client.describe_db_instances()

            instances = []
            for db in response["DBInstances"]:
                # Check tags
                tags_response = self.rds_client.list_tags_for_resource(
                    ResourceName=db["DBInstanceArn"]
                )

                tags = {tag["Key"]: tag["Value"] for tag in tags_response["TagList"]}

                if tags.get("DeploymentName") == self.config.deployment_name:
                    instances.append(
                        {
                            "db_instance_identifier": db["DBInstanceIdentifier"],
                            "db_instance_class": db["DBInstanceClass"],
                            "engine": db["Engine"],
                            "engine_version": db["EngineVersion"],
                            "status": db["DBInstanceStatus"],
                            "allocated_storage": db["AllocatedStorage"],
                            "multi_az": db["MultiAZ"],
                            "tags": tags,
                        }
                    )

            return instances

        except Exception as e:
            logger.error(f"RDSinstanceanalyzefailed: {str(e)}")
            return []

    def _analyze_s3_buckets(self) -> List[Dict[str, Any]]:
        """analyzeS3bucket"""
        try:
            response = self.s3_client.list_buckets()

            buckets = []
            for bucket in response["Buckets"]:
                try:
                    # getbucket tags
                    tags_response = self.s3_client.get_bucket_tagging(
                        Bucket=bucket["Name"]
                    )
                    tags = {tag["Key"]: tag["Value"] for tag in tags_response["TagSet"]}

                    if tags.get("DeploymentName") == self.config.deployment_name:
                        # Get bucket size
                        size_response = self.cloudwatch_client.get_metric_statistics(
                            Namespace="AWS/S3",
                            MetricName="BucketSizeBytes",
                            Dimensions=[
                                {"Name": "BucketName", "Value": bucket["Name"]},
                                {"Name": "StorageType", "Value": "StandardStorage"},
                            ],
                            StartTime=datetime.now() - timedelta(days=2),
                            EndTime=datetime.now(),
                            Period=86400,
                            Statistics=["Average"],
                        )

                        size_bytes = (
                            size_response["Datapoints"][-1]["Average"]
                            if size_response["Datapoints"]
                            else 0
                        )

                        buckets.append(
                            {
                                "name": bucket["Name"],
                                "creation_date": bucket["CreationDate"].isoformat(),
                                "size_bytes": int(size_bytes),
                                "size_gb": round(size_bytes / (1024**3), 2),
                                "tags": tags,
                            }
                        )

                except Exception:
                    # Skip if bucket has no tags or is inaccessible
                    continue

            return buckets

        except Exception as e:
            logger.error(f"S3bucketanalyzefailed: {str(e)}")
            return []

    def _analyze_load_balancers(self) -> List[Dict[str, Any]]:
        """analyzeload balancer"""
        try:
            elbv2_client = boto3.client("elbv2", region_name=self.config.region)
            response = elbv2_client.describe_load_balancers()

            load_balancers = []
            for lb in response["LoadBalancers"]:
                # gettags
                tags_response = elbv2_client.describe_tags(
                    ResourceArns=[lb["LoadBalancerArn"]]
                )
                tags = {}
                for tag_desc in tags_response["TagDescriptions"]:
                    tags.update({tag["Key"]: tag["Value"] for tag in tag_desc["Tags"]})

                if tags.get("DeploymentName") == self.config.deployment_name:
                    load_balancers.append(
                        {
                            "name": lb["LoadBalancerName"],
                            "type": lb["Type"],
                            "scheme": lb["Scheme"],
                            "state": lb["State"]["Code"],
                            "created_time": lb["CreatedTime"].isoformat(),
                            "tags": tags,
                        }
                    )

            return load_balancers

        except Exception as e:
            logger.error(f"load balanceranalyzefailed: {str(e)}")
            return []

    def _get_optimization_recommendations(self) -> List[Dict[str, Any]]:
        """getoptimizerecommendation"""
        recommendations = []

        # Recommendations based on resource utilization
        try:
            instances = self._analyze_ec2_instances()
            for instance in instances:
                if instance["utilization"]["cpu_average"] < 10:
                    recommendations.append(
                        {
                            "type": "rightsizing",
                            "resource": f"EC2 Instance {instance['instance_id']}",
                            "current_type": instance["instance_type"],
                            "recommendation": "Consider downsizing or stopping this instance",
                            "reason": f"Low CPU utilization: {instance['utilization']['cpu_average']}%",
                            "potential_savings": "Up to 50% cost reduction",
                            "priority": (
                                "high"
                                if instance["utilization"]["cpu_average"] < 5
                                else "medium"
                            ),
                        }
                    )
        except Exception as e:
            logger.error(f"generateoptimizerecommendationfailed: {str(e)}")

        return recommendations

    def _get_cost_forecast(self, end_date: str) -> Dict[str, Any]:
        """getcostforecast"""
        try:
            forecast_end = (
                datetime.strptime(end_date, "%Y-%m-%d")
                + timedelta(days=self.config.forecast_days)
            ).strftime("%Y-%m-%d")

            # First try forecast without filters
            try:
                response = self.ce_client.get_cost_forecast(
                    TimePeriod={"Start": end_date, "End": forecast_end},
                    Metric="BLENDED_COST",
                    Granularity="MONTHLY",  # Changed to MONTHLY, easier to get data
                )

                return {
                    "total_forecast": round(float(response["Total"]["Amount"]), 2),
                    "currency": response["Total"]["Unit"],
                    "forecast_period": {"start": end_date, "end": forecast_end},
                    "confidence_level": "Medium",
                    "note": "Account-wide forecast (insufficient data for tag-based forecast)",
                }
            except Exception as inner_e:
                logger.warning(
                    f"Unable to get cost forecast, possibly insufficient historical data: {str(inner_e)}"
                )
                return {
                    "error": "Insufficient historical data for forecasting",
                    "recommendation": "Wait for more billing data to accumulate (typically 2-3 months)",
                }

        except Exception as e:
            logger.error(f"costforecastfailed: {str(e)}")
            return {}

    def _get_budget_analysis(self) -> Dict[str, Any]:
        """Get budget analysis"""
        try:
            budgets_client = boto3.client(
                "budgets", region_name="us-east-1"
            )  # Budgets API only available in us-east-1
            account_id = boto3.client("sts").get_caller_identity()["Account"]

            response = budgets_client.describe_budgets(AccountId=account_id)

            relevant_budgets = []
            all_budgets = []

            for budget in response.get("Budgets", []):
                budget_info = {
                    "name": budget["BudgetName"],
                    "limit": float(budget["BudgetLimit"]["Amount"]),
                    "currency": budget["BudgetLimit"]["Unit"],
                    "time_unit": budget["TimeUnit"],
                    "budget_type": budget["BudgetType"],
                }

                all_budgets.append(budget_info)

                # Check if related to current deployment
                if self.config.deployment_name.lower() in budget["BudgetName"].lower():
                    relevant_budgets.append(budget_info)

            return {
                "relevant_budgets": relevant_budgets,
                "all_budgets_count": len(all_budgets),
                "has_budgets": len(all_budgets) > 0,
            }

        except Exception as e:
            logger.error(f"budgetanalyzefailed: {str(e)}")
            return {
                "error": str(e),
                "recommendation": "Consider creating budgets for cost monitoring",
            }

    def _detect_cost_anomalies(
        self, start_date: str, end_date: str
    ) -> List[Dict[str, Any]]:
        """detectcostanomaly"""
        try:
            # First try to get anomaly detector list
            try:
                # Try different API methods
                if hasattr(self.ce_client, "get_anomaly_detectors"):
                    detectors_response = self.ce_client.get_anomaly_detectors()
                elif hasattr(self.ce_client, "describe_anomaly_detectors"):
                    detectors_response = self.ce_client.describe_anomaly_detectors()
                else:
                    # If none available, skip directly
                    return [
                        {
                            "info": "Anomaly detection API not available",
                            "recommendation": "Update boto3 to latest version or check AWS region support",
                        }
                    ]
            except Exception as api_error:
                logger.warning(f"Unable to get anomaly detectors: {str(api_error)}")
                return [
                    {
                        "info": "Unable to access anomaly detectors",
                        "recommendation": "Check permissions for Cost Explorer anomaly detection APIs",
                        "error": str(api_error),
                    }
                ]

            if not detectors_response.get("AnomalyDetectors"):
                logger.info("No anomaly detectors found, skipping anomaly detection")
                return [
                    {
                        "info": "No anomaly detectors configured",
                        "recommendation": "Create anomaly detectors in AWS Cost Explorer for automated anomaly detection",
                    }
                ]

            # Use the first detector's ARN
            detector_arn = detectors_response["AnomalyDetectors"][0]["MonitorArn"]

            response = self.ce_client.get_anomalies(
                DateInterval={"StartDate": start_date, "EndDate": end_date},
                MonitorArn=detector_arn,
            )

            anomalies = []
            for anomaly in response.get("Anomalies", []):
                anomalies.append(
                    {
                        "anomaly_id": anomaly["AnomalyId"],
                        "start_date": anomaly["AnomalyStartDate"],
                        "end_date": anomaly.get("AnomalyEndDate"),
                        "impact": float(anomaly["Impact"]["TotalImpact"]),
                        "currency": anomaly["Impact"]["Unit"],
                        "feedback": anomaly.get("Feedback", "NO_FEEDBACK"),
                        "dimension_key": anomaly.get("DimensionKey", "Unknown"),
                    }
                )

            return anomalies

        except Exception as e:
            logger.error(f"anomalydetectfailed: {str(e)}")
            return [
                {
                    "error": str(e),
                    "recommendation": "Set up Cost Anomaly Detection in AWS Cost Explorer",
                }
            ]

    def _analyze_tag_compliance(self) -> Dict[str, Any]:
        """Analyze tag compliance"""
        try:
            # Here we can check if resources have necessary tags
            required_tags = ["DeploymentName", "Workspace", "ManagedBy"]

            compliance_report = {
                "required_tags": required_tags,
                "compliant_resources": 0,
                "non_compliant_resources": 0,
                "compliance_percentage": 0,
                "missing_tags_by_resource": [],
            }

            # Check EC2 instances
            instances = self._analyze_ec2_instances()
            for instance in instances:
                missing_tags = [
                    tag for tag in required_tags if tag not in instance["tags"]
                ]
                if missing_tags:
                    compliance_report["non_compliant_resources"] += 1
                    compliance_report["missing_tags_by_resource"].append(
                        {
                            "resource_type": "EC2",
                            "resource_id": instance["instance_id"],
                            "missing_tags": missing_tags,
                        }
                    )
                else:
                    compliance_report["compliant_resources"] += 1

            total_resources = (
                compliance_report["compliant_resources"]
                + compliance_report["non_compliant_resources"]
            )
            if total_resources > 0:
                compliance_report["compliance_percentage"] = round(
                    (compliance_report["compliant_resources"] / total_resources) * 100,
                    2,
                )

            return compliance_report

        except Exception as e:
            logger.error(f"Tag compliance analysis failed: {str(e)}")
            return {}

    def _get_rightsizing_opportunities(self) -> List[Dict[str, Any]]:
        """Get resource rightsizing recommendations"""
        try:
            # Don't use tag filters as API doesn't support them
            response = self.ce_client.get_rightsizing_recommendation(
                Service="AmazonEC2",  # Add required Service parameter
                Configuration={
                    "BenefitsConsidered": True,
                    "RecommendationTarget": "SAME_INSTANCE_FAMILY",
                },
            )

            opportunities = []
            for rec in response.get("RightsizingRecommendations", []):
                # Manually filter deployment-related resources
                resource_tags = rec.get("CurrentInstance", {}).get("Tags", {})
                if resource_tags.get("DeploymentName") == self.config.deployment_name:
                    opportunities.append(
                        {
                            "resource_id": rec.get("ResourceId", "Unknown"),
                            "account_id": rec.get("AccountId", "Unknown"),
                            "current_instance": rec.get("CurrentInstance", {}),
                            "rightsizing_type": rec.get("RightsizingType", "Unknown"),
                            "modify_recommendation": rec.get(
                                "ModifyRecommendationDetail", {}
                            ),
                            "terminate_recommendation": rec.get(
                                "TerminateRecommendationDetail", {}
                            ),
                            "estimated_monthly_savings": rec.get(
                                "EstimatedMonthlySavings", {}
                            ),
                        }
                    )

            if not opportunities:
                return [
                    {
                        "info": "No rightsizing opportunities found for this deployment",
                        "note": "This could mean resources are already optimally sized or insufficient usage data",
                    }
                ]

            return opportunities

        except Exception as e:
            error_msg = str(e)
            if (
                "AccessDeniedException" in error_msg
                and "opt-in only feature" in error_msg
            ):
                return [
                    {
                        "info": "Rightsizing recommendations not enabled",
                        "recommendation": "Enable rightsizing recommendations in AWS Cost Explorer Preferences (requires PAYER account access)",
                        "note": "This is an opt-in feature that needs to be enabled by the billing account administrator",
                    }
                ]
            else:
                logger.error(
                    f"Get resource rightsizing recommendations failed: {str(e)}"
                )
                return [
                    {
                        "error": str(e),
                        "recommendation": "Ensure EC2 instances have been running for at least 14 days for rightsizing analysis",
                    }
                ]

    def _get_ri_recommendations(self) -> List[Dict[str, Any]]:
        """Get reserved instance recommendations"""
        try:
            # Don't use tag filters, API doesn't support them
            response = self.ce_client.get_reservation_purchase_recommendation(
                Service="Amazon Elastic Compute Cloud - Compute"
            )

            recommendations = []
            for rec in response.get("Recommendations", []):
                recommendations.append(
                    {
                        "instance_details": rec.get("InstanceDetails", {}),
                        "recommended_quantity": rec.get(
                            "RecommendedNumberOfInstancesToPurchase", 0
                        ),
                        "estimated_monthly_savings": rec.get(
                            "EstimatedMonthlySavingsAmount", 0
                        ),
                        "estimated_monthly_on_demand_cost": rec.get(
                            "EstimatedMonthlyOnDemandCost", 0
                        ),
                        "estimated_reservation_cost": rec.get(
                            "EstimatedReservationCostForLookbackPeriod", 0
                        ),
                    }
                )

            if not recommendations:
                return [
                    {
                        "info": "No Reserved Instance recommendations available",
                        "note": "RI recommendations require consistent usage patterns over time",
                    }
                ]

            return recommendations

        except Exception as e:
            logger.error(f"Get reserved instance recommendations failed: {str(e)}")
            return [
                {
                    "error": str(e),
                    "recommendation": "Reserved Instance recommendations require stable usage patterns over 14+ days",
                }
            ]

    def _get_savings_plans_recommendations(self) -> List[Dict[str, Any]]:
        """getSavings Plansrecommendation"""
        try:
            response = self.ce_client.get_savings_plans_purchase_recommendation(
                SavingsPlansType="COMPUTE_SP",
                TermInYears="ONE_YEAR",
                PaymentOption="NO_UPFRONT",
                LookbackPeriodInDays="SIXTY_DAYS",  # Should be string enum value
            )

            recommendations = []
            for rec in response.get("SavingsPlansRecommendationDetails", []):
                recommendations.append(
                    {
                        "savings_plans_type": rec.get("SavingsPlansType", "Unknown"),
                        "term_in_years": rec.get("TermInYears", "Unknown"),
                        "payment_option": rec.get("PaymentOption", "Unknown"),
                        "hourly_commitment": rec.get("HourlyCommitment", 0),
                        "estimated_savings_amount": rec.get(
                            "EstimatedSavingsAmount", 0
                        ),
                        "estimated_savings_percentage": rec.get(
                            "EstimatedSavingsPercentage", 0
                        ),
                        "estimated_monthly_commitment": rec.get(
                            "EstimatedMonthlySavings", 0
                        ),
                    }
                )

            if not recommendations:
                return [
                    {
                        "info": "No Savings Plans recommendations available",
                        "note": "Savings Plans recommendations require consistent compute usage patterns",
                    }
                ]

            return recommendations

        except Exception as e:
            logger.error(f"getSavings Plansrecommendationfailed: {str(e)}")
            return [
                {
                    "error": str(e),
                    "recommendation": "Savings Plans recommendations require stable compute usage over 60+ days",
                }
            ]

    def generate_comprehensive_report(self) -> str:
        """Generate comprehensive cost analysis report"""
        analysis = self.get_comprehensive_cost_analysis()

        report = f"""
# 🏗️ AWS Cost Analysis Report - {analysis['metadata']['deployment_name']}

## 📊 Executive Summary
- **Deployment Environment**: {analysis['metadata']['deployment_name']} ({analysis['metadata']['workspace']})
- **Analysis Period**: {analysis['metadata']['analysis_period']['start']} to {analysis['metadata']['analysis_period']['end']}
- **Report Generated**: {analysis['metadata']['generated_at']}

## � Tag Diagnosis
"""

        # Add tag diagnosis information
        if analysis.get("tag_diagnosis"):
            diagnosis = analysis["tag_diagnosis"]
            if diagnosis.get("available_deployment_names"):
                report += f"- **Found DeploymentName tags**: {len(diagnosis['available_deployment_names'])} items\n"
                for dep in diagnosis["available_deployment_names"][:3]:
                    report += f"  - {dep['deployment_name']}: ${dep['cost']} USD\n"
            else:
                report += "- **⚠️ DeploymentName tag not found**: Resources may not be properly tagged\n"

            if diagnosis.get("other_available_tags"):
                report += f"- **Other available tags**: {', '.join(diagnosis['other_available_tags'].keys())}\n"

        report += "\n## 💰 Cost Summary\n"

        if analysis.get("cost_summary"):
            summary = analysis["cost_summary"]
            report += f"""
- **Total Cost**: ${summary.get('total_blended_cost', 0)} {summary.get('currency', 'USD')}
- **Average Daily Cost**: ${summary.get('average_daily_cost', 0)} {summary.get('currency', 'USD')}
- **Projected Monthly Cost**: ${summary.get('projected_monthly_cost', 0)} {summary.get('currency', 'USD')}
"""

        # serviceanalyze
        if analysis.get("service_breakdown"):
            report += "\n## 🔧 servicecostanalyze\n"
            service_costs = {}
            for service in analysis["service_breakdown"]:
                service_name = service["service"]
                if service_name not in service_costs:
                    service_costs[service_name] = 0
                service_costs[service_name] += service["cost"]

            # Show top 10 most expensive services
            sorted_services = sorted(
                service_costs.items(), key=lambda x: x[1], reverse=True
            )[:10]
            for service, cost in sorted_services:
                report += f"- **{service}**: ${cost} USD\n"

        # optimizerecommendation
        if analysis.get("optimization_recommendations"):
            report += "\n## 🎯 optimizerecommendation\n"
            for rec in analysis["optimization_recommendations"][
                :5
            ]:  # Show top 5 recommendations
                report += f"- **{rec['type'].title()}**: {rec['recommendation']}\n"
                report += f"  - resource: {rec['resource']}\n"
                report += f"  - Reason: {rec['reason']}\n"
                report += f"  - Potential Savings: {rec['potential_savings']}\n\n"

        # costforecast
        if analysis.get("forecast"):
            forecast = analysis["forecast"]
            report += "\n## 📈 Cost Forecast\n"
            report += f"- **Total Forecast Cost**: ${forecast.get('total_forecast', 0)} {forecast.get('currency', 'USD')}\n"
            report += f"- **Forecast Period**: {forecast.get('forecast_period', {}).get('start')} to {forecast.get('forecast_period', {}).get('end')}\n"

        # Tag compliance
        if analysis.get("tag_compliance"):
            compliance = analysis["tag_compliance"]
            report += "\n## 🏷️ Tag Compliance\n"
            report += f"- **Compliance Rate**: {compliance.get('compliance_percentage', 0)}%\n"
            report += f"- **Compliant Resources**: {compliance.get('compliant_resources', 0)}\n"
            report += f"- **Non-compliant Resources**: {compliance.get('non_compliant_resources', 0)}\n"

        # anomalydetect
        if analysis.get("anomaly_detection"):
            anomalies = analysis["anomaly_detection"]
            if anomalies:
                report += "\n## ⚠️ Cost Anomalies\n"
                for anomaly in anomalies[:3]:  # Show top 3 anomalies
                    if "anomaly_id" in anomaly:
                        report += f"- **anomalyID**: {anomaly['anomaly_id']}\n"
                        report += f"  - Impact: ${anomaly.get('impact', 0)} USD\n"
                        report += (
                            f"  - Time: {anomaly.get('start_date', 'Unknown')}\n\n"
                        )
                    elif "error" in anomaly:
                        report += f"- **anomalydetect**: {anomaly.get('recommendation', 'No anomaly detection configured')}\n"
                    elif "info" in anomaly:
                        report += f"- **information**: {anomaly['info']}\n"
                        if "recommendation" in anomaly:
                            report += (
                                f"  - recommendation: {anomaly['recommendation']}\n"
                            )

        return report

    def export_to_json(self, filename: Optional[str] = None) -> str:
        """Export analysis results to JSON"""
        analysis = self.get_comprehensive_cost_analysis()

        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"cost_analysis_{self.config.deployment_name}_{timestamp}.json"

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False, default=str)

        return filename

    def export_to_markdown(self, filename: Optional[str] = None) -> str:
        """Export analysis results to Markdown format"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = (
                f"cost_analysis_report_{self.config.deployment_name}_{timestamp}.md"
            )

        report = self.generate_comprehensive_report()

        with open(filename, "w", encoding="utf-8") as f:
            f.write(report)

        return filename

    def export_detailed_markdown(self, filename: Optional[str] = None) -> str:
        """Export detailed Markdown report"""
        analysis = self.get_comprehensive_cost_analysis()

        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = (
                f"detailed_cost_report_{self.config.deployment_name}_{timestamp}.md"
            )

        # Generate detailed Markdown report
        report = self._generate_detailed_markdown_report(analysis)

        with open(filename, "w", encoding="utf-8") as f:
            f.write(report)

        return filename

    def _generate_detailed_markdown_report(self, analysis: Dict[str, Any]) -> str:
        """Generate detailed Markdown report"""
        report = f"""# 🏗️ AWS Cost Analysis Detailed Report

## 📋 Basic Information

| Item | Value |
|------|-------|
| **Deployment Name** | {analysis['metadata']['deployment_name']} |
| **Workspace** | {analysis['metadata']['workspace']} |
| **Analysis Period** | {analysis['metadata']['analysis_period']['start']} to {analysis['metadata']['analysis_period']['end']} |
| **Report Generated** | {analysis['metadata']['generated_at']} |

---

## 🔍 tagdiagnose

"""

        # tagdiagnoseinformation
        if analysis.get("tag_diagnosis"):
            diagnosis = analysis["tag_diagnosis"]

            report += "### Target Deployment Tags\n"
            report += f"- **Search Target**: `{diagnosis.get('target_deployment_name', 'Unknown')}`\n\n"

            if diagnosis.get("available_deployment_names"):
                report += "### Found DeploymentName Tags\n\n"
                report += "| Deployment Name | Cost (USD) |\n"
                report += "|----------|------------|\n"
                for dep in diagnosis["available_deployment_names"]:
                    report += f"| `{dep['deployment_name']}` | ${dep['cost']:.2f} |\n"
                report += "\n"
            else:
                report += "### ⚠️ Tag Issues\n"
                report += "- DeploymentName tag not found\n"
                report += "- Recommend checking resource tag configuration\n\n"

            if diagnosis.get("other_available_tags"):
                report += "### Other Available Tags\n\n"
                for tag_key, tag_values in diagnosis["other_available_tags"].items():
                    report += f"#### {tag_key}\n\n"
                    report += "| Tag Value | Cost (USD) |\n"
                    report += "|-----------|------------|\n"
                    for tag_info in tag_values[:5]:  # Show only top 5
                        report += (
                            f"| `{tag_info['value']}` | ${tag_info['cost']:.2f} |\n"
                        )
                    report += "\n"

        # costsummary
        report += "---\n\n## 💰 costsummary\n\n"

        if analysis.get("cost_summary"):
            summary = analysis["cost_summary"]

            report += "### 📊 costmetrics\n\n"
            report += "| Metrics | Amount (USD) |\n"
            report += "|------|------------|\n"
            report += (
                f"| **Total Cost** | ${summary.get('total_blended_cost', 0):.2f} |\n"
            )
            report += f"| **Unblended Cost** | ${summary.get('total_unblended_cost', 0):.2f} |\n"
            report += f"| **Average Daily Cost** | ${summary.get('average_daily_cost', 0):.2f} |\n"
            report += f"| **Projected Monthly Cost** | ${summary.get('projected_monthly_cost', 0):.2f} |\n\n"

            if summary.get("note"):
                report += f"**Note**: {summary['note']}\n\n"

        # servicecostanalyze
        if analysis.get("service_breakdown"):
            report += "---\n\n## 🔧 servicecostanalyze\n\n"

            # Group by service
            service_costs = {}
            for service in analysis["service_breakdown"]:
                service_name = service["service"]
                if service_name not in service_costs:
                    service_costs[service_name] = 0
                service_costs[service_name] += service["cost"]

            sorted_services = sorted(
                service_costs.items(), key=lambda x: x[1], reverse=True
            )

            if sorted_services:
                report += "### 📈 Cost Grouped by Service\n\n"
                report += "| Service | Cost (USD) | Percentage |\n"
                report += "|------|------------|------|\n"

                total_cost = sum(cost for _, cost in sorted_services)

                for service, cost in sorted_services[:15]:  # Show top 15 services
                    percentage = (cost / total_cost * 100) if total_cost > 0 else 0
                    report += f"| {service} | ${cost:.2f} | {percentage:.1f}% |\n"

                report += "\n"

                # Cost distribution chart (text version)
                report += "### 📊 Cost Distribution\n\n"
                report += "```\n"
                for service, cost in sorted_services[:10]:
                    percentage = (cost / total_cost * 100) if total_cost > 0 else 0
                    bar_length = int(percentage / 2)  # One character per 2%
                    bar = "█" * bar_length
                    report += f"{service:<40} {bar} {percentage:.1f}%\n"
                report += "```\n\n"

        # Daily cost trends
        if analysis.get("daily_trends"):
            report += "---\n\n## 📈 Daily Cost Trends\n\n"

            daily_costs = analysis["daily_trends"]
            if daily_costs:
                report += "### 📅 Daily Cost Details\n\n"
                report += "| Date | Cost (USD) | Trend |\n"
                report += "|------|------------|------|\n"

                for i, day in enumerate(daily_costs[-14:]):  # Show last 14 days
                    trend_indicator = ""
                    if i > 0:
                        prev_cost = daily_costs[-14:][i - 1]["cost"]
                        if day["cost"] > prev_cost:
                            trend_indicator = "📈"
                        elif day["cost"] < prev_cost:
                            trend_indicator = "📉"
                        else:
                            trend_indicator = "➡️"

                    report += (
                        f"| {day['date']} | ${day['cost']:.2f} | {trend_indicator} |\n"
                    )

                report += "\n"

                # trendanalyze
                if len(daily_costs) >= 7:
                    recent_week = daily_costs[-7:]
                    recent_avg = sum(d["cost"] for d in recent_week) / len(recent_week)

                    if len(daily_costs) >= 14:
                        previous_week = daily_costs[-14:-7]
                        previous_avg = sum(d["cost"] for d in previous_week) / len(
                            previous_week
                        )

                        if previous_avg > 0:
                            trend_percentage = (
                                (recent_avg - previous_avg) / previous_avg
                            ) * 100

                            report += "### 📊 trendanalyze\n\n"
                            report += f"- **Recent Week Average**: ${recent_avg:.2f} USD/day\n"
                            report += f"- **Previous Week Average**: ${previous_avg:.2f} USD/day\n"
                            report += (
                                f"- **Trend Change**: {trend_percentage:+.1f}%\n\n"
                            )

                            if trend_percentage > 10:
                                report += "⚠️ **Warning**: Cost growing rapidly, recommend monitoring resource usage\n\n"
                            elif trend_percentage < -10:
                                report += "✅ **Good**: Cost declining significantly, optimization effects are notable\n\n"
                            else:
                                report += "📊 **Stable**: Cost relatively stable\n\n"

        # resourceanalyze
        if analysis.get("resource_analysis"):
            report += "---\n\n## 🖥️ resourceanalyze\n\n"
            resources = analysis["resource_analysis"]

            # EC2instance
            if resources.get("ec2_instances"):
                report += "### 🖥️ EC2 Instances\n\n"
                report += (
                    "| Instance ID | Type | State | CPU Utilization | Launch Time |\n"
                )
                report += "|--------|------|------|-----------|----------|\n"

                for instance in resources["ec2_instances"][:10]:  # Show top 10
                    cpu_util = instance["utilization"]["cpu_average"]
                    cpu_status = (
                        "🔴" if cpu_util < 10 else "🟡" if cpu_util < 50 else "🟢"
                    )

                    report += f"| `{instance['instance_id']}` | {instance['instance_type']} | {instance['state']} | {cpu_status} {cpu_util:.1f}% | {instance['launch_time'][:10]} |\n"

                report += "\n"

            # RDSinstance
            if resources.get("rds_instances"):
                report += "### 🗄️ RDS Instances\n\n"
                report += (
                    "| Instance Identifier | Type | Engine | Status | Storage (GB) |\n"
                )
                report += "|------------|------|------|------|----------|\n"

                for db in resources["rds_instances"][:10]:
                    report += f"| `{db['db_instance_identifier']}` | {db['db_instance_class']} | {db['engine']} {db['engine_version']} | {db['status']} | {db['allocated_storage']} |\n"

                report += "\n"

            # S3bucket
            if resources.get("s3_buckets"):
                report += "### 🪣 S3 Buckets\n\n"
                report += "| Bucket Name | Size (GB) | Creation Time |\n"
                report += "|------------|-----------|----------|\n"

                total_size = 0
                for bucket in resources["s3_buckets"][:10]:
                    total_size += bucket["size_gb"]
                    report += f"| `{bucket['name']}` | {bucket['size_gb']:.2f} | {bucket['creation_date'][:10]} |\n"

                report += f"\n**Total Storage Size**: {total_size:.2f} GB\n\n"

        # optimizerecommendation
        if analysis.get("optimization_recommendations"):
            report += "---\n\n## 💡 optimizerecommendation\n\n"

            recommendations = analysis["optimization_recommendations"]
            if recommendations:
                high_priority = [
                    r for r in recommendations if r.get("priority") == "high"
                ]
                medium_priority = [
                    r for r in recommendations if r.get("priority") == "medium"
                ]

                if high_priority:
                    report += "### 🔴 High Priority Recommendations\n\n"
                    for i, rec in enumerate(high_priority, 1):
                        report += f"#### {i}. {rec['type'].title()}\n\n"
                        report += f"- **Resource**: `{rec['resource']}`\n"
                        report += f"- **Recommendation**: {rec['recommendation']}\n"
                        report += f"- **Reason**: {rec['reason']}\n"
                        report += (
                            f"- **Potential Savings**: {rec['potential_savings']}\n\n"
                        )

                if medium_priority:
                    report += "### 🟡 Medium Priority Recommendations\n\n"
                    for i, rec in enumerate(medium_priority, 1):
                        report += f"#### {i}. {rec['type'].title()}\n\n"
                        report += f"- **Resource**: `{rec['resource']}`\n"
                        report += f"- **Recommendation**: {rec['recommendation']}\n"
                        report += f"- **Reason**: {rec['reason']}\n"
                        report += (
                            f"- **Potential Savings**: {rec['potential_savings']}\n\n"
                        )
            else:
                report += "✅ No obvious optimization opportunities found currently\n\n"

        # costforecast
        if analysis.get("forecast"):
            report += "---\n\n## 📈 costforecast\n\n"
            forecast = analysis["forecast"]

            if forecast.get("total_forecast"):
                report += "### 🔮 Future Cost Forecast\n\n"
                report += f"- **Total Forecast Cost**: ${forecast['total_forecast']:.2f} USD\n"
                report += f"- **Forecast Period**: {forecast['forecast_period']['start']} to {forecast['forecast_period']['end']}\n"
                report += f"- **Confidence Level**: {forecast.get('confidence_level', 'Medium')}\n\n"

                if forecast.get("note"):
                    report += f"**Note**: {forecast['note']}\n\n"
            elif forecast.get("error"):
                report += "### ⚠️ Forecast Limitations\n\n"
                report += f"- **Issue**: {forecast['error']}\n"
                report += f"- **Recommendation**: {forecast.get('recommendation', 'Wait for more historical data')}\n\n"

        # Tag compliance
        if analysis.get("tag_compliance"):
            report += "---\n\n## 🏷️ Tag Compliance\n\n"
            compliance = analysis["tag_compliance"]

            if compliance:
                compliance_rate = compliance.get("compliance_percentage", 0)
                status_emoji = (
                    "🟢"
                    if compliance_rate >= 90
                    else "🟡" if compliance_rate >= 70 else "🔴"
                )

                report += f"### {status_emoji} Compliance Summary\n\n"
                report += f"- **Compliance Rate**: {compliance_rate:.1f}%\n"
                report += f"- **Compliant Resources**: {compliance.get('compliant_resources', 0)}\n"
                report += f"- **Non-compliant Resources**: {compliance.get('non_compliant_resources', 0)}\n\n"

                if compliance.get("missing_tags_by_resource"):
                    report += "### 🔍 Non-compliant Resource Details\n\n"
                    report += "| Resource Type | Resource ID | Missing Tags |\n"
                    report += "|----------|--------|----------|\n"

                    for resource in compliance["missing_tags_by_resource"][:10]:
                        missing_tags = ", ".join(resource["missing_tags"])
                        report += f"| {resource['resource_type']} | `{resource['resource_id']}` | {missing_tags} |\n"

                    report += "\n"

        # anomalydetect
        if analysis.get("anomaly_detection"):
            report += "---\n\n## ⚠️ costanomalydetect\n\n"
            anomalies = analysis["anomaly_detection"]

            actual_anomalies = [a for a in anomalies if "anomaly_id" in a]

            if actual_anomalies:
                report += "### 🚨 Detected Anomalies\n\n"
                report += "| Anomaly ID | Start Time | Impact Amount | Status |\n"
                report += "|--------|----------|----------|------|\n"

                for anomaly in actual_anomalies[:5]:
                    status = "🔴 Active" if not anomaly.get("end_date") else "✅ Ended"
                    report += f"| `{anomaly['anomaly_id']}` | {anomaly['start_date']} | ${anomaly['impact']:.2f} | {status} |\n"

                report += "\n"
            else:
                info_items = [a for a in anomalies if "info" in a or "error" in a]
                if info_items:
                    report += "### ℹ️ Anomaly Detection Status\n\n"
                    for item in info_items:
                        if "info" in item:
                            report += f"- {item['info']}\n"
                        if "recommendation" in item:
                            report += (
                                f"- **recommendation**: {item['recommendation']}\n"
                            )
                        if "error" in item:
                            report += f"- **Issue**: {item['error']}\n"
                    report += "\n"

        # Reserved Instance and Savings Plans recommendations
        ri_recs = analysis.get("reserved_instance_recommendations", [])
        sp_recs = analysis.get("savings_plans_recommendations", [])

        if ri_recs or sp_recs:
            report += "---\n\n## 💰 Savings Opportunities\n\n"

            if ri_recs and any("recommended_quantity" in r for r in ri_recs):
                report += "### 🏦 Reserved Instance Recommendations\n\n"
                report += "| Instance Type | Recommended Quantity | Estimated Monthly Savings |\n"
                report += "|----------|----------|------------|\n"

                for rec in ri_recs[:5]:
                    if "recommended_quantity" in rec:
                        instance_type = rec.get("instance_details", {}).get(
                            "InstanceType", "Unknown"
                        )
                        report += f"| {instance_type} | {rec['recommended_quantity']} | ${rec['estimated_monthly_savings']:.2f} |\n"

                report += "\n"

            if sp_recs and any("hourly_commitment" in r for r in sp_recs):
                report += "### 💳 Savings Plans Recommendations\n\n"
                report += "| Type | Hourly Commitment | Estimated Savings Rate |\n"
                report += "|------|----------|------------|\n"

                for rec in sp_recs[:5]:
                    if "hourly_commitment" in rec:
                        report += f"| {rec['savings_plans_type']} | ${rec['hourly_commitment']:.2f}/hour | {rec['estimated_savings_percentage']:.1f}% |\n"

                report += "\n"

        # Summary and recommendations
        report += "---\n\n## 📋 Summary and Recommendations\n\n"

        # Generate summary based on analysis results
        cost_summary = analysis.get("cost_summary", {})
        total_cost = cost_summary.get("total_blended_cost", 0)

        if total_cost > 0:
            report += "### 💰 Cost Status\n\n"
            report += (
                f"- Current monthly cost is approximately **${total_cost:.2f} USD**\n"
            )

            daily_avg = cost_summary.get("average_daily_cost", 0)
            if daily_avg > 0:
                report += f"- Average daily cost is **${daily_avg:.2f} USD**\n"

            # costrecommendation
            if total_cost > 1000:
                report += "- 💡 Recommend regularly reviewing high-cost services to find optimization opportunities\n"
            if total_cost > 500:
                report += "- 📊 Recommend setting up cost budgets and alerts\n"

            report += "\n"

        # Optimization recommendations summary
        recommendations = analysis.get("optimization_recommendations", [])
        if recommendations:
            high_priority_count = len(
                [r for r in recommendations if r.get("priority") == "high"]
            )
            if high_priority_count > 0:
                report += "### 🎯 Priority Action Items\n\n"
                report += f"- Found **{high_priority_count}** high-priority optimization opportunities\n"
                report += (
                    "- Recommend prioritizing instances with low CPU utilization\n\n"
                )

        # Tag management recommendations
        compliance = analysis.get("tag_compliance", {})
        if compliance and compliance.get("compliance_percentage", 100) < 90:
            report += "### 🏷️ Tag Management\n\n"
            report += f"- Current tag compliance rate is {compliance.get('compliance_percentage', 0):.1f}%\n"
            report += "- Recommend improving resource tags for better cost analysis and management\n\n"

        report += "### 📞 Support\n\n"
        report += "For further cost optimization recommendations, please:\n"
        report += "1. Run this analysis report regularly\n"
        report += "2. Monitor cost trend changes\n"
        report += "3. Respond promptly to anomaly alerts\n"
        report += "4. Consider using AWS Cost Explorer for deeper analysis\n\n"

        report += f"---\n\n*Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"

        return report

    def create_cost_dashboard_data(self) -> Dict[str, Any]:
        """Create dashboard data"""
        analysis = self.get_comprehensive_cost_analysis()

        # Prepare chart data
        dashboard_data = {
            "daily_costs": analysis.get("daily_trends", []),
            "service_breakdown": analysis.get("service_breakdown", []),
            "optimization_summary": {
                "total_recommendations": len(
                    analysis.get("optimization_recommendations", [])
                ),
                "high_priority": len(
                    [
                        r
                        for r in analysis.get("optimization_recommendations", [])
                        if r.get("priority") == "high"
                    ]
                ),
                "potential_savings": sum(
                    [
                        float(
                            r.get("potential_savings", "0")
                            .replace("Up to ", "")
                            .replace("% cost reduction", "")
                        )
                        for r in analysis.get("optimization_recommendations", [])
                        if "cost reduction" in r.get("potential_savings", "")
                    ]
                ),
            },
            "compliance_score": analysis.get("tag_compliance", {}).get(
                "compliance_percentage", 0
            ),
            "forecast_data": analysis.get("forecast", {}),
        }

        return dashboard_data


def main():
    """Main function - example usage"""
    try:
        print("🚀 Starting advanced cost analyzer...")

        config = CostAnalysisConfig(
            deployment_name="lakehouse-core-kolya",  # Use correct deployment_name
            workspace="kolya",
            region="us-west-2",
            days_back=30,
            forecast_days=30,
        )

        print(f"📋 Configuration: {config.deployment_name} ({config.workspace})")

        analyzer = AdvancedCostAnalyzer(config)

        # Generate report
        print("Generating cost analysis report...")
        report = analyzer.generate_comprehensive_report()
        print(report)

        # Export JSON
        print("\nExporting JSON data...")
        json_file = analyzer.export_to_json()
        print(f"JSON data exported to: {json_file}")

        # Export Markdown report
        print("\nExporting Markdown report...")
        md_file = analyzer.export_to_markdown()
        print(f"Brief report exported to: {md_file}")

        # Export detailed Markdown report
        detailed_md_file = analyzer.export_detailed_markdown()
        print(f"Detailed report exported to: {detailed_md_file}")

        # Get dashboard data
        print("\nPreparing dashboard data...")
        dashboard_data = analyzer.create_cost_dashboard_data()
        print(
            f"Dashboard data preparation complete, contains {len(dashboard_data)} datasets"
        )

    except Exception as e:
        print(f"Error occurred during execution: {str(e)}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
