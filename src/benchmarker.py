import time
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

class Benchmarker:
    def __init__(self, data_loader, vllm_client, metrics_collector, result_storage, metrics_storage, metrics_logger):
        self.data_loader = data_loader
        self.vllm_client = vllm_client
        self.metrics_collector = metrics_collector
        self.result_storage = result_storage
        self.metrics_storage = metrics_storage
        self.metrics_logger = metrics_logger


    def run_benchmark(self, max_concurrent=5):
        datasets = self.data_loader.load_datasets()
        for dataset in datasets:
            dataset_name = dataset.get('name', 'unnamed_dataset')
            print(f"Benchmarking dataset: {dataset_name}")
            self._benchmark_dataset(dataset_name, dataset['data'], max_concurrent)

    def _benchmark_dataset(self, dataset_name, dataset, max_concurrent):
        results = []
        start_time = time.time()

        with ThreadPoolExecutor(max_workers=max_concurrent) as executor:
            future_to_prompt = {executor.submit(self._send_request, item['input']): item['input'] for item in dataset}
            for future in as_completed(future_to_prompt):
                results.append(future.result())

        end_time = time.time()
        total_time = end_time - start_time

        self.result_storage.store_results(dataset_name, results)
        
        vllm_metrics = self.metrics_collector.collect_metrics()
        benchmark_metrics = self._calculate_benchmark_metrics(results, total_time)
        
        self.metrics_storage.store_metrics(dataset_name, vllm_metrics, benchmark_metrics)

        print(f"Benchmark for dataset '{dataset_name}' completed.")
        print(f"Total time: {total_time:.2f} seconds")
        print(f"Average latency: {benchmark_metrics['avg_latency']:.2f} seconds")
        print(f"Throughput: {benchmark_metrics['throughput']:.2f} requests/second")
        if any('simulated' in r.get('output', {}) for r in results):
            print("Note: Some or all responses were simulated due to endpoint errors.")

        # Log the benchmark result
        self.metrics_logger.log_benchmark_result(
            model_name="YourModelName",  # Replace with actual model name
            dataset_name=dataset_name,
            avg_latency=benchmark_metrics['avg_latency'],
            throughput=benchmark_metrics['throughput'],
            error_rate=0.0  # You may need to calculate this
        )

    def _send_request(self, prompt: str) -> Dict[str, Any]:
        start_time = time.time()
        response = self.vllm_client.send_request(prompt)
        end_time = time.time()
        return {
            'input': prompt,
            'output': response,
            'latency': end_time - start_time
        }

    def _calculate_benchmark_metrics(self, results: List[Dict[str, Any]], total_time: float) -> Dict[str, float]:
        latencies = [r['latency'] for r in results]
        return {
            'total_requests': len(results),
            'total_time': total_time,
            'avg_latency': sum(latencies) / len(latencies) if latencies else 0,
            'min_latency': min(latencies) if latencies else 0,
            'max_latency': max(latencies) if latencies else 0,
            'throughput': len(results) / total_time if total_time > 0 else 0
        }