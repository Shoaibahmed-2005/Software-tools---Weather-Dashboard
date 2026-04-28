
# Real-Time Weather Station Dashboard
## Mini Project Report â€” Software Tools Laboratory (Mini Project #13)

---

## Section 1: Abstract

This report presents the design, development, and deployment of a **Real-Time Weather Station Dashboard**, implemented as Mini Project #13 in fulfilment of the Software Tools Laboratory curriculum covering Experiments 1 through 12. The project is a full-stack web application that integrates twelve distinct software engineering tools and paradigms into a single, cohesive system.

A Python 3.11 backend built on the Flask 3.0 micro-framework hosts a RESTful API that serves live weather data in both JSON and XML formats. A simulated sensor thread generates realistic atmospheric readings â€” temperature, humidity, barometric pressure, wind speed, and wind direction â€” using a smooth random-walk algorithm augmented with a sinusoidal day/night cycle. These readings are persisted in an SQLite relational database whose schema was derived by forward engineering from an Entity-Relationship (ER) diagram. The same database schema can be extracted at runtime via a reverse-engineering endpoint, demonstrating both directions of the software engineering cycle.

The web dashboard (HTML5, Vanilla CSS dark glassmorphism, JavaScript ES2022) polls the Flask API every three seconds via Asynchronous JavaScript and XML (AJAX), dynamically updating metric cards, a Chart.js multi-line time-series graph, a CSS compass needle, and a live alert banner â€” all without page reload. An additional toggle allows the frontend to switch the data source between JSON and XML, demonstrating both interchange formats in Experiment 9.

A Python Tkinter desktop application allows operators to submit manual sensor readings to the server, while a Bash shell script (`start.sh`) automates environment setup, dependency installation, network diagnostics, database initialisation, and server launch. Docker and Docker Compose enable single-command containerised deployment. The project is version-controlled with Git, and the technical documentation is authored in LaTeX. Together, these components form an end-to-end demonstration of modern software tooling practices.

---

## Section 2: Introduction

The measurement and monitoring of atmospheric conditions is a foundational task in domains ranging from agriculture and aviation to civil infrastructure and disaster management. Modern weather monitoring systems are expected to be always-on, low-latency, remotely accessible, and capable of ingesting data from heterogeneous sources. Building such a system from first principles provides an ideal context for practising the breadth of software tools covered in a university-level Software Tools laboratory.

Mini Project #13 â€” the **Real-Time Weather Station Dashboard** â€” was conceived to serve this dual purpose: to function as a genuinely useful atmospheric monitoring application, and simultaneously to demonstrate the practical application of each of the twelve experiments prescribed in the laboratory syllabus.

The project is structured around a client-server architecture. At the server tier, a Flask application exposes a set of RESTful API endpoints backed by an SQLite database. A background thread continuously simulates sensor readings and writes them to the database, while a separate thread-safe module checks network connectivity. At the client tier, a JavaScript-powered HTML5 dashboard consumes the API over AJAX and renders data using Chart.js visualisations. A standalone Python Tkinter GUI provides a desktop interface for manual data entry, communicating with the server over HTTP.

The entire stack is containerised using Docker, launched via a Bash automation script, documented in LaTeX, and tracked in a Git repository â€” ensuring that every experiment from 1 to 12 is concretely represented in the final codebase. This report documents the rationale, design decisions, implementation details, and observed outputs of the complete system.

---

## Section 3: Scope and Objectives

### 3.1 Scope

The scope of this project encompasses the complete software development lifecycle of a weather station monitoring system, from conceptual modelling through deployment. The system is scoped to:

- Simulate weather sensor data internally (no physical hardware required), providing a self-contained demonstration environment.
- Persist readings in a local SQLite database â€” a lightweight, file-based RDBMS suitable for a single-server deployment.
- Serve data through a RESTful HTTP API that supports both JSON and XML response formats.
- Present a live, auto-refreshing dashboard accessible through any modern web browser.
- Provide a desktop GUI for manual data entry without requiring browser access.
- Be deployable on any operating system (Windows, macOS, Linux) either directly via Python or via Docker containerisation.
- Demonstrate twelve specific software tool categories as mandated by the laboratory curriculum.

The scope explicitly excludes: integration with real physical sensors, cloud-based database hosting, user authentication/authorisation, and mobile-native application development.

### 3.2 Objectives

The primary objectives of this project are:

1. **Experiment 1 (DFD & ER Diagram):** Model the system data flow using a Data Flow Diagram (DFD) and define the relational data model using an Entity-Relationship (ER) diagram with entities `Station`, `Reading`, and `Alert`.

2. **Experiment 2 (UML Diagrams):** Produce UML Class, Sequence, and Use Case diagrams to formally describe the object-oriented structure and runtime behaviour of the system.

3. **Experiment 3 (Forward/Reverse Engineering):** Implement forward engineering by generating the SQLite schema from the ER model (`database.py â†’ init_db()`), and implement reverse engineering by programmatically extracting the live schema via `PRAGMA table_info` and exposing it at `/api/schema`.

4. **Experiment 4 (Shell Script):** Write a production-quality Bash script (`start.sh`) that automates virtual environment setup, dependency installation, network checks, database initialisation, server launch, health polling, and log tailing.

5. **Experiment 5 (Network Interface Check):** Develop `network_check.py` to enumerate all active network interfaces, test internet connectivity via Google DNS, and verify Flask server reachability using raw TCP socket connections.

6. **Experiment 6 (JavaScript Dynamic Pages):** Build a JavaScript-driven dashboard (`app.js`) that dynamically updates DOM elements â€” metric cards, progress bars, compass, chart â€” without full-page reload, using `fetch()` and `DOMParser`.

7. **Experiment 7 (Flask Forms & Validation):** Implement a station registration form (`/register`) with both client-side (HTML5 constraint API) and server-side (Python) validation, persisting valid records to the database and returning inline error messages.

8. **Experiment 8 (Docker Deployment):** Package the application into a Docker image using a multi-step `Dockerfile` and orchestrate it with `docker-compose.yml`, including a health-check, volume mount for database persistence, and environment variable injection.

9. **Experiment 9 (AJAX + JSON/XML):** Provide dual-format API endpoints (`/api/readings` for JSON, `/api/readings.xml` for XML), and implement client-side toggling between formats using `fetch()` + `DOMParser`, demonstrating both data interchange standards.

10. **Experiment 10 (Python GUI â€” Tkinter):** Create a desktop application (`station_gui.py`) using Python's built-in `tkinter` library that fetches the station list from the server, validates user input locally, and POSTs readings to `/api/submit`.

11. **Experiment 11 (LaTeX Documentation):** Author a structured technical report in LaTeX (`docs/report.tex`) suitable for compilation on Overleaf, incorporating formal sections, code listings, figures, and bibliography.

12. **Experiment 12 (Git Version Control):** Maintain a Git repository with a `.gitignore`, meaningful commit history, and a remote-ready configuration for push to GitHub or similar hosting.

---

## Section 4: Requirements

### 4.1 Functional Requirements

| ID | Requirement |
|----|-------------|
| FR-01 | The system shall auto-generate weather readings (temperature, humidity, pressure, wind speed, wind direction) every 5 seconds using a background thread. |
| FR-02 | Readings shall be persisted in a SQLite database with referential integrity enforced via foreign keys. |
| FR-03 | The server shall expose a RESTful API with endpoints for current reading, reading history (JSON), reading history (XML), alerts, stations, station registration, and DB schema. |
| FR-04 | The dashboard shall refresh all displayed metrics automatically every 3 seconds via AJAX, with no page reload. |
| FR-05 | The dashboard shall display a multi-line Chart.js time-series graph for temperature, humidity, and pressure. |
| FR-06 | The system shall generate threshold alerts (HIGH_TEMP, LOW_TEMP, HIGH_WIND) and surface them in the dashboard's alert panel. |
| FR-07 | The station registration form shall validate all fields server-side and return field-level error messages on failure. |
| FR-08 | The Tkinter GUI shall fetch the registered station list from the server and allow manual reading submission with local validation. |
| FR-09 | The Bash script shall perform a health check after launch and display the dashboard URL on success. |
| FR-10 | The Docker container shall expose port 5000 and persist the SQLite file via a named volume. |

### 4.2 Non-Functional Requirements

| ID | Requirement |
|----|-------------|
| NFR-01 | **Performance:** API response time shall be under 200 ms for all GET endpoints under normal load. |
| NFR-02 | **Reliability:** The sensor simulation thread shall be a daemon thread; failure of one reading shall not crash the server. |
| NFR-03 | **Portability:** The application shall run on Python 3.8+ on Windows, macOS, and Linux without modification. |
| NFR-04 | **Usability:** The dashboard shall be readable on a 1024Ã—768 viewport minimum; colour contrast shall meet WCAG AA guidelines. |
| NFR-05 | **Maintainability:** All Python modules shall include docstrings; all API endpoints shall include inline comments referencing the relevant experiment. |
| NFR-06 | **Security:** The Flask secret key shall be configurable via environment variable; no credentials shall be stored in plaintext in version control. |

### 4.3 Hardware and Software Requirements

