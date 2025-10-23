# Banking-app-python
🏗️ Stage 1 — Project Setup Initialized the JOKI Terminal Bank project with main folders and base files: main.py, database.py, helpers.py,  transactions.py. Set up SQLite database joki_bank.db, added .gitignore for cache/db files, and ran git init to begin version control.

🔐 Stage 2 — User Registration & Authentication
Added secure user registration and login system. Integrated SHA-256 password hashing, input validation, and login retry limit with 30-sec lockout.

Stage 3: Account model & DB updates

- Introduced `BankUser` class to represent a logged-in user and centralize account operations:
  - `update_balance_in_db()` — persists in-memory balance to the users table.
  - `record_transaction(amount, t_type="deposit")` — inserts timestamped transaction rows into transactions table.

- Updated `database.py` table definitions to better support transaction history (timestamp field and integer amount storage).
- These changes prepare the app for deposit, withdrawal, and transfer flows (Stage 4).

💰 Stage 4 — Deposit, Withdrawal & Balance Inquiry
Implemented deposit and withdrawal features with real-time balance updates. Added balance inquiry for users to view current account funds safely.


📜 Stage 5 — Transaction History Tracking
Created transaction logging for every deposit and withdrawal. Added view_transaction_history() to display detailed past transactions with timestamps.

Stage 6 —  Refactors the codebase for modularity also introduces core banking operations.
- Moved registration and login functions into the helpers.py
- Transfers now include PIN authentication, daily limit checks, transaction logs, and database-safe commits with rollback on error.
Improved balance display, user feedback, and concurrency handling.

