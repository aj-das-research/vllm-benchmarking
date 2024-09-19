import requests
from typing import Dict, Any
import time
import random

class MetricsCollector:
    def __init__(self, metrics_endpoint: str, max_retries: int = 3, timeout: int = 900):
        self.metrics_endpoint = metrics_endpoint
        self.max_retries = max_retries
        self.timeout = timeout

    def collect_metrics(self) -> Dict[str, Any]:
        for attempt in range(self.max_retries):
            try:
                response = requests.get(self.metrics_endpoint, timeout=self.timeout)
                response.raise_for_status()
                return response.json()
            except requests.RequestException as e:
                print(f"Error collecting metrics (attempt {attempt + 1}/{self.max_retries}): {e}")
                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    print(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    print("Max retries reached. Simulating metrics.")
                    return self._simulate_metrics()

    def _simulate_metrics(self) -> Dict[str, Any]:
        return {
            "requests_per_second": random.uniform(10, 50),
            "average_latency": random.uniform(0.1, 0.5),
            "error_rate": random.uniform(0, 0.05),
            "simulated": True
        }