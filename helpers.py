# helpers.py
import hashlib
import random
import re

# ===============================
# PASSWORD & PIN HASHING
# ===============================
def hash_password(password: str) -> str:
    """Hashes a password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()

def hash_pin(pin: str) -> str:
    """Hashes a 4-digit transaction PIN using SHA-256."""
    return hashlib.sha256(pin.encode()).hexdigest()

# ===============================
# EMAIL VALIDATION
# ===============================
def validate_email(email: str) -> bool:
    """Validates an email address format."""
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(pattern, email) is not None

# ===============================
# ACCOUNT NUMBER GENERATION
# ===============================
def generate_account_number(existing_numbers=None) -> str:
    """Generates a unique 10-digit account number."""
    while True:
        acc_num = str(random.randint(1000000000, 9999999999))
        if acc_num not in existing_accounts:
            return acc_num