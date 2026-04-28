#!/usr/bin/env bash
# =============================================================================
# start.sh — Experiment 4: Linux Shell Script
# Automates server startup, dependency checks, and health monitoring.
# Usage (Linux/Mac/WSL): bash scripts/start.sh
# =============================================================================

set -e

BOLD="\033[1m"
CYAN="\033[1;36m"
GREEN="\033[1;32m"
YELLOW="\033[1;33m"
RED="\033[1;31m"
RESET="\033[0m"

LOG_FILE="server.log"
VENV_DIR=".venv"
PORT=5000

banner() {
  echo -e "${CYAN}"
  echo "  ╔══════════════════════════════════════════╗"
  echo "  ║   🌦  Weather Station — Auto Launcher   ║"
  echo "  ║      Experiment 4: Shell Programming     ║"
  echo "  ╚══════════════════════════════════════════╝"
  echo -e "${RESET}"
}

log()  { echo -e "${GREEN}[✓]${RESET} $1"; }
warn() { echo -e "${YELLOW}[!]${RESET} $1"; }
err()  { echo -e "${RED}[✗]${RESET} $1"; }
info() { echo -e "${CYAN}[→]${RESET} $1"; }

# ── Step 1: Check Python ─────────────────────────────────────────────────────
check_python() {
  info "Checking Python installation..."
  if command -v python3 &>/dev/null; then
    PY_VERSION=$(python3 --version 2>&1)
    log "Found $PY_VERSION"
    PYTHON=python3
  elif command -v python &>/dev/null; then
    PY_VERSION=$(python --version 2>&1)
    log "Found $PY_VERSION"
    PYTHON=python
  else
    err "Python not found. Please install Python 3.8+ first."
    exit 1
  fi
}

# ── Step 2: Virtual Environment ───────────────────────────────────────────────
setup_venv() {
  if [ ! -d "$VENV_DIR" ]; then
    info "Creating virtual environment in $VENV_DIR ..."
    $PYTHON -m venv $VENV_DIR
    log "Virtual environment created."
  else
    log "Virtual environment already exists."
  fi

  # Activate
  if [ -f "$VENV_DIR/bin/activate" ]; then
    source "$VENV_DIR/bin/activate"
    log "Virtual environment activated."
  else
    warn "Could not activate venv — continuing with system Python."
  fi
}

# ── Step 3: Install Dependencies ──────────────────────────────────────────────
install_deps() {
  info "Installing Python dependencies from requirements.txt ..."
  pip install -q -r requirements.txt
  log "Dependencies installed."
}

# ── Step 4: Network check ─────────────────────────────────────────────────────
network_check() {
  info "Running network interface check (Experiment 5)..."
  $PYTHON server/network_check.py 2>/dev/null || warn "Network check failed — continuing."
}

# ── Step 5: Initialise Database ───────────────────────────────────────────────
init_database() {
  info "Initialising database (Forward Engineering)..."
  $PYTHON -c "
import sys; sys.path.insert(0,'server')
from database import init_db, reverse_engineer_schema
init_db()
schema = reverse_engineer_schema()
print('[Reverse Engineering] Tables found:', list(schema.keys()))
"
  log "Database ready."
}

# ── Step 6: Port availability check ───────────────────────────────────────────
check_port() {
  if command -v lsof &>/dev/null; then
    if lsof -Pi :$PORT -sTCP:LISTEN -t &>/dev/null; then
      warn "Port $PORT is already in use. Attempting to kill existing process..."
      kill -9 $(lsof -Pi :$PORT -sTCP:LISTEN -t) 2>/dev/null || true
      sleep 1
    fi
  fi
}

# ── Step 7: Start Flask ───────────────────────────────────────────────────────
start_server() {
  info "Starting Flask server on http://0.0.0.0:$PORT ..."
  nohup $PYTHON server/app.py > "$LOG_FILE" 2>&1 &
  SERVER_PID=$!
  echo $SERVER_PID > server.pid
  log "Server started (PID: $SERVER_PID)"
  log "Logs: $LOG_FILE"
}

# ── Step 8: Health check ──────────────────────────────────────────────────────
health_check() {
  info "Waiting for server to come up..."
  for i in {1..10}; do
    sleep 1
    if $PYTHON -c "
import urllib.request
try:
    urllib.request.urlopen('http://localhost:$PORT/api/current', timeout=2)
    print('ok')
except: pass
" 2>/dev/null | grep -q ok; then
      log "Server is healthy at http://localhost:$PORT"
      echo ""
      echo -e "${BOLD}${GREEN}  Dashboard → http://localhost:$PORT${RESET}"
      echo -e "${BOLD}${CYAN}  JSON API  → http://localhost:$PORT/api/readings${RESET}"
      echo -e "${BOLD}${YELLOW}  XML Feed  → http://localhost:$PORT/api/readings.xml${RESET}"
      echo ""
      return
    fi
    echo -n "."
  done
  warn "Server may not have started. Check $LOG_FILE for errors."
}

# ── Step 9: Tail logs ─────────────────────────────────────────────────────────
tail_logs() {
  echo -e "${CYAN}[→] Tailing server log (Ctrl+C to stop)...${RESET}"
  tail -f "$LOG_FILE"
}

# ── Main ──────────────────────────────────────────────────────────────────────
main() {
  banner
  check_python
  setup_venv
  install_deps
  network_check
  init_database
  check_port
  start_server
  health_check
  tail_logs
}

main "$@"
