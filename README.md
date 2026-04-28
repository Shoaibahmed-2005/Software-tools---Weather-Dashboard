# 🌦 Real-Time Weather Station Dashboard

> **Mini Project #13** — Covers Experiments 1–12 from the Software Tools lab.

A full-stack weather monitoring system where a Python backend auto-generates
realistic sensor readings, a Flask API serves them as **JSON and XML**, a
**JavaScript dashboard** updates live via AJAX every 3 seconds, and a
**Tkinter GUI** lets you push manual readings. Deployable via **Docker**.

---

## 📋 Experiments Covered

| Exp | Topic | Implementation |
|-----|-------|---------------|
| 1 | DFD & ER Diagram | `docs/report.tex` — ER: Stations/Readings/Alerts |
| 2 | UML Diagrams | Class, Sequence, Use Case in report |
| 3 | Forward/Reverse Engineering | `server/database.py` + `/api/schema` endpoint |
| 4 | Shell Programming | `scripts/start.sh` — full automated launcher |
| 5 | Network Interface Check | `server/network_check.py` |
| 6 | JavaScript Dynamic Pages | `static/app.js` — live AJAX + Chart.js |
| 7 | Flask Forms & Validation | `/register` route — client + server validation |
| 8 | Docker Deployment | `Dockerfile` + `docker-compose.yml` |
| 9 | AJAX + JSON/XML | `/api/readings` (JSON), `/api/readings.xml` (XML) |
| 10 | Python GUI | `gui/station_gui.py` — Tkinter desktop app |
| 11 | LaTeX Document | `docs/report.tex` — paste into Overleaf → PDF |
| 12 | Version Control | `.gitignore`, Git workflow below |

---

## 🗂 Project Structure

```
weather-station/
├── server/
│   ├── app.py              # Flask API
│   ├── database.py         # SQLite — Forward Engineering from ER
│   ├── sensor_sim.py       # Auto weather sensor (background thread)
│   └── network_check.py    # Exp 5 — network interfaces
├── gui/
│   └── station_gui.py      # Exp 10 — Tkinter GUI
├── templates/
│   ├── index.html          # Live dashboard
│   └── register.html       # Station registration form
├── static/
│   ├── style.css           # Dark glassmorphism theme
│   └── app.js              # AJAX + Chart.js + JSON/XML toggle
├── scripts/
│   └── start.sh            # Exp 4 — Bash launch script
├── docs/
│   └── report.tex          # Exp 11 — LaTeX project report
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .gitignore
```

---

## 🚀 Quick Start (Windows)

### Option A — Direct Python

```powershell
# 1. Navigate to project
cd "D:\Mini project - Software tools\weather-station"

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start the server
python server/app.py

# 4. Open the dashboard
# http://localhost:5000
```

### Option B — Shell Script (WSL / Git Bash)

```bash
bash scripts/start.sh
```

### Option C — Docker

```powershell
docker-compose up --build
# Dashboard at http://localhost:5000
```

---

## 🖥️ Tkinter GUI

In a **separate terminal** while the server is running:

```powershell
python gui/station_gui.py
```

Fill in sensor values → click Submit → watch the dashboard update!

---

## 🌐 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Live dashboard |
| `/api/current` | GET | Latest reading (JSON) |
| `/api/readings` | GET | Last 20 readings (JSON) |
| `/api/readings.xml` | GET | Last 20 readings (XML) |
| `/api/alerts` | GET | Recent threshold alerts |
| `/api/stations` | GET | All registered stations |
| `/api/submit` | POST | Submit manual reading (GUI) |
| `/api/schema` | GET | Reverse-engineered DB schema |
| `/register` | GET/POST | Station registration form |

---

## 🔬 Experiment 5 — Network Check

```powershell
python server/network_check.py
```

Lists all network interfaces, checks internet, and tests server reachability.

---

## 🐳 Docker Notes

```powershell
# Build and run
docker-compose up --build

# Stop
docker-compose down

# View logs
docker logs weather_station_app
```

---

## 📄 LaTeX Report

Open `docs/report.tex` in [Overleaf](https://www.overleaf.com) and compile
to generate a complete PDF project report with DFD, ER, UML diagrams,
architecture, and screenshots.

---

## 🔧 Git Workflow (Experiment 12)

```bash
git init
git add .
git commit -m "Initial commit — Weather Station Dashboard"
git remote add origin <your-repo-url>
git push -u origin main
```

---

## 📊 Tech Stack

- **Backend**: Python 3.11 · Flask 3.0 · SQLite
- **Frontend**: HTML5 · Vanilla CSS · JavaScript (ES2022) · Chart.js
- **GUI**: Python Tkinter
- **Data Formats**: JSON · XML
- **Deployment**: Docker · Docker Compose
- **Shell**: Bash
- **Documentation**: LaTeX (Overleaf)
