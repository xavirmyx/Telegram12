import sqlite3
import logging
from datetime import datetime

DB_PATH = "bot_data.db"
logger = logging.getLogger(__name__)

def get_connection():
    """Obtener conexión a la base de datos."""
    return sqlite3.connect(DB_PATH)

def init_db():
    """Inicializar la base de datos y crear las tablas necesarias."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        
        # Crear tabla de usuarios
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            telegram_id INTEGER UNIQUE,
                            username TEXT)''')
        
        # Crear tabla de advertencias
        cursor.execute('''CREATE TABLE IF NOT EXISTS warnings (
                            user_id INTEGER PRIMARY KEY,
                            message_id INTEGER,
                            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
        
        # Crear tabla de logs
        cursor.execute('''CREATE TABLE IF NOT EXISTS logs (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_id INTEGER,
                            event TEXT,
                            chat_id INTEGER,
                            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
        
        conn.commit()
    except Exception as e:
        logger.error(f"Error al inicializar la base de datos: {e}")
    finally:
        conn.close()

def add_user(telegram_id: int, username: str):
    """Agregar un usuario a la base de datos si no existe."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO users (telegram_id, username) VALUES (?, ?)", (telegram_id, username))
        conn.commit()
    except Exception as e:
        logger.error(f"Error al agregar usuario: {e}")
    finally:
        conn.close()

def save_warning(user_id: int, message_id: int):
    """Guardar una advertencia en la base de datos."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO warnings (user_id, message_id) VALUES (?, ?)", (user_id, message_id))
        conn.commit()
    except Exception as e:
        logger.error(f"Error al guardar advertencia: {e}")
    finally:
        conn.close()

def remove_warning(user_id: int) -> bool:
    """Eliminar una advertencia de la base de datos. Devuelve True si se eliminó."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM warnings WHERE user_id = ?", (user_id,))
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        logger.error(f"Error al eliminar advertencia: {e}")
        return False
    finally:
        conn.close()

def log_event(user_id: int, event: str, chat_id: int):
    """Registrar un evento en la base de datos."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO logs (user_id, event, chat_id) VALUES (?, ?, ?)", (user_id, event, chat_id))
        conn.commit()
    except Exception as e:
        logger.error(f"Error al registrar evento: {e}")
    finally:
        conn.close()
