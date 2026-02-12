from app.db import get_db_cursor
from psycopg2.extras import RealDictCursor

# Chat Thread operations
def create_chat_thread():
    """Create a new chat thread"""
    with get_db_cursor(commit=True) as cur:
        cur.execute("""
            INSERT INTO chat_thread (created_at)
            VALUES (CURRENT_TIMESTAMP)
            RETURNING id, created_at
        """)
        return cur.fetchone()

def get_chat_thread_by_id(thread_id):
    """Get chat thread by ID"""
    with get_db_cursor() as cur:
        cur.execute("""
            SELECT id, created_at
            FROM chat_thread
            WHERE id = %s
        """, (thread_id,))
        return cur.fetchone()

def get_all_chat_threads(limit=100, offset=0):
    """Get all chat threads with pagination"""
    with get_db_cursor() as cur:
        cur.execute("""
            SELECT id, created_at
            FROM chat_thread
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
        """, (limit, offset))
        return cur.fetchall()

def delete_chat_thread(thread_id):
    """Delete a chat thread and all its messages"""
    with get_db_cursor(commit=True) as cur:
        cur.execute("DELETE FROM chat_thread WHERE id = %s RETURNING id", (thread_id,))
        return cur.fetchone() is not None

def count_chat_threads():
    """Get total count of chat threads"""
    with get_db_cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM chat_thread")
        return cur.fetchone()[0]

# Chat Message operations
def create_chat_message(message, sender_id, thread_id):
    """Create a new chat message"""
    with get_db_cursor(commit=True) as cur:
        cur.execute("""
            INSERT INTO chat_message (message, sender_id, thread_id, sent_at)
            VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
            RETURNING id, message, sent_at, sender_id, thread_id
        """, (message, sender_id, thread_id))
        return cur.fetchone()

def get_chat_message_by_id(message_id):
    """Get chat message by ID"""
    with get_db_cursor() as cur:
        cur.execute("""
            SELECT id, message, sent_at, sender_id, thread_id
            FROM chat_message
            WHERE id = %s
        """, (message_id,))
        return cur.fetchone()

def get_messages_by_thread(thread_id, limit=100, offset=0):
    """Get all messages in a thread"""
    with get_db_cursor() as cur:
        cur.execute("""
            SELECT cm.id, cm.message, cm.sent_at, cm.sender_id, cm.thread_id,
                   u.username as sender_username
            FROM chat_message cm
            LEFT JOIN app_user u ON cm.sender_id = u.id
            WHERE cm.thread_id = %s
            ORDER BY cm.sent_at ASC
            LIMIT %s OFFSET %s
        """, (thread_id, limit, offset))
        return cur.fetchall()

def update_chat_message(message_id, message):
    """Update a chat message"""
    with get_db_cursor(commit=True) as cur:
        cur.execute("""
            UPDATE chat_message
            SET message = %s
            WHERE id = %s
            RETURNING id, message, sent_at, sender_id, thread_id
        """, (message, message_id))
        return cur.fetchone()

def delete_chat_message(message_id):
    """Delete a chat message"""
    with get_db_cursor(commit=True) as cur:
        cur.execute("DELETE FROM chat_message WHERE id = %s RETURNING id", (message_id,))
        return cur.fetchone() is not None

def count_messages_in_thread(thread_id):
    """Get total count of messages in a thread"""
    with get_db_cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM chat_message WHERE thread_id = %s", (thread_id,))
        return cur.fetchone()[0]
