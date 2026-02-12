from app.db.connection import get_conn, put_conn
import os

def create_schema():
    conn = get_conn()
    try:
        cur = conn.cursor()
        schema_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "migrations", "schema.sql")
        with open(schema_path) as f:
            cur.execute(f.read())
        conn.commit()
    finally:
        put_conn(conn)
