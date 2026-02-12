import os
import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager

# Global connection pool
_connection_pool = None

def init_pool():
    """Initialize the PostgreSQL connection pool"""
    global _connection_pool
    if _connection_pool is None:
        _connection_pool = psycopg2.pool.SimpleConnectionPool(
            minconn=1,
            maxconn=10,
            host=os.getenv('DB_HOST', 'localhost'),
            port=os.getenv('DB_PORT', '5432'),
            database=os.getenv('DB_NAME', 'book_haven'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', '')
        )
    return _connection_pool

def get_conn():
    """Get a connection from the pool"""
    if _connection_pool is None:
        init_pool()
    return _connection_pool.getconn()

def put_conn(conn):
    """Return a connection to the pool"""
    if _connection_pool is not None:
        _connection_pool.putconn(conn)

def close_pool():
    """Close all connections in the pool"""
    global _connection_pool
    if _connection_pool is not None:
        _connection_pool.closeall()
        _connection_pool = None

@contextmanager
def get_db_cursor(commit=False):
    """Context manager for database operations"""
    conn = get_conn()
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        yield cur
        if commit:
            conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        put_conn(conn)
