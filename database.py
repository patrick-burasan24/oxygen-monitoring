import sqlite3
import os
from dotenv import load_dotenv
import datetime as dt

def initialize_db(db_path):
    con = sqlite3.connect(db_path)
    con.execute(""" CREATE TABLE IF NOT EXISTS readings(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    o2 DECIMAL(4, 2) NOT NULL,
                    temp DECIMAL(3, 1) NOT NULL,
                    press INT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                );
                """)
    return con

def add_reading(con, o2, temp, press):
    local_now = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    con.execute(""" INSERT INTO readings(o2, temp, press, timestamp)
                VALUES (?, ?, ?, ?);
                """, (o2, temp, press, local_now))
    con.commit()

def summary(con):
    query = con.execute("""
                        SELECT
                        MIN(o2), MAX(o2), AVG(o2),
                        MIN(temp), MAX(temp), AVG(temp),
                        MIN(press), MAX(press), AVG(press)
                        FROM readings
                        WHERE date(timestamp) = date('now')
                        """)
    row = query.fetchone()

    return {
        "o2": {"min": row[0], "max": row[1], "avg": row[2]},
        "temp": {"min": row[3], "max": row[4], "avg": row[5]},
        "press": {"min": row[6], "max": row[7], "avg": row[8]}
    }

if __name__ == "__main__":
    load_dotenv("./data.env")

    DATABASE_PATH = os.getenv("DATABASE_PATH")

    if DATABASE_PATH is None:
        print("Error finding the database. Exiting here.")
        exit(1)
    
    assert(DATABASE_PATH is not None)

    con = initialize_db(DATABASE_PATH)