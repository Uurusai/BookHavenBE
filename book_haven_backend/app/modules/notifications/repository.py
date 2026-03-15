from app.db import get_db_cursor

def get_notifications(user_id, limit=50, offset=0):
    """Get notifications for a user"""
    with get_db_cursor() as cur:
        cur.execute("""
            SELECT id, entity_type, entity_id, type, message, is_read, created_at
            FROM notification
            WHERE user_id = %s
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
        """, (user_id, limit, offset))
        return cur.fetchall()

def count_unread_notifications(user_id):
    """Count unread notifications"""
    with get_db_cursor() as cur:
        cur.execute("""
            SELECT COUNT(*) FROM notification
            WHERE user_id = %s AND is_read = FALSE
        """, (user_id,))
        return cur.fetchone()[0]

def mark_notification_read(notification_id, user_id):
    """Mark a notification as read"""
    with get_db_cursor(commit=True) as cur:
        cur.execute("""
            UPDATE notification
            SET is_read = TRUE
            WHERE id = %s AND user_id = %s
            RETURNING id
        """, (notification_id, user_id))
        return cur.fetchone() is not None

def mark_all_read(user_id):
    """Mark all notifications as read for a user"""
    with get_db_cursor(commit=True) as cur:
        cur.execute("""
            UPDATE notification
            SET is_read = TRUE
            WHERE user_id = %s AND is_read = FALSE
        """, (user_id,))
