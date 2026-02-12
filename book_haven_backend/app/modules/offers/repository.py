from app.db import get_db_cursor
from psycopg2.extras import RealDictCursor

def create_book_offer(offer_type, price, condition, quantity, user_id, book_id, 
                     latitude=None, longitude=None, is_active=True):
    """Create a new book offer"""
    with get_db_cursor(commit=True) as cur:
        cur.execute("""
            INSERT INTO book_offer (offer_type, price, condition, quantity, latitude, 
                                   longitude, is_active, user_id, book_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id, offer_type, price, condition, quantity, latitude, longitude, 
                     is_active, user_id, book_id
        """, (offer_type, price, condition, quantity, latitude, longitude, is_active, 
              user_id, book_id))
        return cur.fetchone()

def get_book_offer_by_id(offer_id):
    """Get book offer by ID"""
    with get_db_cursor() as cur:
        cur.execute("""
            SELECT bo.id, bo.offer_type, bo.price, bo.condition, bo.quantity, 
                   bo.latitude, bo.longitude, bo.is_active, bo.user_id, bo.book_id,
                   b.title as book_title, b.author as book_author, b.isbn,
                   u.username as seller_username
            FROM book_offer bo
            LEFT JOIN book b ON bo.book_id = b.id
            LEFT JOIN app_user u ON bo.user_id = u.id
            WHERE bo.id = %s
        """, (offer_id,))
        return cur.fetchone()

def get_all_book_offers(limit=100, offset=0, offer_type=None, is_active=None):
    """Get all book offers with pagination and optional filters"""
    with get_db_cursor() as cur:
        query = """
            SELECT bo.id, bo.offer_type, bo.price, bo.condition, bo.quantity, 
                   bo.latitude, bo.longitude, bo.is_active, bo.user_id, bo.book_id,
                   b.title as book_title, b.author as book_author, b.isbn,
                   u.username as seller_username
            FROM book_offer bo
            LEFT JOIN book b ON bo.book_id = b.id
            LEFT JOIN app_user u ON bo.user_id = u.id
            WHERE 1=1
        """
        params = []
        
        if offer_type:
            query += " AND bo.offer_type = %s"
            params.append(offer_type)
        
        if is_active is not None:
            query += " AND bo.is_active = %s"
            params.append(is_active)
        
        query += " ORDER BY bo.id DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        
        cur.execute(query, params)
        return cur.fetchall()

def get_offers_by_user(user_id, limit=100, offset=0):
    """Get all offers by a specific user"""
    with get_db_cursor() as cur:
        cur.execute("""
            SELECT bo.id, bo.offer_type, bo.price, bo.condition, bo.quantity, 
                   bo.latitude, bo.longitude, bo.is_active, bo.user_id, bo.book_id,
                   b.title as book_title, b.author as book_author, b.isbn
            FROM book_offer bo
            LEFT JOIN book b ON bo.book_id = b.id
            WHERE bo.user_id = %s
            ORDER BY bo.id DESC
            LIMIT %s OFFSET %s
        """, (user_id, limit, offset))
        return cur.fetchall()

def get_offers_by_book(book_id, limit=100, offset=0, is_active=None):
    """Get all offers for a specific book"""
    with get_db_cursor() as cur:
        query = """
            SELECT bo.id, bo.offer_type, bo.price, bo.condition, bo.quantity, 
                   bo.latitude, bo.longitude, bo.is_active, bo.user_id, bo.book_id,
                   u.username as seller_username
            FROM book_offer bo
            LEFT JOIN app_user u ON bo.user_id = u.id
            WHERE bo.book_id = %s
        """
        params = [book_id]
        
        if is_active is not None:
            query += " AND bo.is_active = %s"
            params.append(is_active)
        
        query += " ORDER BY bo.id DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        
        cur.execute(query, params)
        return cur.fetchall()

def update_book_offer(offer_id, **kwargs):
    """Update book offer information"""
    allowed_fields = ['offer_type', 'price', 'condition', 'quantity', 'latitude', 
                     'longitude', 'is_active']
    updates = {k: v for k, v in kwargs.items() if k in allowed_fields and v is not None}
    
    if not updates:
        return None
    
    set_clause = ', '.join([f"{k} = %s" for k in updates.keys()])
    values = list(updates.values()) + [offer_id]
    
    with get_db_cursor(commit=True) as cur:
        cur.execute(f"""
            UPDATE book_offer
            SET {set_clause}
            WHERE id = %s
            RETURNING id, offer_type, price, condition, quantity, latitude, longitude, 
                     is_active, user_id, book_id
        """, values)
        return cur.fetchone()

def delete_book_offer(offer_id):
    """Delete a book offer"""
    with get_db_cursor(commit=True) as cur:
        cur.execute("DELETE FROM book_offer WHERE id = %s RETURNING id", (offer_id,))
        return cur.fetchone() is not None

def count_book_offers(offer_type=None, is_active=None):
    """Get total count of book offers"""
    with get_db_cursor() as cur:
        query = "SELECT COUNT(*) FROM book_offer WHERE 1=1"
        params = []
        
        if offer_type:
            query += " AND offer_type = %s"
            params.append(offer_type)
        
        if is_active is not None:
            query += " AND is_active = %s"
            params.append(is_active)
        
        cur.execute(query, params)
        return cur.fetchone()[0]
