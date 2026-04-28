import os
import pymssql

SERVER = os.getenv("SQL_SERVER")
DATABASE = os.getenv("SQL_DATABASE", "banking")
USERNAME = os.getenv("SQL_USERNAME")
PASSWORD = os.getenv("SQL_PASSWORD")

async def get_connection():
    conn = pymssql.connect(SERVER, USERNAME, PASSWORD, DATABASE)
    try:
        yield conn
    finally:
        conn.close()

async def init_db():
    conn = pymssql.connect(SERVER, USERNAME, PASSWORD, DATABASE)
    cursor = conn.cursor()
    cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='accounts' AND xtype='U')
        CREATE TABLE accounts (
            id VARCHAR(36) PRIMARY KEY,
            owner_name NVARCHAR(100) NOT NULL,
            email NVARCHAR(100) UNIQUE NOT NULL,
            password_hash NVARCHAR(255) NOT NULL,
            account_type VARCHAR(20) NOT NULL,
            balance DECIMAL(18,2) DEFAULT 0.00,
            is_active BIT DEFAULT 1,
            created_at DATETIME2 DEFAULT GETUTCDATE()
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()