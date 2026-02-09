import sqlite3
from datetime import datetime

def init_db():
    """ایجاد دیتابیس و جدول وظایف"""
    conn = sqlite3.connect('todos.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS todos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task TEXT NOT NULL,
            description TEXT,
            priority INTEGER DEFAULT 1,
            completed BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            due_date DATE
        )
    ''')
    
    # ایجاد ایندکس برای جستجوی بهتر
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_completed ON todos(completed)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_priority ON todos(priority)')
    
    conn.commit()
    conn.close()

def get_db_connection():
    """اتصال به دیتابیس"""
    conn = sqlite3.connect('todos.db')
    conn.row_factory = sqlite3.Row
    return conn
