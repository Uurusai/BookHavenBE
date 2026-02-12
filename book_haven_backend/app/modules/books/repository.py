from app.db import get_db_cursor
from psycopg2.extras import RealDictCursor

def create_book(isbn, title, author=None, publisher=None, category=None):
    """Create a new book in the database"""
    with get_db_cursor(commit=True) as cur:
        cur.execute("""
            INSERT INTO book (isbn, title, author, publisher, category)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id, isbn, title, author, publisher, category
        """, (isbn, title, author, publisher, category))
        return cur.fetchone()

def get_book_by_id(book_id):
    """Get book by ID"""
    with get_db_cursor() as cur:
        cur.execute("""
            SELECT id, isbn, title, author, publisher, category
            FROM book
            WHERE id = %s
        """, (book_id,))
        return cur.fetchone()

def get_book_by_isbn(isbn):
    """Get book by ISBN"""
    with get_db_cursor() as cur:
        cur.execute("""
            SELECT id, isbn, title, author, publisher, category
            FROM book
            WHERE isbn = %s
        """, (isbn,))
        return cur.fetchone()

def get_all_books(limit=100, offset=0):
    """Get all books with pagination"""
    with get_db_cursor() as cur:
        cur.execute("""
            SELECT id, isbn, title, author, publisher, category
            FROM book
            ORDER BY id
            LIMIT %s OFFSET %s
        """, (limit, offset))
        return cur.fetchall()

def search_books(query, limit=100, offset=0):
    """Search books by title, author, or category"""
    with get_db_cursor() as cur:
        search_pattern = f"%{query}%"
        cur.execute("""
            SELECT id, isbn, title, author, publisher, category
            FROM book
            WHERE title ILIKE %s OR author ILIKE %s OR category ILIKE %s
            ORDER BY id
            LIMIT %s OFFSET %s
        """, (search_pattern, search_pattern, search_pattern, limit, offset))
        return cur.fetchall()

def update_book(book_id, **kwargs):
    """Update book information"""
    allowed_fields = ['isbn', 'title', 'author', 'publisher', 'category']
    updates = {k: v for k, v in kwargs.items() if k in allowed_fields and v is not None}
    
    if not updates:
        return None
    
    set_clause = ', '.join([f"{k} = %s" for k in updates.keys()])
    values = list(updates.values()) + [book_id]
    
    with get_db_cursor(commit=True) as cur:
        cur.execute(f"""
            UPDATE book
            SET {set_clause}
            WHERE id = %s
            RETURNING id, isbn, title, author, publisher, category
        """, values)
        return cur.fetchone()

def delete_book(book_id):
    """Delete a book"""
    with get_db_cursor(commit=True) as cur:
        cur.execute("DELETE FROM book WHERE id = %s RETURNING id", (book_id,))
        return cur.fetchone() is not None

def count_books():
    """Get total count of books"""
    with get_db_cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM book")
        return cur.fetchone()[0]
