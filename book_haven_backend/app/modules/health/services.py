from app.modules.health import repository

def get_health_status():
    """Get overall health status of the application"""
    db_status = repository.check_database()
    
    return {
        "status": "healthy" if db_status else "unhealthy",
        "database": "connected" if db_status else "disconnected"
    }