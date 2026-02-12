from app.db.connection import get_conn, put_conn

def db_healthcheck():
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute("SELECT 1;")
        return cur.fetchone()[0] == 1
    finally:
        put_conn(conn)