**Development Environment:**
- Operating System: Windows 11 (64-bit)
- Python: 3.11.x
- Node.js: Not required (CDN-hosted Chart.js)
- Docker Desktop: 24.x with Docker Compose v2

**Runtime Dependencies (Python):**
```
Flask==3.0.3
flask-cors==4.0.1
psutil==5.9.8
```

**Frontend Dependencies (CDN):**
- Chart.js 4.x (loaded from `cdn.jsdelivr.net`)

**Browser Compatibility:**
- Google Chrome 110+, Mozilla Firefox 110+, Microsoft Edge 110+

---

## Section 5: Technology Stack

### 5.1 Backend â€” Python 3.11 & Flask 3.0

Python 3.11 was selected as the backend language for its readability, extensive standard library (particularly `threading`, `socket`, `sqlite3`, `xml.etree.ElementTree`), and the availability of Flask. Flask 3.0 is a lightweight WSGI micro-framework that does not impose an ORM or project structure, making it ideal for a project that must demonstrate distinct technology layers separately. The `flask-cors` extension enables Cross-Origin Resource Sharing, allowing the Tkinter client and any external consumers to query the API without browser CORS errors.

### 5.2 Database â€” SQLite

SQLite was chosen for its zero-configuration, file-based nature (`weather.db`). It requires no separate server process, making the application fully self-contained. The `sqlite3` module ships with Python's standard library, eliminating an external dependency. The `conn.row_factory = sqlite3.Row` setting allows rows to be accessed as dictionaries, simplifying serialisation to JSON and XML. The `weather.db` file is excluded from Docker layers and mounted as an external volume to preserve data across container restarts.

### 5.3 Frontend â€” HTML5, Vanilla CSS (Glassmorphism), JavaScript ES2022

The frontend is built with pure HTML5 semantic markup and Vanilla CSS to avoid framework overhead. The CSS employs a **dark glassmorphism** aesthetic: semi-transparent `backdrop-filter: blur()` cards, gradient borders via `border-image`, and a deep navy/black background gradient. JavaScript ES2022 features â€” `async/await`, optional chaining (`?.`), nullish coalescing (`??`), and the `DOMParser` API â€” are used throughout `app.js`. The `fetch()` API replaces older `XMLHttpRequest` usage for clean, promise-based HTTP.

### 5.4 Chart.js

Chart.js 4.x is a Canvas-based charting library included via CDN. It renders a responsive multi-dataset line chart with smooth bezier-curve tension (`tension: 0.4`), filled areas, custom tooltip styling matching the dark theme, and minimal grid lines. The pressure dataset is linearly scaled (`(pressure - 1000) Ã— 0.5`) to bring it into the same visual range as temperature and humidity, avoiding axis compression.

### 5.5 Python Tkinter (GUI)

Tkinter, Python's built-in GUI toolkit, powers the `WeatherStationGUI` desktop application. The `ttk` themed widget set with the `clam` theme is used to allow style overrides that match the dark colour palette (`#1a1a2e` background, `#00d4ff` accent). Communication with the Flask server is performed using `urllib.request` â€” Python's standard library HTTP client â€” keeping the GUI free of external dependencies.

### 5.6 Bash Shell Scripting

`scripts/start.sh` is a POSIX-compatible Bash script that orchestrates the entire application lifecycle in nine sequential steps. It uses ANSI escape codes for coloured terminal output, `command -v` for portable binary detection, `lsof` for port conflict detection, `nohup` for background process management, and a Python-based health-check loop that polls `/api/current` until the server responds.

### 5.7 Docker & Docker Compose

The `Dockerfile` uses the official `python:3.11-slim` base image (Debian-based, ~130 MB) for a minimal footprint. Dependencies are installed before application code is copied, maximising Docker layer caching efficiency. `docker-compose.yml` defines a single service (`weather-server`) with port mapping, volume mounting, health-check configuration (30 s interval, 3 retries), and `restart: unless-stopped` for production robustness.

### 5.8 JSON and XML

JSON is the primary API response format, produced by Flask's `jsonify()` which serialises Python dicts via the `json` module. XML is generated server-side using `xml.etree.ElementTree` and pretty-printed via `xml.dom.minidom`, producing standards-compliant, human-readable output. On the client side, `DOMParser` parses raw XML text into a traversable DOM tree, from which element text content is extracted via `querySelector`.

### 5.9 Git

The repository is initialised with `git init`, tracked with a `.gitignore` that excludes `.venv/`, `__pycache__/`, `*.pyc`, `weather.db`, and IDE folders. Commits follow a conventional message structure. The project is remote-ready for push to GitHub or GitLab.

### 5.10 LaTeX

`docs/report.tex` is authored for compilation with pdfLaTeX on Overleaf. It uses `article` class with `geometry`, `listings`, `graphicx`, `hyperref`, and `xcolor` packages to produce a professionally formatted PDF with syntax-highlighted code listings and clickable cross-references.

---

## Section 6: System Architecture

### 6.1 Architectural Overview

The system follows a **three-tier architecture**:

1. **Data Tier** â€” SQLite database (`weather.db`) with three tables: `stations`, `readings`, `alerts`.
2. **Application/Logic Tier** â€” Flask server (`server/app.py`) hosting the REST API, background sensor daemon, and form processing logic.
3. **Presentation Tier** â€” Two independent clients: (a) the browser-based HTML/JS dashboard and (b) the Tkinter desktop GUI.

ðŸ“¸ [INSERT IMAGE: System Architecture Diagram â€” three-tier layered diagram showing Browser Client and Tkinter GUI at the top, Flask REST API in the middle, and SQLite DB at the bottom, with arrows labelled HTTP/AJAX, HTTP POST, SQL queries. Draw in draw.io or Lucidchart and export as PNG.]

### 6.2 Data Flow Diagram (DFD) â€” Level 0 (Context Diagram)

At Level 0, the system is represented as a single process ("Weather Station System") with four external entities:

- **Sensor Simulator** â†’ feeds readings into the system automatically.
- **Web Browser** â†’ requests dashboard and API data.
- **Tkinter GUI** â†’ submits manual readings via HTTP POST.
- **Administrator** â†’ triggers registration of new stations via the web form.

ðŸ“¸ [INSERT IMAGE: Level-0 DFD (Context Diagram) â€” single central circle labelled "Weather Station System" with four external rectangles (Sensor Simulator, Web Browser, Tkinter GUI, Administrator) and labelled data flows between them. Draw in draw.io and export as PNG.]

### 6.3 Data Flow Diagram â€” Level 1

At Level 1, the system decomposes into five sub-processes:

1. **Generate Reading** â€” reads from Sensor Simulator, writes to `readings` store.
2. **Check Thresholds** â€” reads from `readings` store, writes to `alerts` store.
3. **Serve API** â€” reads from `readings` and `alerts` stores, returns JSON/XML to Browser.
4. **Process Registration** â€” accepts Station data from Administrator, writes to `stations` store.
5. **Accept Manual Reading** â€” accepts reading from Tkinter GUI, writes to `readings` store.

ðŸ“¸ [INSERT IMAGE: Level-1 DFD â€” five labelled process bubbles with data stores (readings, alerts, stations) shown as open rectangles and external entities connected by directional arrows. Draw in draw.io and export as PNG.]

### 6.4 Entity-Relationship (ER) Diagram

Three entities are modelled:

- **Station** (`id` PK, `name` UNIQUE, `location`, `latitude`, `longitude`, `registered_at`)
- **Reading** (`id` PK, `station_id` FKâ†’Station, `temperature`, `humidity`, `pressure`, `wind_speed`, `wind_direction`, `recorded_at`, `source`)
- **Alert** (`id` PK, `station_id` FKâ†’Station, `reading_id` FKâ†’Reading, `alert_type`, `message`, `triggered_at`)

Relationships:
- Station **has many** Readings (1:N)
- Reading **may trigger** Alert (1:0..1 or 1:N based on threshold violations)
- Alert **belongs to** Station (N:1) and Reading (N:1)

