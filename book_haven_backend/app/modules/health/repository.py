from app.db import db_healthcheck

def check_database():
    """Check if database connection is healthy"""
    try:
        return db_healthcheck()
    except Exception as e:
        return False