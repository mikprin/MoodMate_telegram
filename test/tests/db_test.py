import os
import sqlite3
import time
import unittest
import asyncio

os.environ["SQLITE_DB_PATH"] = "./test_db.db"

from mood_mate_src.database_tools.db_init import init_db, table_exists
from mood_mate_src.database_tools.query import DB_PATH
from mood_mate_src.database_tools.users import USERS_DB_TABLE
from mood_mate_src.database_tools.mood_data import (
    DATA_TABLE,
    add_mood_record_to_db,
    MoodData,
    MoodRecord,
)

# def test_init_db():
    
#     print(f"DB_PATH: {DB_PATH}")
#     init_db()
    
#     # print (table_exists(DB_PATH, USERS_DB_TABLE))
    
#     # Check if the USERS_DB_TABLE table exists
#     assert table_exists(DB_PATH, USERS_DB_TABLE)
#     assert table_exists(DB_PATH, DATA_TABLE)

class TestAddMoodRecordToDb(unittest.TestCase):

    def setUp(self):
        print(f"DB_PATH: {DB_PATH}")
        # Set up an in-memory SQLite database
        init_db()

    def tearDown(self):
        # Drop the table
        # Close the database connection
        self.conn.close()
        # Remove the database file after the test
        os.remove(os.getenv("SQLITE_DB_PATH"))

    def test_add_mood_record_to_db(self):
        
        # Define the test data
        data = MoodData(
            user_id = 1,
            date = '01.01.2021',
            mood = 5,
            sleep = 7,
            horny = 3,
            exercise = 1,
            dopings = ['Caffeine'],
            energy = 8,
            anxiety = 2,
            period = False,
            note = 'Feeling good',
            extra = {},
        )
        
        record = MoodRecord(
            user_id = 1,
            date = '01.01.2021',
            created_at = int(time.time()),
            data = data,
        )

        # Call the function to test
        # Use asincio.run() to run the async function
        asyncio.run(add_mood_record_to_db(record))
    
        self.conn = sqlite3.connect(os.getenv("SQLITE_DB_PATH"))
        self.cursor = self.conn.cursor()
        # Verify the record was inserted correctly
        self.cursor.execute(f'SELECT * FROM {DATA_TABLE} WHERE user_id = {record.user_id}')
        record = self.cursor.fetchone()
        print(f"Record: {record}")
        self.assertIsNotNone(record)

if __name__ == '__main__':
    unittest.main()