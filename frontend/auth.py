import sqlite3
import hashlib
import os

# FIX 1: Use Absolute Path (Crucial for Windows)
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # Gets folder of auth.py
# Go up one level (..), then into backend, then find the file
DB_PATH = os.path.join(os.path.dirname(BASE_DIR), "backend", "medical_db.sqlite")

def get_connection():
    # FIX 2: Add timeout to prevent "Database Locked" errors
    return sqlite3.connect(DB_PATH, timeout=10, check_same_thread=False)

def verify(username, password):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        hashed_pw = hashlib.sha256(password.encode()).hexdigest()
        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, hashed_pw))
        user = cursor.fetchone()
        conn.close()
        return user is not None
    except Exception as e:
        print(f"Auth Error: {e}")
        return False


def verify_user(username, password):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        hashed_pw = hashlib.sha256(password.encode()).hexdigest()
        cursor.execute(
            "SELECT username, role FROM users WHERE username=? AND password=?",
            (username, hashed_pw),
        )
        user = cursor.fetchone()
        conn.close()
        if not user:
            return None
        return {"username": user[0], "role": user[1]}
    except Exception as e:
        print(f"Auth Error: {e}")
        return None

def register(username, password):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        hashed_pw = hashlib.sha256(password.encode()).hexdigest()
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", 
                       (username, hashed_pw, 'user'))
        conn.commit()
        conn.close()
        return True, "Success"
    except sqlite3.IntegrityError:
        return False, "Username already exists"
    except Exception as e:
        return False, str(e)
