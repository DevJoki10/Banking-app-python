import re
import sqlite3
import hashlib




from database import create_tables
from getpass import getpass

DB_FILE = "joki_bank.db"
create_tables()

def check_tables():
    with sqlite3.connect(DB_FILE) as conn:

        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        print(cursor.fetchall())

check_tables()

def register_user():
    print("************************USER REGISTRATION**************************")
    while True:
        last_name = input("Input your last name: ").strip()
        if not last_name:
            print("Last name field cannot be blank")
            continue
        break 

    while True:
        first_name = input("Input  your first name: ").strip()
        if not first_name:
            print("First name field cannot be blank")
            continue
        break

    while True:
        username = input("Enter your username: ").strip()
        if not username:
            print("Username field cannot be blank")
            continue
        
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            existing_user = cursor.fetchone()  

        if existing_user:
            print("Username already taken. Please choose another one.")
            continue
        break  
    
    while True:
        email = input("Enter your email address: ").strip()
        if not email:
            print("Email field cannot be blank")
            continue
        email_pattern =  r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
        if not re.match(email_pattern,email):
            print("Invalid Email Address") 
            continue
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users where email = ?", (email,))
            existing_user = cursor.fetchone()
        if existing_user:
            print("Email already exists. Please choose another one.")    
            continue
        break

    while True:
        password1 = getpass("Enter your password: ").strip()
        if not password1:
            print("Password field cannot be blank")
            continue
        password2 = getpass("Confirm your password: ").strip()
        if not password2:
            print("Confirm Password field cannot be blank")
            continue
        if password1 != password2:
            print("Passwords do not match")
            continue
        break
    hashed_password = hashlib.sha256(password1.encode()).hexdigest()

   
    while True:
        pin = getpass("Set a 4-digit transaction PIN: ").strip()
        if not re.fullmatch(r"\d{4}", pin):
            print("PIN must be exactly 4 digits.")
            continue
        confirm_pin = getpass("Confirm your PIN: ").strip()
        if pin != confirm_pin:
            print("PINs do not match.")
            continue
        break
    hashed_pin = hashlib.sha256(pin.encode()).hexdigest()
    

    
    while True:
        account_number = str(random.randint(1000000000, 9999999999))
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE account_number = ?", (account_number,))
            if not cursor.fetchone():  
                break

    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO users (first_name, last_name, email, username, password, pin, account_number, balance)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (first_name, last_name, email, username, hashed_password, hashed_pin, account_number, 0))
        conn.commit()

    print(f"\nRegistration successful! ")
    print(f"Your new account number is: {account_number}")
    print("Please keep your password and PIN safe.\n")
