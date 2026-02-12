"""Blueprint registration module"""

def register_blueprints(app):
    """Register all application blueprints"""
    from app.modules.health import health_bp
    
    # Register blueprints
    app.register_blueprint(health_bp)
    
    # Future blueprints can be registered here
    # from app.modules.users.routes import users_bp
    # app.register_blueprint(users_bp)
    # from app.modules.books.routes import books_bp
    # app.register_blueprint(books_bp)
    
    return app