import os
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from typing import Dict, Any

class DatabaseStorage:
    def __init__(self, database_url: str):
        db_path = database_url.replace('sqlite:///', '')
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.engine = sa.create_engine(database_url)
        self.Session = sessionmaker(bind=self.engine)
        self._create_tables()

    def _create_tables(self):
        metadata = sa.MetaData()
        
        sa.Table('benchmark_metrics', metadata,
                 sa.Column('id', sa.Integer, primary_key=True),
                 sa.Column('dataset_name', sa.String),
                 sa.Column('metric_name', sa.String),
                 sa.Column('metric_value', sa.Float)
        )
        
        sa.Table('vllm_metrics', metadata,
                 sa.Column('id', sa.Integer, primary_key=True),
                 sa.Column('dataset_name', sa.String),
                 sa.Column('metric_name', sa.String),
                 sa.Column('metric_value', sa.Float)
        )
        
        metadata.create_all(self.engine)

    def store_metrics(self, dataset_name: str, vllm_metrics: Dict[str, Any], benchmark_metrics: Dict[str, Any]):
        session = self.Session()
        
        try:
            for name, value in vllm_metrics.items():
                session.execute(sa.text(
                    "INSERT INTO vllm_metrics (dataset_name, metric_name, metric_value) VALUES (:dataset, :name, :value)"
                ), {"dataset": dataset_name, "name": name, "value": value})
            
            for name, value in benchmark_metrics.items():
                session.execute(sa.text(
                    "INSERT INTO benchmark_metrics (dataset_name, metric_name, metric_value) VALUES (:dataset, :name, :value)"
                ), {"dataset": dataset_name, "name": name, "value": value})
            
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()