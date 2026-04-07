import sqlite3
import pandas as pd
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "expenses.db")


def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = get_connection()
    c = conn.cursor()

    # Expenses table
    c.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            user TEXT NOT NULL DEFAULT 'default',
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)

    # Budgets table
    c.execute("""
        CREATE TABLE IF NOT EXISTS budgets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            monthly_limit REAL NOT NULL,
            user TEXT NOT NULL DEFAULT 'default',
            UNIQUE(category, user)
        )
    """)

    # Users table (Version 3: multi-user)
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            currency TEXT DEFAULT 'USD',
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)

    # Insert default user if not exists
    c.execute("INSERT OR IGNORE INTO users (username, password) VALUES ('default', 'default')")

    conn.commit()
    conn.close()


# ─── EXPENSE CRUD ───────────────────────────────────────────────────

def add_expense(date, amount, category, description, user="default"):
    conn = get_connection()
    conn.execute(
        "INSERT INTO expenses (date, amount, category, description, user) VALUES (?,?,?,?,?)",
        (date, amount, category, description, user)
    )
    conn.commit()
    conn.close()


def get_expenses(user="default"):
    conn = get_connection()
    df = pd.read_sql_query(
        "SELECT * FROM expenses WHERE user=? ORDER BY date DESC, id DESC",
        conn, params=(user,)
    )
    conn.close()
    return df


def update_expense(expense_id, date, amount, category, description):
    conn = get_connection()
    conn.execute(
        "UPDATE expenses SET date=?, amount=?, category=?, description=? WHERE id=?",
        (date, amount, category, description, expense_id)
    )
    conn.commit()
    conn.close()


def delete_expense(expense_id):
    conn = get_connection()
    conn.execute("DELETE FROM expenses WHERE id=?", (expense_id,))
    conn.commit()
    conn.close()


def import_expenses_csv(df, user="default"):
    conn = get_connection()
    for _, row in df.iterrows():
        conn.execute(
            "INSERT INTO expenses (date, amount, category, description, user) VALUES (?,?,?,?,?)",
            (str(row["date"]), float(row["amount"]), str(row["category"]),
             str(row.get("description", "")), user)
        )
    conn.commit()
    conn.close()


# ─── BUDGET CRUD ─────────────────────────────────────────────────────

def set_budget(category, monthly_limit, user="default"):
    conn = get_connection()
    conn.execute(
        "INSERT INTO budgets (category, monthly_limit, user) VALUES (?,?,?) "
        "ON CONFLICT(category, user) DO UPDATE SET monthly_limit=excluded.monthly_limit",
        (category, monthly_limit, user)
    )
    conn.commit()
    conn.close()


def get_budgets(user="default"):
    conn = get_connection()
    df = pd.read_sql_query(
        "SELECT * FROM budgets WHERE user=? ORDER BY category",
        conn, params=(user,)
    )
    conn.close()
    return df


def delete_budget(budget_id):
    conn = get_connection()
    conn.execute("DELETE FROM budgets WHERE id=?", (budget_id,))
    conn.commit()
    conn.close()


# ─── USER MANAGEMENT (Version 3) ─────────────────────────────────────

def register_user(username, password, currency="USD"):
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO users (username, password, currency) VALUES (?,?,?)",
            (username, password, currency)
        )
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False


def authenticate_user(username, password):
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (username, password)
    ).fetchone()
    conn.close()
    return row is not None


def get_users():
    conn = get_connection()
    df = pd.read_sql_query("SELECT username, currency, created_at FROM users", conn)
    conn.close()
    return df


def update_currency(username, currency):
    conn = get_connection()
    conn.execute("UPDATE users SET currency=? WHERE username=?", (currency, username))
    conn.commit()
    conn.close()


def get_currency(username):
    conn = get_connection()
    row = conn.execute("SELECT currency FROM users WHERE username=?", (username,)).fetchone()
    conn.close()
    return row[0] if row else "USD"
