import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

POSTGRES_HOST = os.getenv('POSTGRES_HOST')        # e.g., "localhost" or "remote.server.com"
POSTGRES_DB = os.getenv('POSTGRES_DB') 
POSTGRES_USER = os.getenv('POSTGRES_USER') 
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD') 
POSTGRES_PORT = os.getenv('POSTGRES_PORT')

def register_user(conn, username, password):
    """
    Simple function to register a new user (username, password).
    Returns the username on success or None on failure.
    """
    # Check if user already exists
    check_query = "SELECT id FROM users WHERE username = %s"
    insert_query = "INSERT INTO users (username, password, high_score) VALUES (%s, %s, 0) RETURNING id"

    with conn.cursor() as cur:
        cur.execute(check_query, (username,))
        if cur.fetchone():
            print("Username already exists!")
            return None
        
        try:
            cur.execute(insert_query, (username, password))
            new_id = cur.fetchone()[0]
            conn.commit()
            print(f"User registered successfully with id={new_id}")
            return username
        except Exception as e:
            conn.rollback()
            print("Error registering user:", e)
            return None

def authenticate_user(conn, username, password):
    """
    Simple function to authenticate an existing user (username, password).
    Returns the username if authentication is successful, or None otherwise.
    """
    query = "SELECT id FROM users WHERE username = %s AND password = %s"
    with conn.cursor() as cur:
        cur.execute(query, (username, password))
        row = cur.fetchone()
        if row:
            print("Login successful!")
            return username
        else:
            print("Invalid username or password.")
            return None
        
        
def create_connection():
    """
    Create a connection to the PostgreSQL database.
    Returns a psycopg2 connection or None if failed.
    """
    try:
        conn = psycopg2.connect(
            host=POSTGRES_HOST,
            dbname=POSTGRES_DB,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            port=POSTGRES_PORT
        )
        return conn
    except Exception as e:
        print("Failed to connect to database:", e)
        return None