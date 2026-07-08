import psycopg
from psycopg.errors import DuplicateDatabase

try:
    # Connect to default postgres db
    conn = psycopg.connect("postgresql://postgres:postgres@localhost:5432/postgres", autocommit=True)
    conn.execute("CREATE DATABASE ai_documents_db")
    print("Database created successfully")
except DuplicateDatabase:
    print("Database already exists")
except Exception as e:
    print(f"Error: {e}")
finally:
    if 'conn' in locals():
        conn.close()
