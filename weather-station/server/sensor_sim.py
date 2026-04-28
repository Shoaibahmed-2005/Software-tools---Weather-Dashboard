"""
sensor_sim.py — Simulated Weather Sensor
Generates realistic weather readings and stores them in the DB every 5 seconds.
Runs as a background daemon thread inside Flask.
"""
import threading
import random
import time
import math
from database import get_connection

# Thresholds for alert generation
THRESHOLDS = {
    'temperature': {'min': 5.0, 'max': 42.0, 'label': 'Temperature Alert'},
    'humidity':    {'min': 10.0, 'max': 95.0, 'label': 'Humidity Alert'},
    'wind_speed':  {'max': 80.0, 'label': 'High Wind Alert'},
}

WIND_DIRS = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']

# Smooth random walk state
_state = {
    'temperature': 28.0,
    'humidity': 60.0,
    'pressure': 1013.25,
    'wind_speed': 12.0,
    'wind_dir_idx': 0,
    'tick': 0
}


def _next_value(current, delta_range, min_val, max_val):
    """Smooth random walk — feels like real sensor data."""
    delta = random.uniform(-delta_range, delta_range)
    return round(max(min_val, min(max_val, current + delta)), 2)


def _generate_reading():
    """Generate one set of simulated sensor readings."""
    _state['tick'] += 1
    # Add a gentle sine wave for temperature (simulates day/night)
    sine_offset = 3.0 * math.sin(_state['tick'] * 0.05)

    _state['temperature'] = _next_value(
        _state['temperature'] + sine_offset * 0.05, 0.8, -10.0, 50.0)
    _state['humidity']    = _next_value(_state['humidity'], 1.5, 0.0, 100.0)
    _state['pressure']    = _next_value(_state['pressure'], 0.5, 950.0, 1050.0)
    _state['wind_speed']  = _next_value(_state['wind_speed'], 2.0, 0.0, 120.0)
    _state['wind_dir_idx'] = (_state['wind_dir_idx'] +
                               random.choice([-1, 0, 0, 1])) % len(WIND_DIRS)

    return {
        'temperature': _state['temperature'],
        'humidity':    _state['humidity'],
        'pressure':    _state['pressure'],
        'wind_speed':  _state['wind_speed'],
        'wind_direction': WIND_DIRS[_state['wind_dir_idx']],
        'source': 'auto'
    }


def _check_and_insert_alerts(conn, station_id, reading_id, reading):
    """Check thresholds and insert alerts if needed."""
    cursor = conn.cursor()
    if reading['temperature'] > THRESHOLDS['temperature']['max']:
        cursor.execute(
            "INSERT INTO alerts (station_id, reading_id, alert_type, message) VALUES (?,?,?,?)",
            (station_id, reading_id, 'HIGH_TEMP',
             f"Temperature {reading['temperature']}°C exceeds max threshold!")
        )
    if reading['temperature'] < THRESHOLDS['temperature']['min']:
        cursor.execute(
            "INSERT INTO alerts (station_id, reading_id, alert_type, message) VALUES (?,?,?,?)",
            (station_id, reading_id, 'LOW_TEMP',
             f"Temperature {reading['temperature']}°C below min threshold!")
        )
    if reading['wind_speed'] > THRESHOLDS['wind_speed']['max']:
        cursor.execute(
            "INSERT INTO alerts (station_id, reading_id, alert_type, message) VALUES (?,?,?,?)",
            (station_id, reading_id, 'HIGH_WIND',
             f"Wind speed {reading['wind_speed']} km/h — High wind warning!")
        )
    conn.commit()


def sensor_loop(interval=5):
    """Continuously generate and store readings."""
    print(f"[Sensor] Starting auto-simulation (interval={interval}s)")
    while True:
        try:
            conn = get_connection()
            cursor = conn.cursor()

            # Use first station
            cursor.execute("SELECT id FROM stations LIMIT 1")
            row = cursor.fetchone()
            if row:
                station_id = row['id']
                reading = _generate_reading()

                cursor.execute('''
                    INSERT INTO readings
                        (station_id, temperature, humidity, pressure,
                         wind_speed, wind_direction, source)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    station_id,
                    reading['temperature'], reading['humidity'],
                    reading['pressure'],   reading['wind_speed'],
                    reading['wind_direction'], reading['source']
                ))
                conn.commit()
                reading_id = cursor.lastrowid
                _check_and_insert_alerts(conn, station_id, reading_id, reading)

            conn.close()
        except Exception as e:
            print(f"[Sensor] Error: {e}")
        time.sleep(interval)


def start_background_sensor(interval=5):
    """Start the sensor loop as a background daemon thread."""
    t = threading.Thread(target=sensor_loop, args=(interval,), daemon=True)
    t.start()
    return t
