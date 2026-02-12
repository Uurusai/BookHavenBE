from flask import Flask
from app.config import Config
from app.db import init_pool, close_pool
import atexit

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize database connection pool
    init_pool()
    
    # Register cleanup function
    atexit.register(close_pool)
    
    # Register CLI commands
    from app import cli
    cli.init_app(app)
    
    # Register blueprints
    from app.modules.health import health_bp
    from app.modules.users import users_bp
    
    app.register_blueprint(health_bp)
    app.register_blueprint(users_bp)
    
    @app.route('/')
    def index():
        return {
            "message": "Book Haven API",
            "version": "1.0.0",
            "status": "running",
            "endpoints": {
                "health": "/api/health",
                "users": "/api/users"
            }
        }
    
    return app