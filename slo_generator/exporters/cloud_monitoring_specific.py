# Copyright 2019 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#            http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
`cloud_monitoring.py`
Cloud Monitoring exporter class.
"""
import logging

from google.cloud import monitoring_v3

from .base import MetricsExporter

LOGGER = logging.getLogger(__name__)


class CloudMonitoringSpecificExporter(MetricsExporter):
    """Cloud Monitoring exporter class."""
    METRIC_PREFIX = "custom.googleapis.com/slo_generator/"
    REQUIRED_FIELDS = ['project_id']

    def __init__(self):
        self.client = monitoring_v3.MetricServiceClient()

    def export_metric(self, data):
        """Export metric to Cloud Monitoring. Create metric descriptor if
        it doesn't exist.

        Args:
            data (dict): Data to send to Cloud Monitoring.
            project_id (str): Cloud Monitoring project id.

        Returns:
            object: Cloud Monitoring API result.
        """
        self.create_timeseries(data)

    def create_timeseries(self, data):
        """Create Cloud Monitoring timeseries.

        Args:
            data (dict): Metric data.

        Returns:
            object: Metric descriptor.
        """
        series = monitoring_v3.TimeSeries()
        series.metric.type = data["name"]
        series.resource.type = "global"
        labels = data["labels"]
        for key, value in labels.items():
            if key == "slo_name" or key == "product_name" or key == "slo_type" or key == "env" or key == "product_id"  or key == "service_name" or key == "platform" or key == "client_coverage" or key == "slo_statement" or key == "feature_name" or key == "module_id" or key == "community" or key == "domain" or key == "error_budget_policy_step_name" or key == "entity":
                series.metric.labels[key] = value
    
        # Define end point timestamp.
        timestamp = data["timestamp"]
        seconds = int(timestamp)
        nanos = int((timestamp - seconds) * 10**9)
        interval = monitoring_v3.TimeInterval(
            {
                "end_time": {
                    "seconds": seconds,
                    "nanos": nanos,
                }
            }
        )

        # Create a new data point and set the metric value.
        point = monitoring_v3.Point(
            {
                "interval": interval,
                "value": {
                    "double_value": data["value"],
                },
            }
        )
        series.points = [point]

        
        project = self.client.common_project_path(data["project_id"])
        self.client.create_time_series(name=project, time_series=[series])
        # pylint: disable=E1101
        labels = series.metric.labels
        LOGGER.debug(
            f"timestamp: {timestamp}"
            f"value: {point.value.double_value}"
            f"{labels['service_name']}-{labels['feature_name']}-"
            f"{labels['slo_name']}-{labels['error_budget_policy_step_name']}"
        )

    

   