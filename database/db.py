# database/db.py

import sqlite3
from pathlib import Path

DB_PATH = Path("database/smid.db")

def conectar():
    """Conecta ao banco de dados SQLite."""
    conn = sqlite3.connect(DB_PATH)
    return conn

def criar_tabelas():
    """Cria a tabela de usuários se não existir"""
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL,
            senha TEXT NOT NULL,
            tipo TEXT NOT NULL  -- cliente, gestor, operador
        )
    ''')

    conn.commit()
    conn.close()