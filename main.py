import yaml
from src.benchmarker import Benchmarker
from src.data_loader import DataLoader
from src.vllm_client import VLLMClient
from src.metrics_collector import MetricsCollector
from src.storage.file_storage import FileStorage
from src.storage.database_storage import DatabaseStorage
from src.metrics_logger import MetricsLogger
from src.resource_monitor import ResourceMonitor
from src.visualization.app import create_app
from flask_socketio import SocketIO # type: ignore
import threading

def load_config(config_path):
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def run_benchmark(benchmarker, max_concurrent):
    benchmarker.run_benchmark(max_concurrent=max_concurrent)

def main():
    config = load_config('config.yaml')
    
    data_loader = DataLoader(config['dataset_path'])
    vllm_client = VLLMClient(config['vllm_endpoint'])
    metrics_collector = MetricsCollector(config['vllm_metrics_endpoint'])
    
    file_storage = FileStorage(config['output_file_path'])
    db_storage = DatabaseStorage(config['database_url'])
    
    app, socketio = create_app()
    
    metrics_logger = MetricsLogger(config['database_url'], socketio)
    app.config['metrics_logger'] = metrics_logger
    
    resource_monitor = ResourceMonitor(config.get('monitoring_interval', 5), metrics_logger)
    
    benchmarker = Benchmarker(
        data_loader=data_loader,
        vllm_client=vllm_client,
        metrics_collector=metrics_collector,
        result_storage=file_storage,
        metrics_storage=db_storage,
        metrics_logger=metrics_logger
    )
    
    # Start resource monitoring
    resource_monitor.start()
    
    # Run benchmark in a separate thread
    benchmark_thread = threading.Thread(target=run_benchmark, args=(benchmarker, config.get('max_concurrent_requests', 5)))
    benchmark_thread.start()
    
    print("Benchmark started. Access the dashboard at http://localhost:5000")
    
    # Run the Flask app with SocketIO
    socketio.run(app, debug=False, use_reloader=False)

if __name__ == "__main__":
    main()