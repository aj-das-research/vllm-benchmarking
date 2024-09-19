import psutil
import time
import threading

class ResourceMonitor:
    def __init__(self, interval, metrics_logger):
        self.interval = interval
        self.metrics_logger = metrics_logger
        self.stop_event = threading.Event()
    
    def monitor(self):
        while not self.stop_event.is_set():
            cpu_percent = psutil.cpu_percent()
            memory_percent = psutil.virtual_memory().percent
            # Note: GPU monitoring requires additional setup and possibly a library like pynvml
            gpu_percent = 0  # Placeholder for GPU usage
            
            self.metrics_logger.log_resource_usage(cpu_percent, memory_percent, gpu_percent)
            
            time.sleep(self.interval)
    
    def start(self):
        self.thread = threading.Thread(target=self.monitor)
        self.thread.start()
    
    def stop(self):
        self.stop_event.set()
        self.thread.join()