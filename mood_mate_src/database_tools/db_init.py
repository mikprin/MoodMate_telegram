import sqlite3

from mood_mate_src.database_tools.locks import user_db_lock
from mood_mate_src.database_tools.query import execute_query_with_lock, DB_PATH
from mood_mate_src.database_tools.users import USERS_DB_TABLE
from mood_mate_src.database_tools.mood_data import DATA_TABLE
from mood_mate_src.mate_logger import logger

def table_exists(db_path, table_name):
    """
    Check if a table exists in the SQLite database.

    :param db_path: Path to the SQLite database file.
    :param table_name: Name of the table to check.
    :return: True if the table exists, False otherwise.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f'''
    SELECT name FROM sqlite_master WHERE type='table' AND name=?;
    ''', (table_name,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if the USERS_DB_TABLE table exists
    
    if not table_exists(DB_PATH, USERS_DB_TABLE):
        init_user_db()

    # Check if the DATA_TABLE table exists
    if not table_exists(DB_PATH, DATA_TABLE):
        init_data_db()

def init_user_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(f'''CREATE TABLE {USERS_DB_TABLE}
                 (user_id INTEGER PRIMARY KEY,
                 chat_id INTEGER NOT NULL,
                 settings JSON)''')
    conn.commit()
    conn.close()
    logger.info(f"Table {USERS_DB_TABLE} created in the database {DB_PATH}")
    
    
def init_data_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(f'''CREATE TABLE {DATA_TABLE}
                (
                user_id INTEGER,
                date DATE NOT NULL,
                created_at INTEGER NOT NULL,
                data JSON NOT NULL)''')
    conn.commit()
    conn.close()
    logger.info(f"Table {DATA_TABLE} created. In the database {DB_PATH}")