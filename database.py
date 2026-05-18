import sqlite3
import datetime as dt
from config import get_env, set_env, valid_date_format, valid_time_format
from pathlib import Path
import argparse


def initialize_db(db_path: str = None):
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

        cursor = con.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='readings';")

        if cursor.fetchone() is None:
            print("Connection was established, but table creation failed.")
            return None
        else:
            return con

    except sqlite3.Error as e:
        print(f"Failed to connect or write to the database. Reason: {e}.")


def add_reading(con, o2, temp, press, date=None):
    if con is None:
        return

    if not date:
        date = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    con.execute(""" INSERT INTO readings(o2, temp, press, timestamp)
                VALUES (?, ?, ?, ?);
                """, (o2, temp, press, date))
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

    if not con:
        exit(1)

    parser = argparse.ArgumentParser(description="Table Insertion Tool")
    parser.add_argument(
        "-o", "--oxygen",
        type=float,
        help="Oxygen concentration must be given in the format XX.XX or XX.X or XX",
        default=20.00
    )
    parser.add_argument(
        "-t", "--temp",
        type=float,
        help="Internal temperature must be given in the format XX.X or XX",
        default=30.0
    )
    parser.add_argument(
        "-p", "--press",
        type=float,
        help="Internal pressure must be given in the format XX",
        default=1000
    )
    parser.add_argument(
        "-d", "--date",
        type=str,
        help="Target date must be given in the format YYYY-MM-DD. Default to current system date",
        default=None
    )
    parser.add_argument(
        "-c", "--time",
        type=str,
        help="Target time must be given in the format HH:MM:SS. Default to current system time",
        default=None
    )
    args = parser.parse_args()

    o2_level = round(args.oxygen, 2)
    internal_temperature_level = round(args.temp, 1)
    internal_pressure_level = round(args.press, 0)
   
    target_date = args.date
    if target_date:
        target_date = target_date.strip()
        if not valid_date_format(target_date):
            print(
                f"{target_date} does not conform to the YYYY-MM-DD date format. Exitting here.")
            exit(1)
    else:
        target_date = dt.datetime.now().strftime("%Y-%m-%d")
    
    target_time = args.time
    if target_time:
        if not valid_time_format(target_time):
            print(f"{target_time} does not conform to the HH:MM:SS time format. Exitting here.")
            exit(1)
    else:
        target_time = dt.datetime.now().strftime("%H:%M:%S")

    timestamp = "".join([target_date, " ", target_time])

    add_reading(con, o2_level, internal_temperature_level,
                internal_pressure_level, timestamp)
