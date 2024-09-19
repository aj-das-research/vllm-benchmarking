from flask import Flask
from flask_socketio import SocketIO # type: ignore
from .dashboard import create_dashboard

def create_app():
    app = Flask(__name__)
    socketio = SocketIO(app)
    
    @app.route('/')
    def index():
        return create_dashboard()
    
    return app, socketio