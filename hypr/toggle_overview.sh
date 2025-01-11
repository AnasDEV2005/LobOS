
#!/bin/bash

# Path to the Python script and environment source file
PYTHON_SCRIPT="side-panel/header.py"
ENV_SOURCE="fabric-venv/bin/activate"

# Temporary file to store the PID of the running Python script
PID_FILE="/tmp/python_script_toggle.pid"

start_script() {
  if [ -f "$PID_FILE" ]; then
    echo "Script is already running."
  else
    echo "Starting the Python script..."
    source "$ENV_SOURCE"
    python "$PYTHON_SCRIPT" &
    echo $! > "$PID_FILE"
    echo "Python script started with PID $(cat $PID_FILE)."
  fi
}

stop_script() {
  if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if kill -0 "$PID" 2>/dev/null; then
      echo "Stopping the Python script with PID $PID..."
      kill "$PID"
      rm "$PID_FILE"
      echo "Python script stopped."
    else
      echo "No running process found for PID $PID. Cleaning up PID file."
      rm "$PID_FILE"
    fi
  else
    echo "No script is currently running."
  fi
}

toggle_script() {
  if [ -f "$PID_FILE" ]; then
    stop_script
  else
    start_script
  fi
}

toggle_script
