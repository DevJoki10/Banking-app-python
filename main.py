import re
import sqlite3
import time
from time import sleep
from colorama import Fore, Style, init
init(autoreset=True)
import os
os.system('cls' if os.name == 'nt' else 'clear')
from database import create_tables
from getpass import getpass
from helpers import hash_password, hash_pin, validate_email, generate_account_number


DB_FILE = "joki_bank.db"
create_tables()

def check_tables():
    with sqlite3.connect(DB_FILE) as conn:

        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        print(cursor.fetchall())

# check_tables()

def register_user():
    print( Fore.CYAN + "************************USER REGISTRATION**************************" + Style.RESET_ALL)
    while True:
        last_name = input("Input your last name: ").strip()
        if not last_name:
            print(Fore.LIGHTCYAN_EX + "Last name field cannot be blank"+ Style.RESET_ALL)
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
        if not validate_email(email):
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
    hashed_password = hash_password(password1)
   
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
    hashed_pin = hash_pin(pin)
    

    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT account_number FROM users")
        existing_accounts  = [row[0] for row in cursor.fetchall()]
    account_number = generate_account_number( existing_accounts )

        # Ask user for initial deposit (must be ≥ 2000)
    while True:
        try:
            initial_deposit = float(input("Enter your initial deposit (₦2000 minimum): "))
            if initial_deposit < 2000:
                print("Minimum opening balance is ₦2000.")
                continue
            break
        except ValueError:
            print("Please enter a valid numeric amount.")

    
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO users (first_name, last_name, email, username, password, pin, account_number, balance)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (first_name, last_name, email, username, hashed_password, hashed_pin, account_number, initial_deposit))
        conn.commit()

         
        user_id = cursor.lastrowid

        #  Record the first transaction
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            INSERT INTO transactions (user_id, type, amount, timestamp)
            VALUES (?, ?, ?, ?)
        """, (user_id, "deposit", initial_deposit, timestamp))
        conn.commit()


       

    

    print(Fore.GREEN + "Registration successful!" + Style.RESET_ALL)
    print(f"Your new account number is: {account_number}")
    print("Please keep your password and PIN safe.\n")

def log_in():
    print("************************LOG IN**************************")  
    max_attempts = 3
    failed_attempts = 0  
    while True:
        username_or_email = input("Enter your username/ Email address").strip()
        if not username_or_email:
            print("Username/ Email address field cannot be empty")
            continue
        break 

    while True:
        password = getpass("Enter your password: ").strip()
        if not password :
            print("Password field cannot be blank")  
            continue
        break
    hashed_password =  hash_password(password)
    query = ("SELECT * FROM users WHERE email = ? and password = ?"
             if validate_email(username_or_email)
             else "SELECT * FROM users WHERE username = ? and password = ?")

    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()        
        cursor.execute(query, (username_or_email, hashed_password))
        user = cursor.fetchone()

    if user:
        print(f"Login successful. Hi {user[1]} {user[2]} ") 
        current_user = BankUser(user[0], user[1], user[2], user[8])
        return current_user
    else:
        failed_attempts += 1
        remaining = max_attempts - failed_attempts
        print(f"\nInvalid Username/Email or Password. Attempts left: {remaining}")

        if failed_attempts >= max_attempts:
            print("Too many failed attempts. Please wait 30 seconds before trying again.\n")
            time.sleep(30)
            failed_attempts = 0  

    retry = input("Do you want to try again? (y/n): ").strip().lower()
    if retry != 'y':
        print("Returning to main menu...\n")
        return None
        

class BankUser:         
    def __init__(self,user_id,first_name,last_name,balance):
        self.user_id = user_id  
        self.first_name = first_name
        self.last_name = last_name
        self.balance = balance  

    def update_balance_in_db(self):
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET balance = ? WHERE id = ?", (self.balance, self.user_id))
            conn.commit()

    def record_transaction(self, amount, t_type="deposit"):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO transactions (user_id, type, amount, timestamp)
                VALUES (?, ?, ?, ?)
            """, (self.user_id, t_type, amount, timestamp))
            conn.commit()    


    def deposit(self):
                try:
                    amount = float(input("Input amount you wanna deposit: "))
                    if amount <= 0:
                        print("Amount must not be less than zero")
                        return
                    self.balance += amount
                    self.update_balance_in_db()
                    self.record_transaction(amount)
                    print(f"Deposit successful! New balance: ₦{self.balance:.2f}")  
                except ValueError:
                    print("Invalid amount . Please make sure amout entered is a valid number")    
    def withdraw(self):
        try:
            amount = float(input("Input amount you wanna withdraw: "))
            if amount <= 0:
                print("Amount must not be less than zero")
                return
            if amount > self.balance:
                print("Insufficient Funds")
                return

            self.balance -= amount
            self.update_balance_in_db()
            with sqlite3.connect(DB_FILE) as conn :
                cursor = conn.cursor()
                cursor.execute("""INSERT INTO transactions(user_id,type,amount, timestamp)
                            VALUES(?,?,?,?)""" ,(self.user_id,"withdrawal", amount))
                conn.commit()
                print(f"Withdrawal successful! New balance: ₦{self.balance:.2f}")
        except ValueError: print("Invalid amount . Please make sure amout entered is a valid number")

    def transfer(self):
        try:
            receiver_acct = input("Enter recipient account number: ").strip()
            if not receiver_acct:
                print("Account number field cannot be blank.")
                return

            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, first_name, last_name FROM users WHERE account_number = ?", (receiver_acct,))
                receiver = cursor.fetchone()

            if not receiver:
                print("Recipient account not found.")
                return

            amount = float(input("Enter amount to transfer: "))
            if amount <= 0:
                print("Transfer amount must be greater than zero.")
                return
            if amount > self.balance:
                print("Insufficient funds for this transfer.")
                return

            confirm = input(f"Confirm transfer of ₦{amount:,.2f} to {receiver[1]} {receiver[2]}? (y/n): ").strip().lower()
            if confirm != 'y':
                print("Transfer cancelled.")
                return

            
            self.balance -= amount
            self.update_balance_in_db()
            self.record_transaction(amount, "transfer_out")

            
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE users SET balance = balance + ? WHERE id = ?", (amount, receiver[0]))
                cursor.execute("""
                    INSERT INTO transactions (user_id, type, amount, timestamp)
                    VALUES (?, ?, ?, ?)
                """, (receiver[0], "transfer_in", amount, time.strftime("%Y-%m-%d %H:%M:%S")))
                conn.commit()

            print(f"Transfer successful! ₦{amount:,.2f} sent to {receiver[1]} {receiver[2]}.")
            print(f"New Balance: ₦{self.balance:,.2f}")

        except ValueError:
            print("Invalid amount. Please enter a valid number.")                
        



    def check_balance(self):
        print(f"Your current balance is: ₦{self.balance:.2f}")


    def view_account_details(self):
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT account_number, email, username FROM users WHERE id = ?", (self.user_id,))
            details = cursor.fetchone()

        print("\n================== ACCOUNT DETAILS ==================")
        print(f"Name: {self.first_name} {self.last_name}")
        print(f"Username: {details[2]}")
        print(f"Email: {details[1]}")
        print(f"Account Number: {details[0]}")
        print(f"Current Balance: ₦{self.balance:,.2f}")
        print("=====================================================\n")



    
    def view_transaction_history(self):
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT type, amount, timestamp FROM transactions
                WHERE user_id = ?
                ORDER BY timestamp DESC
            """, (self.user_id,))
            transactions = cursor.fetchall()
            
        print("=======================================================================")
        print(f"      TRANSACTION HISTORY for {self.first_name} {self.last_name}")    
        print("=======================================================================")

        if not transactions:
            print("You have not made any transaction. Your transaction history is empty")
            print("=======================================================================")
            return
        print(f"{'DATE':<22} {'TYPE':<12} {'AMOUNT (₦)':>12}")
        print("=======================================================================")
        for t_type, amount, date in transactions:
            print(f"{date:<22} {t_type.title():<12} ₦{amount:>10,.2f}")

        print("=======================================================================")
        print(f"Current balance. : ₦{self.balance:,.2f}")
        print("=======================================================================")
    
def main_menu ():
    current_user = None
    while True:
        print ("""
 ==============================
    JOKI TERMINAL BANK
 ==============================                 
1. Register
2. Log In
3. Deposit
4. Withdrawal
5. Balance Inquiry
6. Transaction History
7. Transfer
8.Account details            
9. Exit                                                                             
""") 
        choice = input("Select an option (1-9): ").strip()

        if choice == "1":
            register_user()
        elif choice == "2":
           current_user = log_in()
        elif choice == "3":
            if current_user:
                current_user.deposit()
            else:
                print("You must log in first.")
        elif choice == "4":
            if current_user: 
                current_user.withdraw()
            else:
                print("You must log in first.")
        elif choice == "5":
            if current_user: 
                current_user.check_balance()
            else:
                print("You must log in first.")                
        elif choice == "6":
            if current_user:
                current_user.view_transaction_history()
            else:
                print("You must log in first.")
        elif choice == "7":
            if current_user:
                current_user.transfer()
            else:
                print("You must log in first.")
        elif choice == "8":
            if current_user:
                current_user.view_account_details()
            else:
             print("You must log in first.")        
        elif choice == "9":
            print(Fore.CYAN + "Thank you for using JOKI Terminal Bank. Goodbye!" + Style.RESET_ALL)
            break
        else:
            print("Invalid choice, please select 1-9")           



if __name__ == "__main__":
    main_menu()            