import sqlite3
import hashlib
import os
import json
from datetime import datetime

# Force the database to live in the backend folder
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "medical_db.sqlite")

def get_connection():
    return sqlite3.connect(DB_FILE, timeout=10, check_same_thread=False)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Users Table
    cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                      (username TEXT PRIMARY KEY, password TEXT, role TEXT)''')
    
    # History Table - Note the 'values_json' column
    cursor.execute('''CREATE TABLE IF NOT EXISTS history 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                       username TEXT, 
                       disease TEXT, 
                       values_json TEXT, 
                       result TEXT, 
                       confidence REAL,
                       timestamp TEXT)''')

    cursor.execute("PRAGMA table_info(history)")
    history_columns = [row[1] for row in cursor.fetchall()]
    if "confidence" not in history_columns:
        cursor.execute("ALTER TABLE history ADD COLUMN confidence REAL")
    
    # Default Admin
    cursor.execute("SELECT * FROM users WHERE username='admin'")
    if not cursor.fetchone():
        hashed_pw = hashlib.sha256('1234'.encode()).hexdigest()
        cursor.execute("INSERT INTO users VALUES (?, ?, ?)", ('admin', hashed_pw, 'admin'))
    
    conn.commit()
    conn.close()

def register(username, password):
    hashed_pw = hashlib.sha256(password.encode()).hexdigest()
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users VALUES (?, ?, ?)", (username, hashed_pw, 'user'))
        conn.commit()
        return True, "Registration successful"
    except sqlite3.IntegrityError:
        return False, "Username already taken"
    finally:
        conn.close()

def verify(username, password):
    hashed_pw = hashlib.sha256(password.encode()).hexdigest()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, hashed_pw))
    user = cursor.fetchone()
    conn.close()
    return user is not None


def _extract_age(disease, values_json):
    try:
        valid_age_diseases = {"diabetes", "heart", "liver"}
        if str(disease).strip().lower() not in valid_age_diseases:
            return None
        values = json.loads(values_json) if values_json else []
        if not values:
            return None
        age_value = values[0]
        age_float = float(age_value)
        if age_float <= 0 or age_float > 120:
            return None
        return int(age_float) if age_float.is_integer() else round(age_float, 2)
    except Exception:
        return None

def log_prediction(username, disease, values, result, confidence=None):
    conn = get_connection()
    cursor = conn.cursor()
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # Convert list of values to JSON string for safe storage
    values_str = json.dumps(values)
    
    cursor.execute(
        "INSERT INTO history (username, disease, values_json, result, confidence, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
        (username, disease, values_str, result, confidence, ts),
    )
    conn.commit()
    conn.close()

def get_user_history(username):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(
        "SELECT disease, values_json, result, confidence, timestamp FROM history WHERE username=? ORDER BY id DESC",
        (username,),
    )
    rows = cursor.fetchall()
    conn.close()
    history = []
    for row in rows:
        row_dict = dict(row)
        history.append(
            {
                "age": _extract_age(row_dict.get("disease"), row_dict.get("values_json")),
                "disease": row_dict.get("disease"),
                "result": row_dict.get("result"),
                "confidence": row_dict.get("confidence"),
                "timestamp": row_dict.get("timestamp"),
            }
        )
    return history


def get_all_history():
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(
        "SELECT username, disease, result, confidence, timestamp FROM history ORDER BY id DESC"
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_system_status():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM history")
    total_predictions = cursor.fetchone()[0]
    conn.close()
    return {
        "database": "connected",
        "total_users": total_users,
        "total_predictions": total_predictions,
    }


def get_user_role(username):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT role FROM users WHERE username=?", (username,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None
