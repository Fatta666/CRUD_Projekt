import sqlite3

def get_db_connection():
    conn = sqlite3.connect('database.db')
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
            ilosc INTEGER NOT NULL
        );
    ''')
    conn.commit()
    conn.close()


