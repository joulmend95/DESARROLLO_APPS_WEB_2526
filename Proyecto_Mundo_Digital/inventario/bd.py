"""
Módulo para la gestión de la base de datos SQLite
"""
import sqlite3

def get_db_connection():
    """
    Establece y retorna una conexión a la base de datos SQLite
    """
    conn = sqlite3.connect('inventario.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """
    Inicializa la base de datos y crea la tabla si no existe
    """
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            cantidad INTEGER NOT NULL,
            precio REAL NOT NULL,
            categoria TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()
