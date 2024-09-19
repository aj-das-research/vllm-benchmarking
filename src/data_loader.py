import json
from typing import List, Dict, Any

class DataLoader:
    def __init__(self, dataset_path: str):
        self.dataset_path = dataset_path

    def load_datasets(self) -> List[Dict[str, Any]]:
        with open(self.dataset_path, 'r') as f:
            datasets = json.load(f)
        
        # Ensure the loaded data is in the correct format
        if not isinstance(datasets, list):
            datasets = [{"name": "dataset1", "data": datasets}]
        
        return datasets