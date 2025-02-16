import sqlite3
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def init_db():
    """
    Initialize database and create necessary tables
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        
        # Create warnings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS warnings (
                user_id INTEGER PRIMARY KEY,
                message_id INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                event TEXT,
                chat_id INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
    except Exception as e:
        logger.error(f"Database initialization error: {e}")
    finally:
        conn.close()

def get_connection():
    """
    Get database connection
    """
    return sqlite3.connect("bot_data.db")

def save_warning(user_id: int, message_id: int):
    """
    Save warning to database
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO warnings (user_id, message_id) VALUES (?, ?)",
            (user_id, message_id)
        )
        conn.commit()
    except Exception as e:
        logger.error(f"Error saving warning: {e}")
    finally:
        conn.close()

def remove_warning(user_id: int) -> bool:
    """
    Remove warning from database
    Returns True if warning was found and removed
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM warnings WHERE user_id = ?", (user_id,))
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        logger.error(f"Error removing warning: {e}")
        return False
    finally:
        conn.close()

def log_event(user_id: int, event: str, chat_id: int):
    """
    Log event to database
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO logs (user_id, event, chat_id) VALUES (?, ?, ?)",
            (user_id, event, chat_id)
        )
        conn.commit()
    except Exception as e:
        logger.error(f"Error logging event: {e}")
    finally:
        conn.close()
