from app.db import get_db_cursor
from psycopg2.extras import RealDictCursor

def create_review(user_id, book_id, transaction_id, rating, comment):
    """Create a new review"""
    with get_db_cursor(commit=True) as cur:
        # Check for existing review
        cur.execute("""
            SELECT id FROM review 
            WHERE transaction_id = %s AND user_id = %s
        """, (transaction_id, user_id))
        if cur.fetchone():
            raise ValueError("Review already exists for this transaction")

        cur.execute("""
            INSERT INTO review (user_id, book_id, transaction_id, rating, comment, created_at)
            VALUES (%s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
            RETURNING id, user_id, book_id, transaction_id, rating, comment, created_at
        """, (user_id, book_id, transaction_id, rating, comment))
        return cur.fetchone()

def get_reviews_by_user(user_id, limit=100, offset=0):
    """Get reviews for a specific user (as the reviewee)"""
    # Note: user_id in review table is the one BEING reviewed? 
    # The schema says "user_id INT REFERENCES app_user(id)". 
    # Usually this means "Review belonging to user" (the one who wrote it) OR "Review OF user".
    # User Request: "Buyers can review sellers, sellers can review buyers".
    # Schema `review` has `user_id`, `book_id`, `transaction_id`.
    # If I want to review a seller, I should link it to the seller.
    # If `user_id` is the TARGET, then create_review needs to take target_user_id.
    # MY previous interpretation in PL/SQL trigger: user_id is the TARGET.
    # Let's stick to that. user_id = Person being reviewed.
    
    with get_db_cursor() as cur:
        cur.execute("""
            SELECT r.id, r.rating, r.comment, r.created_at, 
                   r.user_id, r.book_id, r.transaction_id,
                   t.buyer_id, t.seller_id,
                   b.title as book_title
            FROM review r
            LEFT JOIN transaction t ON r.transaction_id = t.id
            LEFT JOIN book b ON r.book_id = b.id
            WHERE r.user_id = %s
            ORDER BY r.created_at DESC
            LIMIT %s OFFSET %s
        """, (user_id, limit, offset))
        return cur.fetchall()

def get_reviews_by_book(book_id, limit=100, offset=0):
    """Get reviews for a specific book"""
    with get_db_cursor() as cur:
        cur.execute("""
            SELECT r.id, r.rating, r.comment, r.created_at, 
                   r.user_id, r.book_id, r.transaction_id,
                   u.username as reviewed_user
            FROM review r
            LEFT JOIN app_user u ON r.user_id = u.id
            WHERE r.book_id = %s
            ORDER BY r.created_at DESC
            LIMIT %s OFFSET %s
        """, (book_id, limit, offset))
        return cur.fetchall()
