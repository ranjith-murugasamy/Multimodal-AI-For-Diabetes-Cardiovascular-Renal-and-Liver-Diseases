#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
RUN_DIR="$PROJECT_ROOT/.run"
BACKEND_PORT="${BACKEND_PORT:-5002}"
FRONTEND_PORT="${FRONTEND_PORT:-5173}"
mkdir -p "$RUN_DIR" "$PROJECT_ROOT/input/uploads" \
  "$PROJECT_ROOT/output/results" "$PROJECT_ROOT/output/screenshots" "$PROJECT_ROOT/output/paper"

backend_pid_file="$RUN_DIR/backend.pid"
frontend_pid_file="$RUN_DIR/frontend.pid"

python_bin() {
  if [[ -x "$PROJECT_ROOT/.venv/bin/python" ]]; then
    printf '%s\n' "$PROJECT_ROOT/.venv/bin/python"
  else
    command -v python3
  fi
}

setup() {
  if [[ ! -x "$PROJECT_ROOT/.venv/bin/python" ]]; then
    python3 -m venv "$PROJECT_ROOT/.venv"
  fi
  local py
  py="$(python_bin)"
  if ! "$py" -c 'import flask' >/dev/null 2>&1; then
    "$py" -m pip install -r "$PROJECT_ROOT/backend/requirements.txt"
  fi
  if [[ ! -d "$PROJECT_ROOT/frontend/node_modules" ]]; then
    (cd "$PROJECT_ROOT/frontend" && npm install)
  fi
  echo "Dependencies are ready."
}

server_pid() {
  local pid_file="$1"
  if [[ -f "$pid_file" ]]; then
    local pid
    pid="$(<"$pid_file")"
    if [[ "$pid" =~ ^[0-9]+$ ]] && kill -0 "$pid" 2>/dev/null; then
      printf '%s\n' "$pid"
      return 0
    fi
    rm -f "$pid_file"
  fi
  return 1
}

wait_for_http() {
  local url="$1" pid="$2" attempt
  for attempt in {1..40}; do
    if curl --silent --fail "$url" >/dev/null; then
      return 0
    fi
    if ! kill -0 "$pid" 2>/dev/null; then
      return 1
    fi
    sleep 0.25
  done
  return 1
}

start_backend() {
  if server_pid "$backend_pid_file" >/dev/null; then
    echo "Backend already running (PID $(<"$backend_pid_file"))."
    return
  fi
  local py pid
  py="$(python_bin)"
  BACKEND_PORT="$BACKEND_PORT" nohup "$py" "$PROJECT_ROOT/backend/app.py" \
    >"$RUN_DIR/backend.log" 2>&1 &
  pid=$!
  printf '%s\n' "$pid" >"$backend_pid_file"
  if wait_for_http "http://127.0.0.1:$BACKEND_PORT/api/health" "$pid"; then
    echo "Backend ready at http://127.0.0.1:$BACKEND_PORT (PID $pid)."
  else
    echo "Backend failed to start; see $RUN_DIR/backend.log." >&2
    return 1
  fi
}

start_frontend() {
  if server_pid "$frontend_pid_file" >/dev/null; then
    echo "Frontend already running (PID $(<"$frontend_pid_file"))."
    return
  fi
  local pid node_bin
  node_bin="$(command -v node)"
  cd "$PROJECT_ROOT/frontend"
  VITE_API_BASE="http://127.0.0.1:$BACKEND_PORT" nohup "$node_bin" \
    "$PROJECT_ROOT/frontend/node_modules/vite/bin/vite.js" \
    --host 127.0.0.1 --port "$FRONTEND_PORT" --strictPort \
    >"$RUN_DIR/frontend.log" 2>&1 &
  pid=$!
  printf '%s\n' "$pid" >"$frontend_pid_file"
  if wait_for_http "http://127.0.0.1:$FRONTEND_PORT" "$pid"; then
    echo "Frontend ready at http://127.0.0.1:$FRONTEND_PORT (PID $pid)."
  else
    echo "Frontend failed to start; see $RUN_DIR/frontend.log." >&2
    return 1
  fi
}

stop_one() {
  local name="$1" pid_file="$2" pid command
  if ! server_pid "$pid_file" >/dev/null; then
    echo "$name is not running."
    return
  fi
  pid="$(<"$pid_file")"
  command="$(ps -p "$pid" -o command= 2>/dev/null || true)"
  if [[ "$command" != *"$PROJECT_ROOT"* ]]; then
    echo "Refusing to stop $name: PID $pid does not identify this project." >&2
    rm -f "$pid_file"
    return 1
  fi
  kill "$pid"
  local attempt
  for attempt in {1..40}; do
    if ! kill -0 "$pid" 2>/dev/null; then
      rm -f "$pid_file"
      echo "$name stopped."
      return
    fi
    sleep 0.25
  done
  echo "$name did not stop; check PID $pid and its log." >&2
  return 1
}

case "${1:-}" in
  setup)
    setup
    ;;
  start)
    setup
    start_backend
    start_frontend
    ;;
  stop)
    stop_one frontend "$frontend_pid_file"
    stop_one backend "$backend_pid_file"
    ;;
  restart)
    "$0" stop
    "$0" start
    ;;
  status)
    if server_pid "$backend_pid_file" >/dev/null; then
      echo "Backend running (PID $(<"$backend_pid_file")) on port $BACKEND_PORT."
    else
      echo "Backend stopped."
    fi
    if server_pid "$frontend_pid_file" >/dev/null; then
      echo "Frontend running (PID $(<"$frontend_pid_file")) on port $FRONTEND_PORT."
    else
      echo "Frontend stopped."
    fi
    ;;
  logs)
    case "${2:-}" in
      backend) tail -n 80 -f "$RUN_DIR/backend.log" ;;
      frontend) tail -n 80 -f "$RUN_DIR/frontend.log" ;;
      *) echo "Usage: $0 logs backend|frontend" >&2; exit 2 ;;
    esac
    ;;
  *)
    echo "Usage: $0 {setup|start|stop|restart|status|logs [backend|frontend]}" >&2
    exit 2
    ;;
esac
