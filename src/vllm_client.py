import requests
from typing import Dict, Any
import time
import random

class VLLMClient:
    def __init__(self, endpoint: str, api_key: str = None, max_retries: int = 3, timeout: int = 900):
        self.endpoint = endpoint
        self.api_key = api_key
        self.max_retries = max_retries
        self.timeout = timeout

    def send_request(self, input_text: str) -> Dict[str, Any]:
        headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    self.endpoint,
                    json={"prompt": input_text},
                    headers=headers,
                    timeout=self.timeout
                )
                response.raise_for_status()
                return response.json()
            except requests.RequestException as e:
                print(f"Error sending request (attempt {attempt + 1}/{self.max_retries}): {e}")
                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    print(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    print("Max retries reached. Simulating response.")
                    return self._simulate_response(input_text)

    def _simulate_response(self, input_text: str) -> Dict[str, Any]:
        # Simulate a response with some random latency
        time.sleep(random.uniform(0.5, 2.0))
        return {
            "generated_text": f"Simulated response for: {input_text[:30]}...",
            "simulated": True
        }