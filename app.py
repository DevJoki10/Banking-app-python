from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import sqlite3
from database import (
    create_connection, create_tables, get_user_by_username, insert_user,
    get_user_by_account, get_transactions
)
from helpers import hash_password

app = Flask(__name__)
app.secret_key = "super_secret_key"

# Ensure tables exist
create_tables()

@app.route('/')
def splash():
    return render_template('splash.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        fname = request.form['fname'].strip()
        lname = request.form['lname'].strip()
        email = request.form['email'].strip()
        username = request.form['username'].strip()
        password = request.form['password']
        pin = request.form['pin']

        if len(password) < 6:
            flash("Password must be at least 6 characters long", "danger")
            return redirect(url_for('signup'))

        if len(pin) != 4 or not pin.isdigit():
            flash("PIN must be exactly 4 digits", "danger")
            return redirect(url_for('signup'))

        if get_user_by_username(username):
            flash("Username already exists", "danger")
            return redirect(url_for('signup'))

        try:
            hashed_pw = hash_password(password)
            hashed_pin = hash_password(pin)
            insert_user(fname, lname, email, username, hashed_pw, hashed_pin)
            flash("Account created successfully! Please log in.", "success")
            return redirect(url_for('login'))
        except Exception as e:
            flash(f"Error creating account: {e}", "danger")

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username').strip()
        password = request.form.get('password')

        if not username or not password:
            flash("Both fields are required", "danger")
            return redirect(url_for('login'))

        user = get_user_by_username(username)
        if not user:
            flash("User not found", "danger")
            return redirect(url_for('login'))

        if user[5] == hash_password(password):  # ✅ index 5 = password_hash
            session['user_id'] = user[0]
            session['username'] = user[4]
            flash("Login successful!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid password", "danger")
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash("Please log in first.", "warning")
        return redirect(url_for('login'))

    conn = create_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],))
    user = cursor.fetchone()
    
    if not user:
        session.clear()
        flash("User not found.", "error")
        return redirect(url_for('login'))
        
    transactions = get_transactions(session['user_id'])
    conn.close()

    return render_template('dashboard.html', user=user, transactions=transactions)

@app.route('/transaction', methods=['POST'])
def transaction():
    if 'user_id' not in session:
        return jsonify({'error': 'Please log in first'}), 401
        
    try:
        data = request.get_json()
        transaction_type = data.get('type')
        amount = float(data.get('amount', 0))
        recipient_account = data.get('recipient_account')
        
        if amount <= 0:
            return jsonify({'error': 'Invalid amount'}), 400
            
        conn = create_connection()
        cursor = conn.cursor()
        
        # Get current user's balance
        cursor.execute("SELECT balance, account_number FROM users WHERE id = ?", (session['user_id'],))
        user_data = cursor.fetchone()
        if not user_data:
            conn.close()
            return jsonify({'error': 'User not found'}), 404
            
        current_balance, account_number = user_data
        
        if transaction_type == 'deposit':
            new_balance = current_balance + amount
            cursor.execute("UPDATE users SET balance = ? WHERE id = ?", 
                         (new_balance, session['user_id']))
            cursor.execute("""INSERT INTO transactions (user_id, type, amount) 
                            VALUES (?, 'deposit', ?)""", 
                         (session['user_id'], amount))
                         
        elif transaction_type == 'withdraw':
            if amount > current_balance:
                conn.close()
                return jsonify({'error': 'Insufficient funds'}), 400
                
            new_balance = current_balance - amount
            cursor.execute("UPDATE users SET balance = ? WHERE id = ?", 
                         (new_balance, session['user_id']))
            cursor.execute("""INSERT INTO transactions (user_id, type, amount) 
                            VALUES (?, 'withdraw', ?)""", 
                         (session['user_id'], amount))
                         
        elif transaction_type == 'transfer':
            if amount > current_balance:
                conn.close()
                return jsonify({'error': 'Insufficient funds'}), 400
                
            if not recipient_account:
                conn.close()
                return jsonify({'error': 'Recipient account required'}), 400
                
            # Find recipient
            cursor.execute("SELECT id, balance FROM users WHERE account_number = ?", 
                         (recipient_account,))
            recipient = cursor.fetchone()
            if not recipient:
                conn.close()
                return jsonify({'error': 'Invalid recipient account'}), 400
                
            recipient_id, recipient_balance = recipient
            
            # Update both balances
            new_balance = current_balance - amount
            new_recipient_balance = recipient_balance + amount
            
            cursor.execute("UPDATE users SET balance = ? WHERE id = ?", 
                         (new_balance, session['user_id']))
            cursor.execute("UPDATE users SET balance = ? WHERE id = ?", 
                         (new_recipient_balance, recipient_id))
                         
            # Record transactions for both parties
            cursor.execute("""INSERT INTO transactions (user_id, type, amount, details) 
                            VALUES (?, 'transfer_out', ?, ?)""", 
                         (session['user_id'], amount, f'To: {recipient_account}'))
            cursor.execute("""INSERT INTO transactions (user_id, type, amount, details) 
                            VALUES (?, 'transfer_in', ?, ?)""", 
                         (recipient_id, amount, f'From: {account_number}'))
        
        conn.commit()
        
        # Get updated transactions
        cursor.execute("""
            SELECT type, amount, timestamp FROM transactions
            WHERE user_id = ? ORDER BY timestamp DESC LIMIT 5
        """, (session['user_id'],))
        transactions = [
            {'type': t[0], 'amount': t[1], 'timestamp': t[2]} 
            for t in cursor.fetchall()
        ]
        
        conn.close()
        
        return jsonify({
            'success': True,
            'message': f'{transaction_type.title()} successful',
            'new_balance': new_balance,
            'transactions': transactions
        })
        
    except Exception as e:
        print(f"Transaction error: {str(e)}")
        return jsonify({'error': 'Transaction failed'}), 500

@app.route('/logout')
def logout():
    session.clear()
    flash("You've been logged out.", "info")
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
