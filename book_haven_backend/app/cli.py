import click
from flask.cli import with_appcontext
from app.db import create_schema, seed_data, get_conn, put_conn

@click.command('init-db')
@with_appcontext
def init_db_command():
    try:
        create_schema()
        click.echo('Database schema created successfully!')
    except Exception as e:
        click.echo(f'Error creating schema: {e}', err=True)

@click.command('seed-db')
@with_appcontext
def seed_db_command():
    try:
        seed_data()
        click.echo('Database seeded successfully!')
    except Exception as e:
        click.echo(f'Error seeding database: {e}', err=True)

@click.command('reset-db')
@with_appcontext
def reset_db_command():
    try:
        conn = get_conn()
        cur = conn.cursor()
        
        # Drop all tables
        tables = ['reading_history', 'wishlist', 'notification', 'report', 'review', 
                  'transaction', 'chat_message', 'chat_thread', 'book_offer', 'book', 
                  'meet_event', 'discussion', 'membership', 'community', 'app_user']
        
        for table in tables:
            cur.execute(f'DROP TABLE IF EXISTS {table} CASCADE;')
        
        conn.commit()
        put_conn(conn)
        
        click.echo('All tables dropped.')
        
        # Recreate schema
        create_schema()
        click.echo('Database reset successfully!')
    except Exception as e:
        click.echo(f'Error resetting database: {e}', err=True)

def init_app(app):
    app.cli.add_command(init_db_command)
    app.cli.add_command(seed_db_command)
    app.cli.add_command(reset_db_command)