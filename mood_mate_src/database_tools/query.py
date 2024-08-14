import sqlite3
import os

DB_PATH = os.getenv("SQLITE_DB_PATH", "moodmate_db/mood_mate.db")

async def execute_query_with_lock(db_path,
                                  db_lock,
                                  query,
                                  params=(),
                                  return_result=False,
                                  dict_result=False):
    async with db_lock:
        conn = sqlite3.connect(db_path)
        if dict_result:
            conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        if return_result:
            result = cursor.fetchall()
            conn.close()
            if dict_result:
                result = [dict(row) for row in result]
            return result
        conn.close()
        
def execute_query(db_path, query, params=(), return_result=False, dict_result=False):
    conn = sqlite3.connect(db_path)
    if dict_result:
        conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(query, params)
    conn.commit()
    if return_result:
        result = cursor.fetchall()
        conn.close()
        if dict_result:
            result = [dict(row) for row in result]
        return result
    conn.close()