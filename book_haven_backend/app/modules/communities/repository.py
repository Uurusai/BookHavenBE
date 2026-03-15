from app.db import get_db_cursor
from psycopg2.extras import RealDictCursor

# Community operations
def create_community(name, description=None):
    """Create a new community"""
    with get_db_cursor(commit=True) as cur:
        cur.execute("""
            INSERT INTO community (name, description, created_at, member_count)
            VALUES (%s, %s, CURRENT_TIMESTAMP, 0)
            RETURNING id, name, description, created_at, member_count
        """, (name, description))
        return cur.fetchone()

def get_community_by_id(community_id):
    """Get community by ID"""
    with get_db_cursor() as cur:
        cur.execute("""
            SELECT id, name, description, created_at, member_count
            FROM community
            WHERE id = %s
        """, (community_id,))
        return cur.fetchone()

def get_all_communities(limit=100, offset=0):
    """Get all communities with pagination"""
    with get_db_cursor() as cur:
        cur.execute("""
            SELECT id, name, description, created_at, member_count
            FROM community
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
        """, (limit, offset))
        return cur.fetchall()

def search_communities(query, limit=100, offset=0):
    """Search communities by name or description"""
    with get_db_cursor() as cur:
        search_pattern = f"%{query}%"
        cur.execute("""
            SELECT id, name, description, created_at, member_count
            FROM community
            WHERE name ILIKE %s OR description ILIKE %s
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
        """, (search_pattern, search_pattern, limit, offset))
        return cur.fetchall()

def update_community(community_id, **kwargs):
    """Update community information"""
    allowed_fields = ['name', 'description', 'member_count']
    updates = {k: v for k, v in kwargs.items() if k in allowed_fields and v is not None}
    
    if not updates:
        return None
    
    set_clause = ', '.join([f"{k} = %s" for k in updates.keys()])
    values = list(updates.values()) + [community_id]
    
    with get_db_cursor(commit=True) as cur:
        cur.execute(f"""
            UPDATE community
            SET {set_clause}
            WHERE id = %s
            RETURNING id, name, description, created_at, member_count
        """, values)
        return cur.fetchone()

def delete_community(community_id):
    """Delete a community"""
    with get_db_cursor(commit=True) as cur:
        cur.execute("DELETE FROM community WHERE id = %s RETURNING id", (community_id,))
        return cur.fetchone() is not None

def count_communities():
    """Get total count of communities"""
    with get_db_cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM community")
        return cur.fetchone()[0]

# Membership operations
def add_member(user_id, community_id, role='member'):
    """Add a user to a community"""
    with get_db_cursor(commit=True) as cur:
        # Check if membership already exists
        cur.execute("""
            SELECT user_id FROM membership
            WHERE user_id = %s AND community_id = %s
        """, (user_id, community_id))
        
        if cur.fetchone():
            return None  # Already a member
        
        # Add membership
        cur.execute("""
            INSERT INTO membership (user_id, community_id, role, joined_at)
            VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
            RETURNING user_id, community_id, role, joined_at
        """, (user_id, community_id, role))
        
        membership = cur.fetchone()
        
        # Update member count
        cur.execute("""
            UPDATE community
            SET member_count = member_count + 1
            WHERE id = %s
        """, (community_id,))
        
        return membership

def remove_member(user_id, community_id):
    """Remove a user from a community"""
    with get_db_cursor(commit=True) as cur:
        cur.execute("""
            DELETE FROM membership
            WHERE user_id = %s AND community_id = %s
            RETURNING user_id
        """, (user_id, community_id))
        
        result = cur.fetchone()
        
        if result:
            # Update member count
            cur.execute("""
                UPDATE community
                SET member_count = GREATEST(member_count - 1, 0)
                WHERE id = %s
            """, (community_id,))
        
        return result is not None

def get_community_members(community_id, limit=100, offset=0):
    """Get all members of a community"""
    with get_db_cursor() as cur:
        cur.execute("""
            SELECT m.user_id, m.community_id, m.role, m.joined_at,
                   u.username, u.email, u.full_name
            FROM membership m
            JOIN app_user u ON m.user_id = u.id
            WHERE m.community_id = %s
            ORDER BY m.joined_at DESC
            LIMIT %s OFFSET %s
        """, (community_id, limit, offset))
        return cur.fetchall()

def get_user_communities(user_id, limit=100, offset=0):
    """Get all communities a user is member of"""
    with get_db_cursor() as cur:
        cur.execute("""
            SELECT c.id, c.name, c.description, c.created_at, c.member_count,
                   m.role, m.joined_at
            FROM membership m
            JOIN community c ON m.community_id = c.id
            WHERE m.user_id = %s
            ORDER BY m.joined_at DESC
            LIMIT %s OFFSET %s
        """, (user_id, limit, offset))
        return cur.fetchall()

def update_member_role(user_id, community_id, role):
    """Update a member's role in a community"""
    with get_db_cursor(commit=True) as cur:
        cur.execute("""
            UPDATE membership
            SET role = %s
            WHERE user_id = %s AND community_id = %s
            RETURNING user_id, community_id, role, joined_at
        """, (role, user_id, community_id))
        return cur.fetchone()
