from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from flask_socketio import SocketIO # type: ignore

Base = declarative_base()

class BenchmarkResult(Base):
    __tablename__ = 'benchmark_results'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    model_name = Column(String)
    dataset_name = Column(String)
    avg_latency = Column(Float)
    throughput = Column(Float)
    error_rate = Column(Float)

class ResourceUsage(Base):
    __tablename__ = 'resource_usage'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    cpu_percent = Column(Float)
    memory_percent = Column(Float)
    gpu_percent = Column(Float)

class MetricsLogger:
    def __init__(self, database_url, socketio):
        self.engine = create_engine(database_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.socketio = socketio
    
    def log_benchmark_result(self, model_name, dataset_name, avg_latency, throughput, error_rate):
        session = self.Session()
        result = BenchmarkResult(
            model_name=model_name,
            dataset_name=dataset_name,
            avg_latency=avg_latency,
            throughput=throughput,
            error_rate=error_rate
        )
        session.add(result)
        session.commit()
        session.close()
        
        # Emit the new result to connected clients
        self.socketio.emit('new_benchmark_result', {
            'model_name': model_name,
            'dataset_name': dataset_name,
            'avg_latency': avg_latency,
            'throughput': throughput,
            'error_rate': error_rate,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    def log_resource_usage(self, cpu_percent, memory_percent, gpu_percent):
        session = self.Session()
        usage = ResourceUsage(
            cpu_percent=cpu_percent,
            memory_percent=memory_percent,
            gpu_percent=gpu_percent
        )
        session.add(usage)
        session.commit()
        session.close()
        
        # Emit the new resource usage to connected clients
        self.socketio.emit('new_resource_usage', {
            'cpu_percent': cpu_percent,
            'memory_percent': memory_percent,
            'gpu_percent': gpu_percent,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    def get_benchmark_results(self):
        session = self.Session()
        results = session.query(BenchmarkResult).all()
        session.close()
        return results
    
    def get_resource_usage(self):
        session = self.Session()
        usage = session.query(ResourceUsage).all()
        session.close()
        return usage