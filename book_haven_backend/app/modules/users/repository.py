from app.db import get_db_cursor
from psycopg2.extras import RealDictCursor

def create_user(username, email, password_hash, role='user', full_name=None, city=None, country=None, latitude=None, longitude=None):
    """Create a new user in the database"""
    with get_db_cursor(commit=True) as cur:
        cur.execute("""
            INSERT INTO app_user (username, email, password_hash, role, full_name, city, country, latitude, longitude)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id, username, email, role, full_name, city, country, latitude, longitude, trust_score
        """, (username, email, password_hash, role, full_name, city, country, latitude, longitude))
        return cur.fetchone()

def update_user_location(user_id, latitude, longitude):
    """Update user's location"""
    with get_db_cursor(commit=True) as cur:
        cur.execute("""
            UPDATE app_user
            SET latitude = %s, longitude = %s
            WHERE id = %s
            RETURNING id, latitude, longitude
        """, (latitude, longitude, user_id))
        return cur.fetchone()

def get_user_by_id(user_id):
    """Get user by ID"""
    with get_db_cursor() as cur:
        cur.execute("""
            SELECT id, username, email, role, full_name, city, country, latitude, longitude, trust_score
            FROM app_user
            WHERE id = %s
        """, (user_id,))
        return cur.fetchone()

def get_user_by_username(username):
    """Get user by username"""
    with get_db_cursor() as cur:
        cur.execute("""
            SELECT id, username, email, role, full_name, city, country
            FROM app_user
            WHERE username = %s
        """, (username,))
        return cur.fetchone()

def get_user_by_email(email):
    """Get user by email"""
    with get_db_cursor() as cur:
        cur.execute("""
            SELECT id, username, email, role, full_name, city, country
            FROM app_user
            WHERE email = %s
        """, (email,))
        return cur.fetchone()

def get_user_with_password(username):
    """Get user with password hash for authentication"""
    with get_db_cursor() as cur:
        cur.execute("""
            SELECT id, username, email, password_hash, role, full_name, city, country
            FROM app_user
            WHERE username = %s
        """, (username,))
        return cur.fetchone()

def get_all_users(limit=100, offset=0):
    """Get all users with pagination"""
    with get_db_cursor() as cur:
        cur.execute("""
            SELECT id, username, email, role, full_name, city, country
            FROM app_user
            ORDER BY id
            LIMIT %s OFFSET %s
        """, (limit, offset))
        return cur.fetchall()

def update_user(user_id, **kwargs):
    """Update user information"""
    allowed_fields = ['username', 'email', 'full_name', 'city', 'country', 'role']
    updates = {k: v for k, v in kwargs.items() if k in allowed_fields and v is not None}
    
    if not updates:
        return None
    
    set_clause = ', '.join([f"{k} = %s" for k in updates.keys()])
    values = list(updates.values()) + [user_id]
    
    with get_db_cursor(commit=True) as cur:
        cur.execute(f"""
            UPDATE app_user
            SET {set_clause}
            WHERE id = %s
            RETURNING id, username, email, role, full_name, city, country
        """, values)
        return cur.fetchone()

def delete_user(user_id):
    """Delete a user"""
    with get_db_cursor(commit=True) as cur:
        cur.execute("DELETE FROM app_user WHERE id = %s RETURNING id", (user_id,))
        return cur.fetchone() is not None

def count_users():
    """Get total count of users"""
    with get_db_cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM app_user")
        return cur.fetchone()[0]

def get_users_nearby(latitude, longitude, radius_km=50, limit=20):
    """Get users within a specific radius using Haversine formula"""
    with get_db_cursor() as cur:
        # SQL Haversine implementation
        # 6371 is Earth's radius in km
        query = """
            SELECT id, username, email, role, full_name, city, country, latitude, longitude, trust_score,
            (
                6371 * acos(
                    cos(radians(%s)) * cos(radians(latitude)) * cos(radians(longitude) - radians(%s)) +
                    sin(radians(%s)) * sin(radians(latitude))
                )
            ) AS distance
            FROM app_user
            WHERE latitude IS NOT NULL AND longitude IS NOT NULL
            AND (
                6371 * acos(
                    cos(radians(%s)) * cos(radians(latitude)) * cos(radians(longitude) - radians(%s)) +
                    sin(radians(%s)) * sin(radians(latitude))
                )
            ) <= %s
            ORDER BY distance ASC
            LIMIT %s
        """
        cur.execute(query, (latitude, longitude, latitude, latitude, longitude, latitude, radius_km, limit))
        return cur.fetchall()