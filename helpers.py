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
    if existing_numbers is None:
        existing_numbers = set()
    while True:
        acc_num = str(random.randint(1000000000, 9999999999))
        if acc_num not in existing_numbers:
            return acc_num

def verify_password(stored_hash: str, provided_password: str) -> bool:
    """Verifies a password against its hash."""
    return stored_hash == hash_password(provided_password)