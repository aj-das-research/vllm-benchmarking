import json
import os
from typing import List, Dict, Any

class FileStorage:
    def __init__(self, file_path: str):
        self.file_path = file_path
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)

    def store_results(self, dataset_name: str, results: List[Dict[str, Any]]):
        full_path = f"{self.file_path}_{dataset_name}.json"
        with open(full_path, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"Results for dataset '{dataset_name}' stored in {full_path}")