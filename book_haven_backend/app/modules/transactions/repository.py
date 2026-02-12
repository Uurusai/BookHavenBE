from app.db import get_db_cursor
from psycopg2.extras import RealDictCursor

def create_transaction(status, final_price, buyer_id, seller_id, book_offer_id):
    """Create a new transaction"""
    with get_db_cursor(commit=True) as cur:
        cur.execute("""
            INSERT INTO transaction (status, final_price, buyer_id, seller_id, 
                                   book_offer_id, created_at)
            VALUES (%s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
            RETURNING id, status, final_price, created_at, buyer_id, seller_id, book_offer_id
        """, (status, final_price, buyer_id, seller_id, book_offer_id))
        return cur.fetchone()

def get_transaction_by_id(transaction_id):
    """Get transaction by ID with related information"""
    with get_db_cursor() as cur:
        cur.execute("""
            SELECT t.id, t.status, t.final_price, t.created_at, 
                   t.buyer_id, t.seller_id, t.book_offer_id,
                   buyer.username as buyer_username,
                   seller.username as seller_username,
                   bo.offer_type, bo.price as offer_price, bo.condition,
                   b.title as book_title, b.author as book_author, b.isbn
            FROM transaction t
            LEFT JOIN app_user buyer ON t.buyer_id = buyer.id
            LEFT JOIN app_user seller ON t.seller_id = seller.id
            LEFT JOIN book_offer bo ON t.book_offer_id = bo.id
            LEFT JOIN book b ON bo.book_id = b.id
            WHERE t.id = %s
        """, (transaction_id,))
        return cur.fetchone()

def get_all_transactions(limit=100, offset=0, status=None):
    """Get all transactions with pagination and optional status filter"""
    with get_db_cursor() as cur:
        query = """
            SELECT t.id, t.status, t.final_price, t.created_at, 
                   t.buyer_id, t.seller_id, t.book_offer_id,
                   buyer.username as buyer_username,
                   seller.username as seller_username,
                   b.title as book_title
            FROM transaction t
            LEFT JOIN app_user buyer ON t.buyer_id = buyer.id
            LEFT JOIN app_user seller ON t.seller_id = seller.id
            LEFT JOIN book_offer bo ON t.book_offer_id = bo.id
            LEFT JOIN book b ON bo.book_id = b.id
            WHERE 1=1
        """
        params = []
        
        if status:
            query += " AND t.status = %s"
            params.append(status)
        
        query += " ORDER BY t.created_at DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        
        cur.execute(query, params)
        return cur.fetchall()

def get_transactions_by_buyer(buyer_id, limit=100, offset=0):
    """Get all transactions for a specific buyer"""
    with get_db_cursor() as cur:
        cur.execute("""
            SELECT t.id, t.status, t.final_price, t.created_at, 
                   t.buyer_id, t.seller_id, t.book_offer_id,
                   seller.username as seller_username,
                   b.title as book_title, b.author as book_author
            FROM transaction t
            LEFT JOIN app_user seller ON t.seller_id = seller.id
            LEFT JOIN book_offer bo ON t.book_offer_id = bo.id
            LEFT JOIN book b ON bo.book_id = b.id
            WHERE t.buyer_id = %s
            ORDER BY t.created_at DESC
            LIMIT %s OFFSET %s
        """, (buyer_id, limit, offset))
        return cur.fetchall()

def get_transactions_by_seller(seller_id, limit=100, offset=0):
    """Get all transactions for a specific seller"""
    with get_db_cursor() as cur:
        cur.execute("""
            SELECT t.id, t.status, t.final_price, t.created_at, 
                   t.buyer_id, t.seller_id, t.book_offer_id,
                   buyer.username as buyer_username,
                   b.title as book_title, b.author as book_author
            FROM transaction t
            LEFT JOIN app_user buyer ON t.buyer_id = buyer.id
            LEFT JOIN book_offer bo ON t.book_offer_id = bo.id
            LEFT JOIN book b ON bo.book_id = b.id
            WHERE t.seller_id = %s
            ORDER BY t.created_at DESC
            LIMIT %s OFFSET %s
        """, (seller_id, limit, offset))
        return cur.fetchall()

def get_transactions_by_offer(book_offer_id, limit=100, offset=0):
    """Get all transactions for a specific book offer"""
    with get_db_cursor() as cur:
        cur.execute("""
            SELECT t.id, t.status, t.final_price, t.created_at, 
                   t.buyer_id, t.seller_id, t.book_offer_id,
                   buyer.username as buyer_username,
                   seller.username as seller_username
            FROM transaction t
            LEFT JOIN app_user buyer ON t.buyer_id = buyer.id
            LEFT JOIN app_user seller ON t.seller_id = seller.id
            WHERE t.book_offer_id = %s
            ORDER BY t.created_at DESC
            LIMIT %s OFFSET %s
        """, (book_offer_id, limit, offset))
        return cur.fetchall()

def update_transaction(transaction_id, **kwargs):
    """Update transaction information"""
    allowed_fields = ['status', 'final_price']
    updates = {k: v for k, v in kwargs.items() if k in allowed_fields and v is not None}
    
    if not updates:
        return None
    
    set_clause = ', '.join([f"{k} = %s" for k in updates.keys()])
    values = list(updates.values()) + [transaction_id]
    
    with get_db_cursor(commit=True) as cur:
        cur.execute(f"""
            UPDATE transaction
            SET {set_clause}
            WHERE id = %s
            RETURNING id, status, final_price, created_at, buyer_id, seller_id, book_offer_id
        """, values)
        return cur.fetchone()

def delete_transaction(transaction_id):
    """Delete a transaction"""
    with get_db_cursor(commit=True) as cur:
        cur.execute("DELETE FROM transaction WHERE id = %s RETURNING id", (transaction_id,))
        return cur.fetchone() is not None

def count_transactions(status=None):
    """Get total count of transactions"""
    with get_db_cursor() as cur:
        query = "SELECT COUNT(*) FROM transaction WHERE 1=1"
        params = []
        
        if status:
            query += " AND status = %s"
            params.append(status)
        
        cur.execute(query, params)
        return cur.fetchone()[0]
