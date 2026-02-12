from app.db.connection import get_conn, put_conn
from werkzeug.security import generate_password_hash

def seed_data():
    """Seed the database with test/demo data"""
    conn = get_conn()
    try:
        cur = conn.cursor()
        
        # Check if data already exists
        cur.execute("SELECT COUNT(*) FROM app_user")
        user_count = cur.fetchone()[0]
        
        if user_count > 0:
            print("Database already contains data. Skipping seed.")
            return
        
        # Seed users
        users_data = [
            ('john_doe', 'john@example.com', generate_password_hash('password123'), 'user', 'John Doe', 'New York', 'USA'),
            ('jane_smith', 'jane@example.com', generate_password_hash('password123'), 'user', 'Jane Smith', 'London', 'UK'),
            ('admin_user', 'admin@bookhaven.com', generate_password_hash('admin123'), 'admin', 'Admin User', 'San Francisco', 'USA'),
            ('alice_wonder', 'alice@example.com', generate_password_hash('password123'), 'user', 'Alice Wonder', 'Paris', 'France'),
            ('bob_builder', 'bob@example.com', generate_password_hash('password123'), 'user', 'Bob Builder', 'Toronto', 'Canada'),
        ]
        
        for user in users_data:
            cur.execute("""
                INSERT INTO app_user (username, email, password_hash, role, full_name, city, country)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, user)
        
        print(f"Inserted {len(users_data)} users")
        
        # Seed books
        books_data = [
            ('978-0-7475-3269-9', 'Harry Potter and the Philosopher\'s Stone', 'J.K. Rowling', 'Bloomsbury', 'Fantasy'),
            ('978-0-06-112008-4', 'To Kill a Mockingbird', 'Harper Lee', 'J.B. Lippincott & Co.', 'Fiction'),
            ('978-0-452-28423-4', '1984', 'George Orwell', 'Secker & Warburg', 'Dystopian'),
            ('978-0-7432-7356-5', 'The Great Gatsby', 'F. Scott Fitzgerald', 'Scribner', 'Fiction'),
            ('978-0-14-028329-3', 'Pride and Prejudice', 'Jane Austen', 'T. Egerton', 'Romance'),
        ]
        
        for book in books_data:
            cur.execute("""
                INSERT INTO book (isbn, title, author, publisher, category)
                VALUES (%s, %s, %s, %s, %s)
            """, book)
        
        print(f"Inserted {len(books_data)} books")
        
        conn.commit()
        print("Database seeded successfully!")
        
    except Exception as e:
        conn.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        put_conn(conn)