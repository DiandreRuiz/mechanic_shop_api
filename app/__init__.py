from flask import Flask
from extensions import ma, db

def create_app(config_name: str):
    app = Flask(__name__)
    
    # Import appropriate config
    app.config.from_object(f"config.{config_name}")
    
    # Initialize Extensions
    ma.init_app(app)
    db.init_app(app)
    
    # Register Blueprints
    
    return app