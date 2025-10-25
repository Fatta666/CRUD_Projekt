import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'database.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS produkty (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nazwa TEXT NOT NULL,
            cena REAL NOT NULL,
            kategoria TEXT NOT NULL,
            ilosc INTEGER NOT NULL,
            producent TEXT,
            data_dodania TEXT
        );
    ''')
    conn.commit()
    conn.close()

def init_users_table():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            login TEXT UNIQUE NOT NULL,
            hasloHash TEXT NOT NULL,
            rola TEXT NOT NULL DEFAULT 'USER',
            created_at TEXT NOT NULL
        );
    ''')
    conn.commit()
    conn.close()
