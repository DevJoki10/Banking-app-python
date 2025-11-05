import sqlite3


DB_FILE = "bank.db"


def create_connection():
    conn = sqlite3.connect(DB_FILE)
    return conn

def create_tables():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
CREATE TABLE IF NOT EXISTS users ( 
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL CHECK (first_name <> ''), 
    last_name TEXT NOT NULL CHECK (last_name <> ''),
    email TEXT NOT NULL UNIQUE CHECK (email <> ''),
    username TEXT NOT NULL UNIQUE CHECK (username <> ''),
    password_hash TEXT NOT NULL CHECK (password_hash <> ''), 
    pin TEXT,             
    account_number TEXT UNIQUE,
    balance REAL DEFAULT 0.0,   
    created_at TEXT DEFAULT CURRENT_TIMESTAMP                                    
) 
""")

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        type TEXT NOT NULL,
        amount REAL NOT NULL,
        details TEXT,
        timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
        );               
        """)        

        conn.commit()
        print("✅ Tables checked/created successfully.")

def generate_account_number():
    import random
    return ''.join([str(random.randint(0, 9)) for _ in range(10)])

def insert_user(first_name, last_name, email, username, password_hash, pin=None):
    with create_connection() as conn:
        cursor = conn.cursor()
        # Generate a unique account number
        while True:
            account_number = generate_account_number()
            cursor.execute("SELECT id FROM users WHERE account_number = ?", (account_number,))
            if not cursor.fetchone():
                break
                
        cursor.execute("""
            INSERT INTO users (first_name, last_name, email, username, password_hash, pin, account_number)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (first_name, last_name, email, username, password_hash, pin, account_number))
        conn.commit()
        return cursor.lastrowid

def get_user_by_username(username):
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        return cursor.fetchone()

def get_user_by_email(email):
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        return cursor.fetchone()

def get_user_by_id(user_id):
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        return cursor.fetchone()

def update_balance(user_id, new_balance):
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET balance = ? WHERE id = ?", (new_balance, user_id))
        conn.commit()

def record_transaction(user_id, type, amount, details=None):
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO transactions (user_id, type, amount, details)
            VALUES (?, ?, ?, ?)
        """, (user_id, type, amount, details))
        conn.commit()
        return cursor.lastrowid

def get_user_by_account(account_number):
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE account_number = ?", (account_number,))
        return cursor.fetchone()

def get_user_balance(user_id):
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT balance FROM users WHERE id = ?", (user_id,))
        result = cursor.fetchone()
        return result[0] if result else 0.0

def get_transactions(user_id, limit=5):
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT type, amount, timestamp, details
            FROM transactions 
            WHERE user_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (user_id, limit))
        return cursor.fetchall()