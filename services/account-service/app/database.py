import os
import aioodbc
from typing import AsyncGenerator

CONNECTION_STRING = os.getenv("SQL_CONNECTION_STRING")

async def get_connection() -> AsyncGenerator:
    conn = await aioodbc.connect(dsn=CONNECTION_STRING)
    try:
        yield conn
    finally:
        await conn.close()

async def init_db():
    conn = await aioodbc.connect(dsn=CONNECTION_STRING)
    cursor = await conn.cursor()
    await cursor.execute("""
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
    await conn.commit()
    await cursor.close()
    await conn.close()
