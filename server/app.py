"""
app.py — Flask Backend
Experiments covered:
  - Exp 7: Form design & validation (/register)
  - Exp 8: Serves the web app (deployed via Docker)
  - Exp 9: JSON & XML API endpoints for AJAX
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, jsonify, request, render_template, redirect, url_for, flash
from flask_cors import CORS
import sqlite3
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom
from datetime import datetime

from database import init_db, get_connection, reverse_engineer_schema
from sensor_sim import start_background_sensor

app = Flask(
    __name__,
    template_folder=os.path.join(os.path.dirname(__file__), '..', 'templates'),
    static_folder=os.path.join(os.path.dirname(__file__), '..', 'static')
)
app.secret_key = 'weather-station-secret-2024'
CORS(app)

# ── Helpers ──────────────────────────────────────────────────────────────────

def row_to_dict(row):
    return dict(row) if row else {}


def readings_to_xml(readings):
    """Convert readings list to pretty-printed XML string (Exp 9)."""
    root = Element('WeatherData')
    root.set('generated_at', datetime.utcnow().isoformat() + 'Z')
    for r in readings:
        entry = SubElement(root, 'Reading')
        for key, val in r.items():
            child = SubElement(entry, key)
            child.text = str(val) if val is not None else ''
    raw = tostring(root, encoding='unicode')
    return minidom.parseString(raw).toprettyxml(indent='  ')


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    """Dashboard page (Exp 6 & 9)."""
    return render_template('index.html')


@app.route('/api/current')
def api_current():
    """Latest single reading — polled every 3s via AJAX (Exp 9)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT r.*, s.name AS station_name, s.location
        FROM readings r
        JOIN stations s ON r.station_id = s.id
        ORDER BY r.id DESC LIMIT 1
    ''')
    row = cursor.fetchone()
    conn.close()
    return jsonify(row_to_dict(row) if row else {})


@app.route('/api/readings')
def api_readings():
    """Last N readings as JSON (Exp 9)."""
    limit = request.args.get('limit', 20, type=int)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT r.*, s.name AS station_name
        FROM readings r
        JOIN stations s ON r.station_id = s.id
        ORDER BY r.id DESC LIMIT ?
    ''', (limit,))
    rows = [row_to_dict(r) for r in cursor.fetchall()]
    conn.close()
    return jsonify({'count': len(rows), 'readings': rows[::-1]})  # oldest first


@app.route('/api/readings.xml')
def api_readings_xml():
    """Last N readings as XML (Exp 9 — XML support)."""
    limit = request.args.get('limit', 20, type=int)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT r.*, s.name AS station_name
        FROM readings r
        JOIN stations s ON r.station_id = s.id
        ORDER BY r.id DESC LIMIT ?
    ''', (limit,))
    rows = [row_to_dict(r) for r in cursor.fetchall()]
    conn.close()
    xml_str = readings_to_xml(rows[::-1])
    return app.response_class(xml_str, mimetype='application/xml')


@app.route('/api/alerts')
def api_alerts():
    """Latest alerts as JSON."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT a.*, s.name AS station_name
        FROM alerts a
        JOIN stations s ON a.station_id = s.id
        ORDER BY a.id DESC LIMIT 10
    ''')
    rows = [row_to_dict(r) for r in cursor.fetchall()]
    conn.close()
    return jsonify({'alerts': rows})


@app.route('/api/stations')
def api_stations():
    """List all registered stations."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM stations ORDER BY id")
    rows = [row_to_dict(r) for r in cursor.fetchall()]
    conn.close()
    return jsonify({'stations': rows})


@app.route('/api/submit', methods=['POST'])
def api_submit():
    """
    Accept manual readings from Tkinter GUI (Exp 10).
    Expects JSON: {station_id, temperature, humidity, pressure, wind_speed, wind_direction}
    """
    data = request.get_json(force=True)
    errors = {}

    try:
        temperature = float(data.get('temperature', ''))
        if not -50 <= temperature <= 60:
            errors['temperature'] = 'Must be between -50 and 60 °C'
    except (ValueError, TypeError):
        errors['temperature'] = 'Invalid number'

    try:
        humidity = float(data.get('humidity', ''))
        if not 0 <= humidity <= 100:
            errors['humidity'] = 'Must be between 0 and 100 %'
    except (ValueError, TypeError):
        errors['humidity'] = 'Invalid number'

    try:
        pressure = float(data.get('pressure', ''))
        if not 870 <= pressure <= 1085:
            errors['pressure'] = 'Must be between 870 and 1085 hPa'
    except (ValueError, TypeError):
        errors['pressure'] = 'Invalid number'

    try:
        wind_speed = float(data.get('wind_speed', ''))
        if not 0 <= wind_speed <= 200:
            errors['wind_speed'] = 'Must be between 0 and 200 km/h'
    except (ValueError, TypeError):
        errors['wind_speed'] = 'Invalid number'

    if errors:
        return jsonify({'success': False, 'errors': errors}), 400

    conn = get_connection()
    cursor = conn.cursor()
    station_id = data.get('station_id', 1)
    cursor.execute('''
        INSERT INTO readings (station_id, temperature, humidity, pressure, wind_speed, wind_direction, source)
        VALUES (?, ?, ?, ?, ?, ?, 'manual')
    ''', (station_id, temperature, humidity, pressure, wind_speed,
          data.get('wind_direction', 'N')))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': 'Reading submitted successfully!'})


# ── Experiment 7: Form Design & Validation ────────────────────────────────────

@app.route('/register', methods=['GET', 'POST'])
def register_station():
    """Station registration form with server-side validation (Exp 7)."""
    errors = {}
    form_data = {}

    if request.method == 'POST':
        name     = request.form.get('name', '').strip()
        location = request.form.get('location', '').strip()
        lat_str  = request.form.get('latitude', '').strip()
        lon_str  = request.form.get('longitude', '').strip()
        form_data = {'name': name, 'location': location,
                     'latitude': lat_str, 'longitude': lon_str}

        # Validation
        if not name:
            errors['name'] = 'Station name is required.'
        elif len(name) < 3:
            errors['name'] = 'Name must be at least 3 characters.'

        if not location:
            errors['location'] = 'Location is required.'

        try:
            lat = float(lat_str)
            if not -90 <= lat <= 90:
                errors['latitude'] = 'Latitude must be between -90 and 90.'
        except ValueError:
            errors['latitude'] = 'Enter a valid decimal number.'

        try:
            lon = float(lon_str)
            if not -180 <= lon <= 180:
                errors['longitude'] = 'Longitude must be between -180 and 180.'
        except ValueError:
            errors['longitude'] = 'Enter a valid decimal number.'

        if not errors:
            try:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO stations (name, location, latitude, longitude) VALUES (?,?,?,?)",
                    (name, location, lat, lon)
                )
                conn.commit()
                conn.close()
                flash(f'Station "{name}" registered successfully!', 'success')
                return redirect(url_for('register_station'))
            except sqlite3.IntegrityError:
                errors['name'] = f'Station name "{name}" already exists.'

    return render_template('register.html', errors=errors, form_data=form_data)


@app.route('/api/schema')
def api_schema():
    """Reverse Engineering: return DB schema as JSON (Exp 3)."""
    schema = reverse_engineer_schema()
    return jsonify({'schema': schema})


# ── Entry Point ───────────────────────────────────────────────────────────────

if __name__ == '__main__':
    init_db()
    start_background_sensor(interval=5)
    print("[Server] Starting Flask on http://0.0.0.0:5000")
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