ðŸ“¸ [INSERT IMAGE: ER Diagram â€” crow's foot notation showing Station, Reading, and Alert entities with their attributes and relationship cardinalities. Draw in draw.io (use ER notation template) and export as PNG.]

### 6.5 UML Diagrams

#### 6.5.1 Class Diagram

The key classes and modules in the system:

- `Flask (app)` â€” `route()`, `run()`, `jsonify()`, `render_template()`
- `database` module â€” `get_connection()`, `init_db()`, `reverse_engineer_schema()`
- `sensor_sim` module â€” `_generate_reading()`, `_check_and_insert_alerts()`, `sensor_loop()`, `start_background_sensor()`
- `network_check` module â€” `get_interfaces()`, `check_server_reachability()`, `check_internet()`, `dns_lookup()`
- `WeatherStationGUI` class â€” `__init__()`, `_setup_styles()`, `_build_header()`, `_build_form()`, `_build_status()`, `_fetch_stations()`, `_submit()`

ðŸ“¸ [INSERT IMAGE: UML Class Diagram â€” boxes for Flask app, database module, sensor_sim module, network_check module, and WeatherStationGUI class with methods listed and dependency/association arrows. Draw in draw.io or PlantUML and export as PNG.]

#### 6.5.2 Sequence Diagram â€” AJAX Poll Cycle

1. Browser `setInterval()` fires `poll()` every 3 s.
2. `poll()` calls `fetchJSON()` â†’ HTTP GET `/api/current`.
3. Flask `api_current()` calls `get_connection()` â†’ SQL SELECT on `readings JOIN stations`.
4. DB returns row â†’ `row_to_dict()` â†’ `jsonify()` â†’ HTTP 200 JSON.
5. `fetchJSON()` resolves â†’ `updateCards(data)` â†’ DOM update.
6. `updateChart(data)` â†’ Chart.js `update()` â†’ canvas redraws.
7. `fetchAlerts()` â†’ HTTP GET `/api/alerts` â†’ alerts list DOM update.

ðŸ“¸ [INSERT IMAGE: UML Sequence Diagram â€” lifelines for Browser, app.js, Flask (app.py), database.py, SQLite showing the full 3-second poll cycle with synchronous and asynchronous messages. Draw in draw.io or use PlantUML.]

#### 6.5.3 Use Case Diagram

Actors: **Browser User**, **Station Operator (Tkinter)**, **Administrator**, **Sensor Daemon**.

Use cases:
- View Live Dashboard, View JSON Raw Data, View XML Raw Data, Dismiss Alert (Browser User)
- Submit Manual Reading, Select Station (Station Operator)
- Register New Station (Administrator)
- Auto-generate Reading, Trigger Alert (Sensor Daemon)

ðŸ“¸ [INSERT IMAGE: UML Use Case Diagram â€” system boundary rectangle with four actors outside and use case ellipses inside connected by association lines. Draw in draw.io and export as PNG.]

### 6.6 Module Dependency Graph

```
app.py
  â”œâ”€â”€ database.py        (get_connection, init_db, reverse_engineer_schema)
  â”œâ”€â”€ sensor_sim.py      (start_background_sensor)
  â”‚     â””â”€â”€ database.py  (get_connection)
  â””â”€â”€ Flask / flask_cors / xml.etree / sqlite3

station_gui.py
  â””â”€â”€ urllib.request / json / tkinter

network_check.py
  â””â”€â”€ socket / psutil / subprocess

start.sh
  â””â”€â”€ python server/app.py
  â””â”€â”€ python server/network_check.py
  â””â”€â”€ python server/database.py (via -c inline)
```

ðŸ“¸ [INSERT IMAGE: Module dependency graph â€” boxes for each .py file with directed arrows showing import/call dependencies. Can be auto-generated from the graphify-out/graph.html file â€” open in browser and screenshot.]

---

## Section 7: Interface Design and Screen Overview

### 7.1 Web Dashboard (index.html)

The primary user interface is accessed at `http://localhost:5000/`. It is a single-page dashboard built with a dark glassmorphism aesthetic â€” a deep navy-to-black radial gradient background with translucent frosted-glass cards using `backdrop-filter: blur(10px)` and `rgba` backgrounds.

**Header Bar:** Displays the application title ("ðŸŒ¦ Weather Station â€” Live Monitor"), the active station name and location, the last-updated timestamp, and a pulsing green "â— LIVE" badge that dims to 30% opacity if the AJAX poll fails (indicating connectivity loss).

**Metric Cards:** Four cards arranged in a responsive CSS Grid display:
- ðŸŒ¡ Temperature (Â°C) with a cyan progress bar
- ðŸ’§ Humidity (%) with a purple progress bar
- ðŸ”µ Pressure (hPa) with a green progress bar
- ðŸ’¨ Wind Speed (km/h) with a blue progress bar

Each card shows the numeric value in a large bold font, with the progress bar proportionally filled to represent the reading relative to its operational range.

**Chart.js Time-Series Graph:** Below the metric cards, a multi-line area chart plots the last 30 readings. Three datasets are overlaid: Temperature (cyan), Humidity (purple), and Pressure scaled near zero (green). The chart features smooth bezier curves, filled semi-transparent areas, and custom-styled tooltips matching the dark theme.

**Wind Compass:** A CSS-animated compass dial with a triangular needle that rotates to the current wind direction. The cardinal direction label (N, NE, E, etc.) updates textually below the dial.

**Alert Banner:** A dismissible red/orange banner appears at the top of the viewport when temperature exceeds 42Â°C or drops below 5Â°C. The banner message includes the exact value and station name.

**Alerts History Panel:** A scrollable list of the five most recent threshold alerts retrieved from `/api/alerts`, showing alert type, message text, and timestamp.

**Raw Data Panel:** A `<pre>` element that shows the live raw JSON or XML response from the last API poll, toggled by "JSON" / "XML" buttons demonstrating Experiment 9.

**Data Source Toggle:** Two buttons labelled "JSON" and "XML" switch the AJAX data source between `/api/current` (JSON) and `/api/readings.xml?limit=1` (XML), highlighting the active format.

ðŸ“¸ [INSERT IMAGE: Screenshot of the full live dashboard at http://localhost:5000/ â€” show metric cards, Chart.js graph, compass, alerts panel, and raw data panel. Run `python server/app.py` and open browser to localhost:5000, then take a full-page screenshot (use browser DevTools â†’ Capture screenshot or the Windows Snipping Tool).]

ðŸ“¸ [INSERT IMAGE: Close-up of the Chart.js time-series graph showing multiple coloured lines with tooltip visible â€” hover over a data point to show the tooltip then screenshot.]

ðŸ“¸ [INSERT IMAGE: Dashboard with Alert Banner visible â€” wait for temperature to exceed 42Â°C (the sensor simulation will eventually trigger this) or temporarily lower the threshold in sensor_sim.py and screenshot the red alert banner at the top.]

### 7.2 Station Registration Form (register.html)

Accessed at `http://localhost:5000/register`, this form implements Experiment 7 (Flask Forms & Validation). The form fields are:

- **Station Name** (text, required, minimum 3 characters)
- **Location** (text, required)
- **Latitude** (number, -90 to 90, decimal)
- **Longitude** (number, -180 to 180, decimal)

The form uses HTML5 `required` and `pattern` attributes for client-side validation, and the Flask route performs an identical validation pass server-side. On success, a green flash message confirms registration. On failure, red inline error messages appear below each invalid field, and the form retains the user's input (sticky form).

ðŸ“¸ [INSERT IMAGE: Screenshot of the Register Station page at http://localhost:5000/register â€” show the form with glassmorphism styling. Open browser and navigate to localhost:5000/register then screenshot.]

ðŸ“¸ [INSERT IMAGE: Screenshot of the Register Station form with validation errors visible â€” submit the form with an empty Station Name and invalid Latitude (e.g., "999") to trigger server-side error messages, then screenshot.]

ðŸ“¸ [INSERT IMAGE: Screenshot of the Register Station form after successful submission â€” shows the green flash message "Station X registered successfully!" at the top.]

### 7.3 Tkinter Desktop GUI (station_gui.py)

The desktop application presents a dark-themed window (520Ã—600 px, fixed size) with:

- **Header** â€” "ðŸŒ¦ Weather Station" title in cyan, subtitle "Manual Sensor Input Console | Exp 10 â€” Python GUI"
- **Station Dropdown** â€” a read-only `ttk.Combobox` populated from `/api/stations` on startup
- **Five Input Fields** â€” Temperature (Â°C), Humidity (%), Pressure (hPa), Wind Speed (km/h), Wind Direction (8-point compass Combobox)
- **Submit Button** â€” styled dark navy button that validates inputs locally, then POSTs to `/api/submit`
- **Status Bar** â€” bottom bar showing connection status or submission result

ðŸ“¸ [INSERT IMAGE: Screenshot of the Tkinter GUI window (station_gui.py) â€” run `python gui/station_gui.py` while the Flask server is running, then screenshot the open window showing all form fields, the station dropdown, and the status bar at the bottom.]

ðŸ“¸ [INSERT IMAGE: Screenshot of the Tkinter GUI showing a validation error messagebox â€” enter an invalid temperature (e.g., "999") and click Submit to trigger the local validation error dialog.]

## Section 8: Code Snippets

### 8.1 database.py â€” Forward & Reverse Engineering (Experiment 3)

```python
"""
database.py â€” Forward Engineering from ER Diagram
ER Entities: Station, Reading, Alert
"""
import sqlite3, os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'weather.db')

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Forward Engineering: Creates tables from ER model."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stations (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            name          TEXT NOT NULL UNIQUE,
            location      TEXT NOT NULL,
            latitude      REAL,
            longitude     REAL,
            registered_at TEXT DEFAULT (datetime('now'))
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS readings (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            station_id     INTEGER NOT NULL,
            temperature    REAL NOT NULL,
            humidity       REAL NOT NULL,
            pressure       REAL NOT NULL,
            wind_speed     REAL NOT NULL,
            wind_direction TEXT DEFAULT 'N',
            recorded_at    TEXT DEFAULT (datetime('now')),
            source         TEXT DEFAULT 'auto',
            FOREIGN KEY (station_id) REFERENCES stations(id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alerts (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            station_id   INTEGER NOT NULL,
            reading_id   INTEGER NOT NULL,
            alert_type   TEXT NOT NULL,
            message      TEXT NOT NULL,
            triggered_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (station_id) REFERENCES stations(id),
            FOREIGN KEY (reading_id) REFERENCES readings(id)
        )
    ''')
    cursor.execute('''
        INSERT OR IGNORE INTO stations (name, location, latitude, longitude)
        VALUES ('Station Alpha', 'Main Campus', 12.9716, 77.5946)
    ''')
    conn.commit(); conn.close()
    print("[DB] Database initialized (Forward Engineering complete)")

def reverse_engineer_schema():
    """Reverse Engineering: Extract schema from existing DB."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row['name'] for row in cursor.fetchall()]
    schema = {}
    for table in tables:
        cursor.execute(f"PRAGMA table_info({table})")
        schema[table] = [
            {'name': c['name'], 'type': c['type'],
             'not_null': bool(c['notnull']), 'primary_key': bool(c['pk'])}
            for c in cursor.fetchall()
        ]
    conn.close()
    return schema
```

**Explanation:** `init_db()` implements forward engineering â€” the Python code IS the migration script, translating ER entities directly into `CREATE TABLE` DDL statements. `reverse_engineer_schema()` implements reverse engineering by querying SQLite's internal `sqlite_master` catalogue and `PRAGMA table_info`, producing a dictionary that mirrors the live database structure. This schema is exposed via the `/api/schema` endpoint for programmatic introspection.

---

### 8.2 sensor_sim.py â€” Simulated Sensor with Alert Generation

```python
"""
sensor_sim.py â€” Simulated Weather Sensor (background daemon thread)
"""
import threading, random, time, math
from database import get_connection

THRESHOLDS = {
    'temperature': {'min': 5.0,  'max': 42.0},
    'humidity':    {'min': 10.0, 'max': 95.0},
    'wind_speed':  {'max': 80.0},
}
WIND_DIRS = ['N','NE','E','SE','S','SW','W','NW']

_state = {'temperature': 28.0, 'humidity': 60.0,
          'pressure': 1013.25, 'wind_speed': 12.0,
          'wind_dir_idx': 0, 'tick': 0}

def _next_value(current, delta_range, min_val, max_val):
    """Smooth random walk â€” feels like real sensor data."""
    delta = random.uniform(-delta_range, delta_range)
    return round(max(min_val, min(max_val, current + delta)), 2)

def _generate_reading():
    _state['tick'] += 1
    sine_offset = 3.0 * math.sin(_state['tick'] * 0.05)
    _state['temperature'] = _next_value(
        _state['temperature'] + sine_offset * 0.05, 0.8, -10.0, 50.0)
    _state['humidity']    = _next_value(_state['humidity'],   1.5, 0.0,  100.0)
    _state['pressure']    = _next_value(_state['pressure'],   0.5, 950.0,1050.0)
    _state['wind_speed']  = _next_value(_state['wind_speed'], 2.0, 0.0,  120.0)
    _state['wind_dir_idx'] = (
        _state['wind_dir_idx'] + random.choice([-1,0,0,1])) % len(WIND_DIRS)
    return {
        'temperature':    _state['temperature'],
        'humidity':       _state['humidity'],
        'pressure':       _state['pressure'],
        'wind_speed':     _state['wind_speed'],
        'wind_direction': WIND_DIRS[_state['wind_dir_idx']],
        'source': 'auto'
    }

def sensor_loop(interval=5):
    print(f"[Sensor] Starting auto-simulation (interval={interval}s)")
    while True:
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM stations LIMIT 1")
            row = cursor.fetchone()
            if row:
                station_id = row['id']
                reading = _generate_reading()
                cursor.execute('''
                    INSERT INTO readings
                        (station_id,temperature,humidity,pressure,
                         wind_speed,wind_direction,source)
                    VALUES (?,?,?,?,?,?,?)
                ''', (station_id, reading['temperature'], reading['humidity'],
                      reading['pressure'], reading['wind_speed'],
                      reading['wind_direction'], reading['source']))
                conn.commit()
                reading_id = cursor.lastrowid
                # Alert check
                if reading['temperature'] > THRESHOLDS['temperature']['max']:
                    cursor.execute(
                        "INSERT INTO alerts (station_id,reading_id,alert_type,message)"
                        " VALUES (?,?,?,?)",
                        (station_id, reading_id, 'HIGH_TEMP',
                         f"Temperature {reading['temperature']}Â°C exceeds max!"))
                    conn.commit()
            conn.close()
        except Exception as e:
            print(f"[Sensor] Error: {e}")
        time.sleep(interval)

def start_background_sensor(interval=5):
    t = threading.Thread(target=sensor_loop, args=(interval,), daemon=True)
    t.start()
    return t
```

**Explanation:** The smooth random-walk algorithm (`_next_value`) prevents unnatural step-changes in readings. The sinusoidal `sine_offset` applied to temperature simulates the real-world day/night thermal cycle. The daemon thread (`daemon=True`) ensures the thread is automatically killed when the main Flask process exits, preventing zombie processes. Alert generation is tightly coupled to the reading insertion loop â€” immediately after committing a reading, threshold checks are performed and alerts are inserted in the same database connection.

---

### 8.3 app.py â€” Flask API Endpoints (Experiments 7, 8, 9)

```python
from flask import Flask, jsonify, request, render_template, redirect, url_for, flash
from flask_cors import CORS
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom
from datetime import datetime
from database import init_db, get_connection, reverse_engineer_schema
from sensor_sim import start_background_sensor

app = Flask(__name__,
    template_folder='../templates', static_folder='../static')
app.secret_key = 'weather-station-secret-2024'
CORS(app)

def row_to_dict(row):
    return dict(row) if row else {}

def readings_to_xml(readings):
    """Convert readings list to pretty-printed XML (Exp 9)."""
    root = Element('WeatherData')
    root.set('generated_at', datetime.utcnow().isoformat() + 'Z')
    for r in readings:
        entry = SubElement(root, 'Reading')
        for key, val in r.items():
            child = SubElement(entry, key)
            child.text = str(val) if val is not None else ''
    raw = tostring(root, encoding='unicode')
    return minidom.parseString(raw).toprettyxml(indent='  ')

@app.route('/api/current')
def api_current():
    """Latest single reading â€” polled every 3s via AJAX (Exp 9)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT r.*, s.name AS station_name, s.location
        FROM readings r
        JOIN stations s ON r.station_id = s.id
        ORDER BY r.id DESC LIMIT 1
    ''')
    row = cursor.fetchone(); conn.close()
    return jsonify(row_to_dict(row) if row else {})

@app.route('/api/readings.xml')
def api_readings_xml():
    """Last N readings as XML (Exp 9 â€” XML support)."""
    limit = request.args.get('limit', 20, type=int)
    conn = get_connection(); cursor = conn.cursor()
    cursor.execute('''
        SELECT r.*, s.name AS station_name FROM readings r
        JOIN stations s ON r.station_id = s.id
        ORDER BY r.id DESC LIMIT ?
    ''', (limit,))
    rows = [row_to_dict(r) for r in cursor.fetchall()]; conn.close()
    return app.response_class(readings_to_xml(rows[::-1]), mimetype='application/xml')

@app.route('/register', methods=['GET','POST'])
def register_station():
    """Station registration form with server-side validation (Exp 7)."""
    errors = {}; form_data = {}
    if request.method == 'POST':
        name     = request.form.get('name','').strip()
        location = request.form.get('location','').strip()
        lat_str  = request.form.get('latitude','').strip()
        lon_str  = request.form.get('longitude','').strip()
        form_data = {'name':name,'location':location,
                     'latitude':lat_str,'longitude':lon_str}
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
            conn = get_connection(); cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO stations (name,location,latitude,longitude) VALUES (?,?,?,?)",
                (name, location, lat, lon))
            conn.commit(); conn.close()
            flash(f'Station "{name}" registered successfully!', 'success')
            return redirect(url_for('register_station'))
    return render_template('register.html', errors=errors, form_data=form_data)

@app.route('/api/schema')
def api_schema():
    """Reverse Engineering: return DB schema as JSON (Exp 3)."""
    return jsonify({'schema': reverse_engineer_schema()})

if __name__ == '__main__':
    init_db()
    start_background_sensor(interval=5)
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
```

---

### 8.4 app.js â€” AJAX Poll Loop with JSON/XML Toggle (Experiments 6 & 9)

```javascript
'use strict';
const POLL_INTERVAL_MS = 3000;
const HISTORY_LIMIT    = 30;
let dataSource = 'json';
let chartInstance = null;
let chartLabels=[], chartTemp=[], chartHum=[], chartPres=[];
const WIND_DEGREES = {N:0,NE:45,E:90,SE:135,S:180,SW:225,W:270,NW:315};

function el(id) { return document.getElementById(id); }

function updateCards(d) {
  if (!d || !d.temperature) return;
  el('val-temp').textContent = parseFloat(d.temperature).toFixed(1);
  el('val-hum').textContent  = parseFloat(d.humidity).toFixed(1);
  el('val-pres').textContent = parseFloat(d.pressure).toFixed(1);
  el('val-wind').textContent = parseFloat(d.wind_speed).toFixed(1);
  el('bar-temp').style.width = Math.max(0,Math.min(100,
      ((d.temperature+10)/60)*100)) + '%';
  const dir = (d.wind_direction||'N').trim().toUpperCase();
  el('compass-needle').style.transform =
      `translate(-50%,-100%) rotate(${WIND_DEGREES[dir]??0}deg)`;
  el('compass-dir').textContent = dir;
  if (d.temperature > 42) {
    el('alert-text').textContent =
        `âš  High Temperature: ${parseFloat(d.temperature).toFixed(1)}Â°C`;
    el('alert-banner').classList.remove('hidden');
  }
}

async function fetchXML() {
  const resp = await fetch('/api/readings.xml?limit=1');
  const text = await resp.text();
  el('raw-data').textContent = text.slice(0, 800);
  const xmlDoc  = new DOMParser().parseFromString(text,'application/xml');
  const reading = xmlDoc.querySelector('Reading');
  if (!reading) return null;
  const get = tag => reading.querySelector(tag)?.textContent ?? null;
  return {
    temperature: get('temperature'), humidity: get('humidity'),
    pressure: get('pressure'),       wind_speed: get('wind_speed'),
    wind_direction: get('wind_direction'), recorded_at: get('recorded_at'),
    station_name: get('station_name'),
  };
}

async function poll() {
  try {
    const data = dataSource==='xml' ? await fetchXML()
               : await (fetch('/api/current').then(r=>r.json()));
    if (data) { updateCards(data); updateChart(data); }
    await fetchAlerts();
    el('live-badge').style.opacity = '1';
  } catch(err) {
    console.warn('[AJAX] Poll error:', err.message);
    el('live-badge').style.opacity = '0.3';
  }
}

document.addEventListener('DOMContentLoaded', () => {
  initChart();
  poll();
  setInterval(poll, POLL_INTERVAL_MS);
});
```

---

### 8.5 network_check.py â€” Network Interface Inspector (Experiment 5)

```python
"""
network_check.py â€” Experiment 5: Python Network Interface Checker
"""
import socket, subprocess, platform, psutil

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 5000

def get_interfaces():
    hostname   = socket.gethostname()
    primary_ip = socket.gethostbyname(hostname)
    print(f" Hostname  : {hostname}\n Primary IP: {primary_ip}")
    ifaces = psutil.net_if_addrs()
    stats  = psutil.net_if_stats()
    for iface, addrs in ifaces.items():
        is_up = stats[iface].isup if iface in stats else False
        for addr in addrs:
            if addr.family == socket.AF_INET:
                print(f"  [{'UP  ' if is_up else 'DOWN'}] {iface:<20} {addr.address}")

def check_server_reachability(host=SERVER_HOST, port=SERVER_PORT, timeout=3):
    try:
        sock = socket.create_connection((host, port), timeout=timeout)
        sock.close()
        print(f"  Status : âœ“ REACHABLE â€” Server is running!")
        return True
    except ConnectionRefusedError:
        print(f"  Status : âœ— REFUSED â€” Server not running on port {port}")
    return False

def check_internet(host='8.8.8.8', port=53, timeout=3):
    try:
        socket.create_connection((host, port), timeout=timeout).close()
        print("  Status : âœ“ Internet is REACHABLE")
        return True
    except Exception:
        print("  Status : âœ— No internet connection")
    return False

if __name__ == '__main__':
    get_interfaces()
    check_internet()
    check_server_reachability()
```

---

### 8.6 scripts/start.sh â€” Bash Automation (Experiment 4)

```bash
#!/usr/bin/env bash
# start.sh â€” Experiment 4: Linux Shell Script
set -e
CYAN="\033[1;36m"; GREEN="\033[1;32m"; RESET="\033[0m"
PORT=5000; LOG_FILE="server.log"; VENV_DIR=".venv"

log()  { echo -e "${GREEN}[âœ“]${RESET} $1"; }
info() { echo -e "${CYAN}[â†’]${RESET} $1"; }

check_python() {
  command -v python3 &>/dev/null && { PYTHON=python3; log "Python3 found"; } \
  || { echo "Python not found"; exit 1; }
}

setup_venv() {
  [ ! -d "$VENV_DIR" ] && $PYTHON -m venv $VENV_DIR
  source "$VENV_DIR/bin/activate" 2>/dev/null || true
  log "Virtual environment ready."
}

install_deps() {
  pip install -q -r requirements.txt
  log "Dependencies installed."
}

start_server() {
  nohup $PYTHON server/app.py > "$LOG_FILE" 2>&1 &
  echo $! > server.pid
  log "Server started (PID: $!)"
}

health_check() {
  for i in {1..10}; do
    sleep 1
    $PYTHON -c "import urllib.request; urllib.request.urlopen(
        'http://localhost:$PORT/api/current',timeout=2); print('ok')" \
        2>/dev/null | grep -q ok && {
      log "Server healthy â†’ http://localhost:$PORT"; return; }
    echo -n "."
  done
}

check_python; setup_venv; install_deps
$PYTHON server/network_check.py 2>/dev/null || true
$PYTHON -c "import sys; sys.path.insert(0,'server'); \
from database import init_db; init_db()"
start_server; health_check
tail -f "$LOG_FILE"
```

---

### 8.7 Dockerfile & docker-compose.yml (Experiment 8)

```dockerfile
# Dockerfile â€” Experiment 8: Docker Deployment
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY server/    ./server/
COPY templates/ ./templates/
COPY static/    ./static/
EXPOSE 5000
ENV FLASK_ENV=production PYTHONUNBUFFERED=1
CMD ["python", "server/app.py"]
```

```yaml
# docker-compose.yml â€” Experiment 8
version: '3.9'
services:
  weather-server:
    build: .
    container_name: weather_station_app
    ports:
      - "5000:5000"
    volumes:
      - ./data:/app/data
    environment:
      - FLASK_ENV=production
      - PYTHONUNBUFFERED=1
    restart: unless-stopped
    healthcheck:
      test: ["CMD","python","-c",
             "import urllib.request; urllib.request.urlopen(
             'http://localhost:5000/api/current')"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s
```

---

### 8.8 station_gui.py â€” Tkinter GUI (Experiment 10)

```python
"""
station_gui.py â€” Experiment 10: Python GUI using Tkinter
"""
import tkinter as tk
from tkinter import ttk, messagebox
import urllib.request, urllib.error, json

SERVER_URL = 'http://127.0.0.1:5000'

class WeatherStationGUI:
    def __init__(self, root):
        self.root = root
        root.title("Weather Station â€” Manual Input Console")
        root.geometry("520x600"); root.configure(bg='#1a1a2e')
        self._setup_styles(); self._build_header()
        self._build_form(); self._build_status()
        self._fetch_stations()

    def _fetch_stations(self):
        """Fetch station list from server to populate dropdown."""
        try:
            req  = urllib.request.urlopen(f'{SERVER_URL}/api/stations', timeout=3)
            data = json.loads(req.read())
            stations = data.get('stations', [])
            labels = [f"{s['id']} â€” {s['name']} ({s['location']})" for s in stations]
            self.station_combo['values'] = labels
            self._station_ids = {lbl: s['id'] for lbl,s in zip(labels, stations)}
            if labels: self.station_combo.current(0)
        except Exception:
            self.station_combo['values'] = ['1 â€” Station Alpha (Main Campus)']
            self._station_ids = {'1 â€” Station Alpha (Main Campus)': 1}
            self.station_combo.current(0)

    def _submit(self):
        """Validate and POST reading to Flask API."""
        errors = []
        def parse(var, label, lo, hi):
            try:
                v = float(var.get())
                if not lo <= v <= hi:
                    errors.append(f"{label}: must be {lo}â€“{hi}")
                return v
            except ValueError:
                errors.append(f"{label}: enter a valid number")
        temp = parse(self.temp_var, 'Temperature', -50, 60)
        hum  = parse(self.hum_var,  'Humidity',    0,  100)
        pres = parse(self.pres_var, 'Pressure',    870, 1085)
        wind = parse(self.wind_var, 'Wind Speed',  0,  200)
        if errors:
            messagebox.showerror("Validation Error", "\n".join(errors)); return
        payload = json.dumps({
            'station_id': self._get_station_id(),
            'temperature': temp, 'humidity': hum,
            'pressure': pres, 'wind_speed': wind,
            'wind_direction': self.wind_dir_var.get()
        }).encode('utf-8')
        try:
            req  = urllib.request.Request(f'{SERVER_URL}/api/submit',
                data=payload, headers={'Content-Type':'application/json'}, method='POST')
            resp = urllib.request.urlopen(req, timeout=5)
            result = json.loads(resp.read())
            if result.get('success'):
                messagebox.showinfo("Success", "Reading submitted to server!")
        except urllib.error.HTTPError as e:
            body = json.loads(e.read())
            messagebox.showerror("Validation Error", str(body.get('errors', e)))
        except Exception as e:
            messagebox.showerror("Connection Error", f"Cannot reach server.\n{e}")

if __name__ == '__main__':
    root = tk.Tk()
    WeatherStationGUI(root)
    root.mainloop()
```

## Section 9: Implementation

### 9.1 Experiment 1 â€” DFD and ER Diagram

The system design began with producing a Level-0 and Level-1 Data Flow Diagram to map all data sources, sinks, processes, and stores. The ER diagram identified three entities â€” Station, Reading, Alert â€” with two one-to-many relationships. This diagram directly drove the schema in `database.py`, making the ER-to-DDL mapping explicit and traceable.

ðŸ“¸ [INSERT IMAGE: The final ER Diagram â€” draw in draw.io using crow's foot notation with Station, Reading, and Alert entities showing all attributes and cardinality labels. Export as PNG and insert here.]

### 9.2 Experiment 2 â€” UML Diagrams

Three UML artefacts were produced:

1. **Class Diagram** â€” Captures the Flask application's modules as classes, with methods listed and dependency/call arrows between them, including the `WeatherStationGUI` class in `station_gui.py`.
2. **Sequence Diagram** â€” Traces the complete AJAX poll cycle from browser timer fire to DOM update, through Flask, database, and back.
3. **Use Case Diagram** â€” Maps actor-system interactions for all four actors: Browser User, Station Operator, Administrator, and Sensor Daemon.

ðŸ“¸ [INSERT IMAGE: UML Class Diagram drawn in draw.io or PlantUML showing all classes/modules with attributes and methods.]

ðŸ“¸ [INSERT IMAGE: UML Sequence Diagram showing the AJAX poll cycle through app.js â†’ Flask â†’ SQLite â†’ DOM.]

ðŸ“¸ [INSERT IMAGE: UML Use Case Diagram with system boundary and four actors.]

### 9.3 Experiment 3 â€” Forward and Reverse Engineering

**Forward Engineering** is implemented in `database.py:init_db()`. The function translates the three ER entities directly into SQLite `CREATE TABLE` DDL statements with appropriate data types, `NOT NULL` constraints, `UNIQUE` constraints, and foreign key references. On first launch, the database schema is generated programmatically from this code.

**Reverse Engineering** is implemented in `database.py:reverse_engineer_schema()`. It queries `sqlite_master` to enumerate all tables, then calls `PRAGMA table_info(table_name)` for each, extracting column names, types, nullability, default values, and primary key flags. The result is returned as a nested Python dict serialised to JSON at the `/api/schema` endpoint.

ðŸ“¸ [INSERT IMAGE: Browser screenshot of http://localhost:5000/api/schema showing the JSON response with the stations, readings, and alerts table schemas. Run the server and navigate to this URL in browser, then screenshot.]

### 9.4 Experiment 4 â€” Shell Script

`scripts/start.sh` is structured as a sequential pipeline of nine named functions: `check_python`, `setup_venv`, `install_deps`, `network_check`, `init_database`, `check_port`, `start_server`, `health_check`, `tail_logs`. Each step is preceded by a coloured `info` message and concludes with a `log` (green tick) on success, or a `warn`/`err` on failure.

Key implementation choices:
- `set -e` ensures the script aborts immediately on any unhandled error.
- `nohup ... &` runs Flask in the background, detached from the terminal session.
- The health-check loop uses an inline Python one-liner to HTTP-GET `/api/current` and prints `ok` on success, which `grep -q ok` detects.
- Port conflict resolution uses `lsof -Pi :5000` to find and `kill -9` any existing process holding port 5000.

ðŸ“¸ [INSERT IMAGE: Terminal screenshot of `bash scripts/start.sh` running â€” shows the coloured banner, each step's tick marks, the health check dots, and the final "Dashboard â†’ http://localhost:5000" URL. Run in WSL or Git Bash terminal and screenshot.]

### 9.5 Experiment 5 â€” Network Interface Check

`server/network_check.py` performs three diagnostic tasks using only Python's standard library (with an optional `psutil` enhancement):

1. **Interface Enumeration:** Uses `psutil.net_if_addrs()` and `psutil.net_if_stats()` to list all IPv4 interfaces with UP/DOWN status. Falls back to `ipconfig`/`ip addr` subprocess call if psutil is unavailable.
2. **Internet Connectivity:** Attempts a TCP connection to Google's public DNS at `8.8.8.8:53` with a 3-second timeout.
3. **Server Reachability:** Attempts a TCP connection to `127.0.0.1:5000`. This directly tests whether the Flask server is accepting connections.

ðŸ“¸ [INSERT IMAGE: Terminal screenshot of `python server/network_check.py` output â€” shows hostname, primary IP, interface list with UP/DOWN status, internet check result, and server reachability result. Run in PowerShell or terminal while Flask server is running.]

### 9.6 Experiment 6 â€” JavaScript Dynamic Pages

The dashboard's `app.js` file drives all DOM manipulation. On `DOMContentLoaded`, `initChart()` creates the Chart.js canvas, `poll()` fires immediately for an instant first load, and `setInterval(poll, 3000)` establishes the recurring refresh cycle.

The `updateCards(data)` function updates eight DOM elements per poll cycle: four value spans and four progress bar widths. The compass needle is rotated using `element.style.transform = \`rotate(${deg}deg)\`` where degrees are looked up from a constant map (`WIND_DEGREES`). The live badge opacity is set to `1` on success and `0.3` on fetch failure â€” a subtle but clear indicator of connectivity status.

ðŸ“¸ [INSERT IMAGE: Browser DevTools Network tab screenshot showing the repeated XHR/Fetch requests to /api/current every 3 seconds â€” open DevTools (F12) â†’ Network tab â†’ filter by "current" â†’ wait 10 seconds to see multiple requests appear.]

### 9.7 Experiment 7 â€” Flask Forms and Validation

The `/register` route handles both `GET` (render empty form) and `POST` (validate and insert) in a single view function. Validation is dual-layer:

- **Client-side:** HTML5 `required`, `type="number"`, `min`/`max`, and `minlength` attributes provide instant browser-native validation before form submission.
- **Server-side:** Flask checks each field independently, collecting errors into a dict. The template renders error messages next to each field using Jinja2 conditionals (`{% if errors.name %}`). The `form_data` dict is passed back to the template to repopulate fields (sticky form pattern), preventing data loss on validation failure.

On successful INSERT, Flask's `flash()` system stores a one-time success message in the session, displayed on the next page render via Jinja2.

ðŸ“¸ [INSERT IMAGE: Register page with a successful flash message â€” after submitting a valid station name, the green success banner appears at the top of the form. Screenshot from localhost:5000/register.]

### 9.8 Experiment 8 â€” Docker Deployment

The `Dockerfile` uses a two-phase copy strategy to maximise layer cache efficiency: `requirements.txt` is copied and `pip install` runs first; only then is application source code copied. This means that if only source code changes, Docker can reuse the cached pip layer, dramatically speeding up subsequent builds.

`docker-compose.yml` adds operational concerns: the `volumes` stanza mounts `./data` on the host to `/app/data` in the container, ensuring `weather.db` persists across `docker-compose down` / `up` cycles. The `healthcheck` polls `/api/current` every 30 seconds; after 3 failures, Docker marks the container as unhealthy and the `restart: unless-stopped` policy triggers a restart.

ðŸ“¸ [INSERT IMAGE: Terminal screenshot of `docker-compose up --build` â€” shows Docker pulling python:3.11-slim, running pip install, copying files, and starting the container. Run `docker-compose up --build` in PowerShell from the project root and screenshot the terminal output.]

ðŸ“¸ [INSERT IMAGE: `docker ps` output showing the `weather_station_app` container as healthy with port 5000 mapped. Run `docker ps` in PowerShell after `docker-compose up`.]

### 9.9 Experiment 9 â€” AJAX with JSON and XML

Two parallel code paths handle data retrieval:

**JSON path:** `fetchJSON()` calls `fetch('/api/current')` and resolves to a plain JavaScript object via `.json()`. The Flask endpoint uses `jsonify()` to serialise a `sqlite3.Row` dict.

**XML path:** `fetchXML()` calls `fetch('/api/readings.xml?limit=1')` and resolves to raw text via `.text()`. A `DOMParser` instance parses the XML string into a live DOM tree. Individual field values are extracted via `xmlDoc.querySelector('Reading').querySelector('fieldname').textContent`. The same `updateCards()` and `updateChart()` functions consume both outputs identically, since both return plain JavaScript objects.

The toggle between formats is achieved by setting `dataSource = 'json'` or `'xml'` when the user clicks the format buttons. The `poll()` function reads `dataSource` at each interval.

ðŸ“¸ [INSERT IMAGE: Dashboard with "XML" button active â€” click the XML toggle button on the dashboard and screenshot showing the raw XML data in the Raw Data panel and the XML label active.]

ðŸ“¸ [INSERT IMAGE: Browser screenshot of http://localhost:5000/api/readings.xml showing pretty-printed XML with WeatherData root element and multiple Reading child elements.]

### 9.10 Experiment 10 â€” Python GUI (Tkinter)

`WeatherStationGUI` initialises by calling `_fetch_stations()` which issues a `urllib.request.urlopen` GET to `/api/stations`. If the server is unreachable, the combo box is pre-populated with a default "Station Alpha" entry and a warning is shown in the status bar â€” ensuring the GUI is usable even when offline.

The `_submit()` method performs local validation using a nested `parse()` helper function that checks both type (float conversion) and range. If any field fails, a `messagebox.showerror` dialog lists all errors. On validation success, the JSON payload is encoded to bytes and POSTed via `urllib.request.Request` with `Content-Type: application/json`. The server's response is parsed and a success/failure dialog shown accordingly.

ðŸ“¸ [INSERT IMAGE: Tkinter GUI window after successful submission â€” shows "âœ“ Reading submitted successfully!" in the cyan status bar at the bottom. Screenshot after clicking Submit with valid values while server is running.]

### 9.11 Experiment 11 â€” LaTeX Documentation

`docs/report.tex` is structured as a formal academic document using the `article` document class with `a4paper` geometry. Key LaTeX packages used:

- `listings` â€” for syntax-highlighted Python and Bash code blocks
- `graphicx` â€” for inserting ER diagram, UML diagrams, and screenshots as figures
- `hyperref` â€” for clickable cross-references and a PDF table of contents
- `xcolor` â€” for custom colours in code listings
- `geometry` â€” for margin control

The document is compiled on Overleaf using pdfLaTeX. Figures are wrapped in the `figure` environment with `\caption{}` and `\label{}` for automatic numbering and `\ref{}` cross-referencing.

ðŸ“¸ [INSERT IMAGE: Overleaf editor screenshot showing the report.tex file open with the compiled PDF preview on the right â€” paste docs/report.tex into a new Overleaf project, upload diagram images, and screenshot the editor + PDF preview side by side.]

### 9.12 Experiment 12 â€” Git Version Control

The repository was initialised with `git init` in the project root. The `.gitignore` excludes:

```
.venv/
__pycache__/
*.pyc
weather.db
*.log
*.pid
.idea/
.vscode/
```

A typical commit workflow:
```bash
git add .
git commit -m "feat: add XML API endpoint and client-side toggle"
git push origin main
```

ðŸ“¸ [INSERT IMAGE: `git log --oneline` output in terminal â€” shows the commit history with descriptive commit messages. Run `git log --oneline -15` in PowerShell from the project root and screenshot.]

ðŸ“¸ [INSERT IMAGE: `git status` output showing a clean working tree â€” run `git status` in PowerShell and screenshot.]

---

## Section 10: Application Output

### 10.1 Server Startup Output

When `python server/app.py` is executed:

```
[DB] Database initialized (Forward Engineering complete)
[Sensor] Starting auto-simulation (interval=5s)
[Server] Starting Flask on http://0.0.0.0:5000
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://192.168.x.x:5000
```

ðŸ“¸ [INSERT IMAGE: PowerShell terminal screenshot showing Flask server startup output â€” run `python server/app.py` and screenshot the terminal immediately after startup.]

### 10.2 Live Dashboard Output

The browser dashboard at `http://localhost:5000` shows:
- Metric cards auto-updating every 3 seconds
- Chart.js graph growing with each new reading
- Station name "Station Alpha" and location "Main Campus"
- LIVE badge pulsing green

ðŸ“¸ [INSERT IMAGE: Full-page screenshot of the live dashboard at localhost:5000 showing all four metric cards with real values, the Chart.js time-series graph with 10+ data points, and the wind compass. Use browser's full-page screenshot tool or Windows Snipping Tool.]

### 10.3 JSON API Response

`GET http://localhost:5000/api/current` returns:

```json
{
  "humidity": 63.47,
  "id": 142,
  "location": "Main Campus",
  "pressure": 1014.32,
  "recorded_at": "2026-04-28 12:34:05",
  "source": "auto",
  "station_id": 1,
  "station_name": "Station Alpha",
  "temperature": 29.81,
  "wind_direction": "NE",
  "wind_speed": 14.52
}
```

ðŸ“¸ [INSERT IMAGE: Browser screenshot of http://localhost:5000/api/current showing the raw JSON response. Navigate to this URL and screenshot (use JSONView browser extension for prettier formatting).]

### 10.4 XML API Response

`GET http://localhost:5000/api/readings.xml?limit=2` returns:

```xml
<?xml version="1.0" ?>
<WeatherData generated_at="2026-04-28T12:34:10Z">
  <Reading>
    <id>141</id>
    <station_id>1</station_id>
    <temperature>29.21</temperature>
    <humidity>62.84</humidity>
    <pressure>1013.97</pressure>
    <wind_speed>13.80</wind_speed>
    <wind_direction>N</wind_direction>
    <recorded_at>2026-04-28 12:34:00</recorded_at>
    <source>auto</source>
    <station_name>Station Alpha</station_name>
  </Reading>
  <Reading>
    <id>142</id>
    ...
  </Reading>
</WeatherData>
```

ðŸ“¸ [INSERT IMAGE: Browser screenshot of http://localhost:5000/api/readings.xml?limit=2 showing pretty-printed XML output. Navigate in browser and screenshot.]

### 10.5 Tkinter GUI Submission Output

After filling values and clicking "Submit Reading":
- Status bar: `âœ“ Reading submitted successfully!`
- Info dialog: "Reading submitted to server!"
- Dashboard immediately reflects the new reading on next poll.

ðŸ“¸ [INSERT IMAGE: Tkinter GUI window after a successful manual submission â€” status bar shows green tick message and the success dialog is visible. Screenshot from station_gui.py running alongside the server.]

### 10.6 Network Check Output

```
=======================================================
  NETWORK INTERFACE CHECKER â€” Weather Station
=======================================================

 Hostname     : DESKTOP-ABC123
 Primary IP   : 192.168.1.105

 Active Network Interfaces:
----------------------------------------
  [UP  ] Wi-Fi                 192.168.1.105
  [UP  ] Loopback Pseudo-Interface 127.0.0.1

 Internet Connectivity Check
----------------------------------------
  Target : Google DNS (8.8.8.8:53)
  Status : âœ“ Internet is REACHABLE

 Server Reachability Check
----------------------------------------
  Target : 127.0.0.1:5000
  Status : âœ“ REACHABLE â€” Server is running!
=======================================================
```

ðŸ“¸ [INSERT IMAGE: Terminal screenshot of `python server/network_check.py` showing the full formatted output with all checks passing. Run in PowerShell with server active.]

### 10.7 Alerts Panel Output

When temperature exceeds 42Â°C, the alert system triggers:
- Alert banner visible at top of dashboard
- Alerts panel shows: `HIGH_TEMP â€” Temperature 42.31Â°C exceeds max threshold!`

ðŸ“¸ [INSERT IMAGE: Dashboard screenshot showing the red alert banner at the top and the alerts history panel populated with HIGH_TEMP entries. Can trigger by temporarily lowering THRESHOLDS['temperature']['max'] to 30.0 in sensor_sim.py.]

### 10.8 Schema Endpoint Output

`GET http://localhost:5000/api/schema` returns a JSON representation of all tables:

ðŸ“¸ [INSERT IMAGE: Browser screenshot of http://localhost:5000/api/schema showing the JSON schema response with all three tables (stations, readings, alerts) and their column definitions.]

---

## Section 11: Conclusion and Future Enhancements

### 11.1 Conclusion

The Real-Time Weather Station Dashboard successfully demonstrates the practical application of all twelve experiments prescribed in the Software Tools laboratory curriculum within a single, integrated project. Each tool or technology â€” from the conceptual ER/DFD diagrams of Experiment 1 through to the Git version control workflow of Experiment 12 â€” is not merely present as a token inclusion but is functionally integral to the system's operation.

The project illustrates several important software engineering principles:
- **Separation of Concerns:** The database layer, API layer, simulation layer, and presentation layer are cleanly separated into distinct modules.
- **Dual-format data interchange:** Supporting both JSON and XML demonstrates format-agnostic API design.
- **Automation over manual steps:** The Bash script reduces a complex multi-step launch procedure to a single command.
- **Containerisation for reproducibility:** Docker ensures the application runs identically on any machine regardless of local Python configuration.
- **Progressive enhancement:** The dashboard degrades gracefully when the server is unreachable (live badge dims, errors silently swallowed in `poll()`).

The system generates realistic, continuously evolving weather data and surfaces meaningful threshold-based alerts, making it a self-contained demonstration platform that requires no physical hardware.

### 11.2 Future Enhancements

| Enhancement | Description |
|-------------|-------------|
| **Real Sensor Integration** | Replace `sensor_sim.py` with an adapter for real hardware sensors (e.g., Raspberry Pi with DHT22 or BMP280) via serial/IÂ²C. |
| **Multiple Station Support** | Extend the dashboard to show a station selector and render per-station charts, leveraging the existing multi-station schema. |
| **WebSocket Push** | Replace 3-second AJAX polling with Flask-SocketIO WebSocket push for true real-time updates with sub-second latency and reduced HTTP overhead. |
| **User Authentication** | Add JWT-based authentication for the `/api/submit` and `/register` endpoints to prevent unauthorised data injection. |
| **Historical Analytics** | Add a date-range picker and server-side aggregation (hourly/daily min/max/avg) exposed via a new `/api/stats` endpoint. |
| **Map View** | Integrate Leaflet.js to display registered stations at their GPS coordinates on an interactive map, using the `latitude` and `longitude` columns already in the `stations` table. |
| **Mobile PWA** | Convert the dashboard into a Progressive Web App (PWA) with a `manifest.json` and Service Worker for offline caching of the last known reading. |
| **Cloud Deployment** | Deploy to a cloud platform (AWS ECS, Google Cloud Run, or Railway.app) using the existing Docker image, replacing SQLite with PostgreSQL for production-grade persistence. |
| **Alerting Notifications** | Integrate SMTP email or Twilio SMS alerts when threshold violations are detected, triggered from `_check_and_insert_alerts()`. |
| **Unit Test Suite** | Add `pytest` tests for all API endpoints using Flask's test client, and unit tests for `sensor_sim` and `database` modules. |

---

## Section 12: References

1. Grinberg, M. (2018). *Flask Web Development: Developing Web Applications with Python* (2nd ed.). O'Reilly Media.

2. Python Software Foundation. (2024). *Python 3.11 Documentation â€” sqlite3 module*. Retrieved from https://docs.python.org/3/library/sqlite3.html

3. Python Software Foundation. (2024). *Python 3.11 Documentation â€” tkinter (Tk interface)*. Retrieved from https://docs.python.org/3/library/tkinter.html

4. Python Software Foundation. (2024). *Python 3.11 Documentation â€” threading â€” Thread-based parallelism*. Retrieved from https://docs.python.org/3/library/threading.html

5. Python Software Foundation. (2024). *Python 3.11 Documentation â€” xml.etree.ElementTree*. Retrieved from https://docs.python.org/3/library/xml.etree.elementtree.html

6. Chart.js Contributors. (2024). *Chart.js Documentation â€” Getting Started*. Retrieved from https://www.chartjs.org/docs/latest/

7. Docker Inc. (2024). *Docker Documentation â€” Dockerfile reference*. Retrieved from https://docs.docker.com/engine/reference/builder/

8. Docker Inc. (2024). *Docker Documentation â€” Compose file version 3 reference*. Retrieved from https://docs.docker.com/compose/compose-file/

9. MDN Web Docs. (2024). *Fetch API*. Mozilla Developer Network. Retrieved from https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API

10. MDN Web Docs. (2024). *DOMParser*. Mozilla Developer Network. Retrieved from https://developer.mozilla.org/en-US/docs/Web/API/DOMParser

11. Bash Reference Manual. (2024). GNU Project. Retrieved from https://www.gnu.org/software/bash/manual/

12. Git SCM. (2024). *Git Documentation*. Retrieved from https://git-scm.com/doc

13. Overleaf. (2024). *LaTeX documentation and tutorials*. Retrieved from https://www.overleaf.com/learn

14. Pallets Projects. (2024). *Flask 3.0 Documentation*. Retrieved from https://flask.palletsprojects.com/en/3.0.x/

15. SQLite Consortium. (2024). *SQLite Documentation â€” PRAGMA Statements*. Retrieved from https://www.sqlite.org/pragma.html

16. Sommerville, I. (2016). *Software Engineering* (10th ed.). Pearson Education Limited.

17. Fowler, M. (2003). *UML Distilled: A Brief Guide to the Standard Object Modeling Language* (3rd ed.). Addison-Wesley.

18. psutil Contributors. (2024). *psutil Documentation*. Retrieved from https://psutil.readthedocs.io/

---

## Section 13: Annexure

### Annexure A: Project File Structure

```
weather-station/
â”œâ”€â”€ server/
â”‚   â”œâ”€â”€ app.py              # Flask API â€” Exp 7, 8, 9
â”‚   â”œâ”€â”€ database.py         # SQLite â€” Exp 3 (Forward/Reverse Engineering)
â”‚   â”œâ”€â”€ sensor_sim.py       # Auto weather sensor background thread
â”‚   â””â”€â”€ network_check.py    # Exp 5 â€” network interface check
â”œâ”€â”€ gui/
â”‚   â””â”€â”€ station_gui.py      # Exp 10 â€” Tkinter desktop GUI
â”œâ”€â”€ templates/
â”‚   â”œâ”€â”€ index.html          # Live dashboard â€” Exp 6 & 9
â”‚   â””â”€â”€ register.html       # Station registration form â€” Exp 7
â”œâ”€â”€ static/
â”‚   â”œâ”€â”€ style.css           # Dark glassmorphism CSS theme
â”‚   â””â”€â”€ app.js              # AJAX + Chart.js + JSON/XML toggle
â”œâ”€â”€ scripts/
â”‚   â””â”€â”€ start.sh            # Exp 4 â€” Bash automation script
â”œâ”€â”€ docs/
â”‚   â””â”€â”€ report.tex          # Exp 11 â€” LaTeX project report
â”œâ”€â”€ Dockerfile              # Exp 8 â€” Docker image definition
â”œâ”€â”€ docker-compose.yml      # Exp 8 â€” Docker Compose orchestration
â”œâ”€â”€ requirements.txt        # Python dependencies
â”œâ”€â”€ .gitignore              # Exp 12 â€” Git ignore rules
â””â”€â”€ README.md               # Project documentation
```

### Annexure B: API Endpoint Reference

| Endpoint | Method | Experiment | Description | Sample Response |
|----------|--------|-----------|-------------|-----------------|
| `/` | GET | 6, 9 | Live dashboard HTML | HTML page |
| `/api/current` | GET | 9 | Latest single reading | JSON object |
| `/api/readings` | GET | 9 | Last N readings (JSON) | `{"count":20,"readings":[...]}` |
| `/api/readings.xml` | GET | 9 | Last N readings (XML) | XML document |
| `/api/alerts` | GET | â€” | Recent threshold alerts | `{"alerts":[...]}` |
| `/api/stations` | GET | 7 | All registered stations | `{"stations":[...]}` |
| `/api/submit` | POST | 10 | Manual reading from GUI | `{"success":true}` |
| `/api/schema` | GET | 3 | Reverse-engineered schema | `{"schema":{...}}` |
| `/register` | GET/POST | 7 | Station registration form | HTML page |

### Annexure C: Sensor Simulation Parameters

| Parameter | Initial Value | Delta Range | Min | Max | Notes |
|-----------|--------------|-------------|-----|-----|-------|
| Temperature (Â°C) | 28.0 | Â±0.8 | -10.0 | 50.0 | + sinusoidal day/night offset |
| Humidity (%) | 60.0 | Â±1.5 | 0.0 | 100.0 | â€” |
| Pressure (hPa) | 1013.25 | Â±0.5 | 950.0 | 1050.0 | â€” |
| Wind Speed (km/h) | 12.0 | Â±2.0 | 0.0 | 120.0 | â€” |
| Wind Direction | N (idx 0) | Â±1 step | â€” | â€” | 8-point compass cyclic |

### Annexure D: Alert Threshold Table

| Alert Type | Field | Condition | Message Template |
|-----------|-------|-----------|-----------------|
| HIGH_TEMP | temperature | > 42.0Â°C | "Temperature XÂ°C exceeds max threshold!" |
| LOW_TEMP | temperature | < 5.0Â°C | "Temperature XÂ°C below min threshold!" |
| HIGH_WIND | wind_speed | > 80.0 km/h | "Wind speed X km/h â€” High wind warning!" |

### Annexure E: Git Commit Log Sample

```
a3f9c21  feat: add XML API endpoint and client-side toggle (Exp 9)
b14e853  feat: implement Tkinter GUI for manual readings (Exp 10)
c82d401  feat: add Docker and docker-compose deployment (Exp 8)
d5a1f76  feat: station registration form with validation (Exp 7)
e901234  feat: add network interface checker (Exp 5)
f1b2c3d  feat: implement sensor simulator background thread
g4e5f6a  feat: Flask API with JSON and SQLite (Exp 9)
h7i8j9k  init: project structure, database schema (Exp 1, 3)
```

ðŸ“¸ [INSERT IMAGE: `git log --oneline` screenshot from PowerShell showing actual commit history of the project. Run `git log --oneline` in the project directory.]

### Annexure F: Docker Container Health Check Log

```
$ docker inspect weather_station_app | grep -A5 Health
"Health": {
    "Status": "healthy",
    "FailingStreak": 0,
    "Log": [
        {
            "Start": "2026-04-28T12:30:00.000Z",
            "End": "2026-04-28T12:30:01.234Z",
            "ExitCode": 0,
            "Output": ""
        }
    ]
}
```

ðŸ“¸ [INSERT IMAGE: `docker inspect weather_station_app` terminal output or `docker ps` showing STATUS as "healthy (1 second ago)". Run after `docker-compose up --build` and screenshot.]

### Annexure G: requirements.txt

```
Flask==3.0.3
flask-cors==4.0.1
psutil==5.9.8
```

### Annexure H: .gitignore

```
# Python
.venv/
__pycache__/
*.pyc
*.pyo

# Database
weather.db
data/

# Server runtime
server.log
server.pid

# IDE
.idea/
.vscode/
*.swp

# OS
.DS_Store
Thumbs.db
```

---

*End of Report*

**Project:** Real-Time Weather Station Dashboard
**Mini Project #13** â€” Software Tools Laboratory
**Experiments Covered:** 1 through 12
**Tech Stack:** Python 3.11 Â· Flask 3.0 Â· SQLite Â· HTML5 Â· Vanilla CSS Â· JavaScript ES2022 Â· Chart.js Â· Tkinter Â· JSON Â· XML Â· Docker Â· Docker Compose Â· Bash Â· LaTeX Â· Git
