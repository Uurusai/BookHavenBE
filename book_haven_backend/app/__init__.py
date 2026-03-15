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
    from app.modules.communities import communities_bp
    from app.modules.books import books_bp
    from app.modules.offers import offers_bp
    from app.modules.transactions import transactions_bp
    from app.modules.chat import chat_bp
    
    app.register_blueprint(health_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(communities_bp)
    app.register_blueprint(books_bp)
    app.register_blueprint(offers_bp)
    app.register_blueprint(transactions_bp)
    app.register_blueprint(chat_bp)
    
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