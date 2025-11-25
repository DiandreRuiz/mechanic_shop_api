from flask import Flask
from app.extensions import ma, db
from app.blueprints.customers import customers_bp

def create_app(config_name: str):
    app = Flask(__name__)
    
    # Import appropriate config
    app.config.from_object(f"config.{config_name}")
    
    # Initialize Extensions
    ma.init_app(app)
    db.init_app(app)
    
    # Register Blueprints
    app.register_blueprint(customers_bp, url_prefix="/customers")
    
    return app