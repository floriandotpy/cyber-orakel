import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

SQLITE_DB_PATH = Path(__file__).parent.parent / "fortunes.db"


@dataclass
class Fortune:
    generation_time: datetime
    fortune: str
    prompt: str
    generation_duration: float
    zodiac_key: str
    sentiment: str


def log_to_sqlite(fortune_obj: Fortune):
    # Check if the database file exists
    db_exists = SQLITE_DB_PATH.exists()

    # Connect to the SQLite database
    conn = sqlite3.connect(SQLITE_DB_PATH)
    cursor = conn.cursor()

    # If the database does not exist, create the table
    if not db_exists:
        cursor.execute('''
            CREATE TABLE fortunes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                generation_time TEXT,
                fortune TEXT,
                prompt TEXT,
                generation_duration REAL,
                zodiac_key TEXT,
                sentiment TEXT
            )
        ''')
        conn.commit()

    # Insert the fortune object into the database
    cursor.execute('''
        INSERT INTO fortunes (generation_time, fortune, prompt, generation_duration, zodiac_key, sentiment)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        fortune_obj.generation_time.isoformat(),
        fortune_obj.fortune,
        fortune_obj.prompt,
        fortune_obj.generation_duration,
        fortune_obj.zodiac_key,
        fortune_obj.sentiment
    ))
    conn.commit()

    # Close the connection
    conn.close()
