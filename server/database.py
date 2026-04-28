"""
database.py — Forward Engineering from ER Diagram
ER Entities: Station, Reading, Alert
Relationships: Station has many Readings; Reading may trigger Alert
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'weather.db')


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Forward Engineering: Creates tables from ER model."""
    conn = get_connection()
    cursor = conn.cursor()

    # ER Entity: Station
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stations (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT NOT NULL UNIQUE,
            location    TEXT NOT NULL,
            latitude    REAL,
            longitude   REAL,
            registered_at TEXT DEFAULT (datetime('now'))
        )
    ''')

    # ER Entity: Reading (weak entity — depends on Station)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS readings (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            station_id      INTEGER NOT NULL,
            temperature     REAL NOT NULL,
            humidity        REAL NOT NULL,
            pressure        REAL NOT NULL,
            wind_speed      REAL NOT NULL,
            wind_direction  TEXT DEFAULT 'N',
            recorded_at     TEXT DEFAULT (datetime('now')),
            source          TEXT DEFAULT 'auto',
            FOREIGN KEY (station_id) REFERENCES stations(id)
        )
    ''')

    # ER Entity: Alert (generated when threshold crossed)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alerts (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            station_id  INTEGER NOT NULL,
            reading_id  INTEGER NOT NULL,
            alert_type  TEXT NOT NULL,
            message     TEXT NOT NULL,
            triggered_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (station_id) REFERENCES stations(id),
            FOREIGN KEY (reading_id) REFERENCES readings(id)
        )
    ''')

    # Seed a default station
    cursor.execute('''
        INSERT OR IGNORE INTO stations (name, location, latitude, longitude)
        VALUES ('Station Alpha', 'Main Campus', 12.9716, 77.5946)
    ''')

    conn.commit()
    conn.close()
    print("[DB] Database initialized (Forward Engineering complete)")


def reverse_engineer_schema():
    """
    Reverse Engineering: Extract schema info from existing DB
    Returns dict of table -> columns (simulates reverse engineering).
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row['name'] for row in cursor.fetchall()]

    schema = {}
    for table in tables:
        cursor.execute(f"PRAGMA table_info({table})")
        cols = cursor.fetchall()
        schema[table] = [
            {
                'col_id': c['cid'],
                'name': c['name'],
                'type': c['type'],
                'not_null': bool(c['notnull']),
                'default': c['dflt_value'],
                'primary_key': bool(c['pk'])
            }
            for c in cols
        ]
    conn.close()
    return schema


if __name__ == '__main__':
    init_db()
    schema = reverse_engineer_schema()
    print("\n[Reverse Engineering] Extracted Schema:")
    for table, cols in schema.items():
        print(f"\nTable: {table}")
        for col in cols:
            pk = " [PK]" if col['primary_key'] else ""
            nn = " NOT NULL" if col['not_null'] else ""
            print(f"  {col['name']} {col['type']}{pk}{nn}")
