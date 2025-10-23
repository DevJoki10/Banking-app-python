import sqlite3

DB_FILE = "joki_bank.db"


def create_tables():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
CREATE TABLE IF NOT EXISTS users ( 
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL CHECK (first_name <> '') 
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