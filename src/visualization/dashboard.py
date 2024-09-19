import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
from flask import current_app
from datetime import datetime

def create_dashboard():
    metrics_logger = current_app.config['metrics_logger']
    benchmark_results = metrics_logger.get_benchmark_results()
    resource_usage = metrics_logger.get_resource_usage()
    
    benchmark_plot = create_benchmark_plot(benchmark_results)
    resource_plot = create_resource_usage_plot(resource_usage)
    
    return f"""
    <html>
        <head>
            <title>vLLM Benchmark Monitor</title>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f0f0f0; }}
                h1 {{ color: #333; }}
                .plot {{ background-color: white; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); margin-bottom: 20px; padding: 20px; }}
            </style>
        </head>
        <body>
            <h1>vLLM Benchmark Monitor</h1>
            <div id="benchmark-plot" class="plot"></div>
            <div id="resource-plot" class="plot"></div>
            <script>
                var socket = io();
                var benchmarkPlot = {benchmark_plot};
                var resourcePlot = {resource_plot};
                
                Plotly.newPlot('benchmark-plot', benchmarkPlot.data, benchmarkPlot.layout);
                Plotly.newPlot('resource-plot', resourcePlot.data, resourcePlot.layout);
                
                socket.on('new_benchmark_result', function(data) {{
                    Plotly.extendTraces('benchmark-plot', {{
                        x: [[data.timestamp], [data.timestamp], [data.timestamp]],
                        y: [[data.avg_latency], [data.throughput], [data.error_rate]]
                    }}, [0, 1, 2]);
                }});
                
                socket.on('new_resource_usage', function(data) {{
                    Plotly.extendTraces('resource-plot', {{
                        x: [[data.timestamp], [data.timestamp], [data.timestamp]],
                        y: [[data.cpu_percent], [data.memory_percent], [data.gpu_percent]]
                    }}, [0, 1, 2]);
                }});
            </script>
        </body>
    </html>
    """

def create_benchmark_plot(benchmark_results):
    fig = make_subplots(rows=2, cols=2, subplot_titles=("Average Latency", "Throughput", "Error Rate"))
    
    models = list(set(result.model_name for result in benchmark_results))
    
    for model in models:
        model_results = [r for r in benchmark_results if r.model_name == model]
        x = [r.timestamp.isoformat() for r in model_results]
        
        fig.add_trace(go.Scatter(x=x, y=[r.avg_latency for r in model_results], name=f"{model} - Latency"), row=1, col=1)
        fig.add_trace(go.Scatter(x=x, y=[r.throughput for r in model_results], name=f"{model} - Throughput"), row=1, col=2)
        fig.add_trace(go.Scatter(x=x, y=[r.error_rate for r in model_results], name=f"{model} - Error Rate"), row=2, col=1)
    
    fig.update_layout(height=800, width=1000, title_text="Benchmark Results")
    return fig.to_json()

def create_resource_usage_plot(resource_usage):
    fig = go.Figure()
    
    x = [u.timestamp.isoformat() for u in resource_usage]
    
    fig.add_trace(go.Scatter(x=x, y=[u.cpu_percent for u in resource_usage], name="CPU Usage"))
    fig.add_trace(go.Scatter(x=x, y=[u.memory_percent for u in resource_usage], name="Memory Usage"))
    fig.add_trace(go.Scatter(x=x, y=[u.gpu_percent for u in resource_usage], name="GPU Usage"))
    
    fig.update_layout(height=400, width=1000, title_text="Resource Usage")
    return fig.to_json()