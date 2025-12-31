import sqlite3
from datetime import datetime
from typing import Optional, Dict, Any

DB_PATH = "panjur.db"

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# ------------------ DB OLUŞTUR ------------------
def init_db():
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sensor_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TEXT NOT NULL,
                isik INTEGER NOT NULL,
                sicaklik REAL NOT NULL,
                nem REAL NOT NULL,
                mode TEXT NOT NULL,
                shutter TEXT NOT NULL
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS system_state (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        """)

        conn.execute(
            "INSERT OR IGNORE INTO system_state VALUES ('mode','AUTO')"
        )
        conn.execute(
            "INSERT OR IGNORE INTO system_state VALUES ('shutter','OPEN')"
        )

        conn.commit()

# ------------------ STATE ------------------
def get_state() -> Dict[str, str]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT key, value FROM system_state"
        ).fetchall()

        data = {r["key"]: r["value"] for r in rows}
        return {
            "mode": data.get("mode", "AUTO"),
            "shutter": data.get("shutter", "OPEN")
        }

def set_state(mode: Optional[str] = None, shutter: Optional[str] = None):
    with get_conn() as conn:
        if mode:
            conn.execute(
                """
                INSERT INTO system_state(key,value)
                VALUES('mode',?)
                ON CONFLICT(key) DO UPDATE SET value=excluded.value
                """,
                (mode,)
            )

        if shutter:
            conn.execute(
                """
                INSERT INTO system_state(key,value)
                VALUES('shutter',?)
                ON CONFLICT(key) DO UPDATE SET value=excluded.value
                """,
                (shutter,)
            )

        conn.commit()

# ------------------ SENSOR DATA ------------------
def insert_sensor_data(isik, sicaklik, nem, mode, shutter):
    ts = datetime.now().isoformat(timespec="seconds")
    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO sensor_data
            (ts, isik, sicaklik, nem, mode, shutter)
            VALUES (?,?,?,?,?,?)
            """,
            (ts, isik, sicaklik, nem, mode, shutter)
        )
        conn.commit()

def get_latest_sensor_data() -> Optional[Dict[str, Any]]:
    with get_conn() as conn:
        row = conn.execute(
            """
            SELECT ts, isik, sicaklik, nem, mode, shutter
            FROM sensor_data
            ORDER BY id DESC LIMIT 1
            """
        ).fetchone()

        return dict(row) if row else None

def get_history_data(limit: int = 15):
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT ts, isik, sicaklik, nem
            FROM sensor_data
            ORDER BY id DESC LIMIT ?
            """,
            (limit,)
        ).fetchall()

        return [dict(r) for r in reversed(rows)]
