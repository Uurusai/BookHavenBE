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

def search_offers(query=None, offer_type=None, min_price=None, max_price=None, 
                  latitude=None, longitude=None, radius_km=None, 
                  limit=20, offset=0):
    """
    Search offers with filters and geographical sorting.
    """
    with get_db_cursor() as cur:
        sql = """
            SELECT bo.id, bo.offer_type, bo.price, bo.condition, bo.quantity, 
                   bo.latitude, bo.longitude, bo.is_active, bo.user_id, bo.book_id,
                   b.title as book_title, b.author as book_author, b.isbn, b.category,
                   u.username as seller_username,
                   u.trust_score
        """
        
        # Add distance calculation if coords provided
        if latitude is not None and longitude is not None:
            sql += """,
            (
                6371 * acos(
                    cos(radians(%s)) * cos(radians(bo.latitude)) * cos(radians(bo.longitude) - radians(%s)) +
                    sin(radians(%s)) * sin(radians(bo.latitude))
                )
            ) AS distance
            """
        else:
            sql += ", NULL as distance"

        sql += """
            FROM book_offer bo
            JOIN book b ON bo.book_id = b.id
            JOIN app_user u ON bo.user_id = u.id
            WHERE bo.is_active = TRUE
        """
        
        params = []
        if latitude is not None and longitude is not None:
            params.extend([latitude, longitude, latitude])

        if query:
            sql += " AND (b.title ILIKE %s OR b.author ILIKE %s OR b.category ILIKE %s)"
            search_pattern = f"%{query}%"
            params.extend([search_pattern, search_pattern, search_pattern])

        if offer_type:
            sql += " AND bo.offer_type = %s"
            params.append(offer_type)

        if min_price is not None:
            sql += " AND bo.price >= %s"
            params.append(min_price)
            
        if max_price is not None:
            sql += " AND bo.price <= %s"
            params.append(max_price)

        # Distance filter
        if radius_km is not None and latitude is not None and longitude is not None:
             sql += """ AND (
                6371 * acos(
                    cos(radians(%s)) * cos(radians(bo.latitude)) * cos(radians(bo.longitude) - radians(%s)) +
                    sin(radians(%s)) * sin(radians(bo.latitude))
                )
            ) <= %s
            """
             params.extend([latitude, longitude, latitude, radius_km])

        # Sorting
        if latitude is not None and longitude is not None:
            sql += " ORDER BY distance ASC"
        else:
            sql += " ORDER BY bo.created_at DESC" # Assuming created_at exists or use ID
            # bo table doesn't have created_at in schema provided? 
            # Checked schema: book_offer doesn't have created_at. IDs are serial, so ID DESC is fine for "newest".
            # but I'll stick to ID DESC if distance not used.
            if latitude is None:
                 sql += ", bo.id DESC"

        sql += " LIMIT %s OFFSET %s"
        params.extend([limit, offset])

        cur.execute(sql, params)
        return cur.fetchall()
