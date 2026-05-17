import sqlite3
import datetime as dt
from config import get_env, set_env
from pathlib import Path

def initialize_db(db_path:str = None):
    """Initializes the connection to the database at db_path. Creates the
    database if it doesn't exist."""

    if not db_path:
        default_db = Path.home() / ".o2m" / "sensor_readings.db"
        db_path = get_env("DATABASE_PATH", str(default_db))
    
    if not db_path.endswith(".db"):
        print(db_path)
        print("Error: The database entension must end with .db")
        return
    
    try:
        con = sqlite3.connect(db_path)
        con.execute(""" CREATE TABLE IF NOT EXISTS readings(
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        o2 REAL NOT NULL,
                        temp REAL NOT NULL,
                        press REAL NOT NULL,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    );
                    """)
        
        set_env("DATABASE_PATH", db_path)
        
        cursor = con.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='readings';")

        if cursor.fetchone() is None:
            print("Connection was established, but table creation failed.")
            return None
        else:
            return con
    
    except sqlite3.Error as e:
        print(f"Failed to connect or write to the database. Reason: {e}.")        

def add_reading(con, o2, temp, press):
    if con is None:
        return

    local_now = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    con.execute(""" INSERT INTO readings(o2, temp, press, timestamp)
                VALUES (?, ?, ?, ?);
                """, (o2, temp, press, local_now))
    con.commit()

def summary(con, target_date):
    if con is None:
        return
    
    if target_date is None:
        target_date = dt.datetime.today().strftime("%Y-%m-%d")

    query = con.execute("""
                        SELECT
                        MIN(o2), MAX(o2), AVG(o2),
                        MIN(temp), MAX(temp), AVG(temp),
                        MIN(press), MAX(press), AVG(press)
                        FROM readings
                        WHERE date(timestamp) = ?
                        """, (target_date,))
    row = query.fetchone()

    if row[0] is None:
        return None
    return {
        "o2": {"min": round(row[0], 2), "max": round(row[1], 2), "avg": round(row[2], 2)},
        "temp": {"min": round(row[3], 1), "max": round(row[4], 1), "avg": round(row[5], 1)},
        "press": {"min": round(row[6], 0), "max": round(row[7], 0), "avg": round(row[8], 0)}
    }

def get_daily_timeseries(con, target_date):
    if con is None:
        return
    
    if target_date is None:
        target_date = dt.datetime.today().strftime("%Y-%m-%d")
    
    query = con.execute(""" SELECT timestamp, o2, temp, press
                        FROM readings
                        WHERE date(timestamp) = ?
                        ORDER BY timestamp ASC
                        """, (target_date,))
    rows = query.fetchall()
    
    if len(rows) == 0:
        return None
    return rows

if __name__ == "__main__":
    DATABASE_PATH = get_env("DATABASE_PATH")
    con = initialize_db(DATABASE_PATH)

    add_reading(con, 25.01, 35, 1004)