#!/bin/bash

# Setze Display für X11 (wichtig für Raspberry Pi)
export DISPLAY=:0

# Wechseln Sie in das Projektverzeichnis
cd ~/Projects/cyber-orakel/

# Aktivieren Sie die virtuelle Umgebung
source venv/bin/activate

# Log-Datei mit Timestamp
LOG_FILE="orakel_$(date +%Y%m%d).log"

echo "=== Cyber-Orakel Kiosk Mode gestartet um $(date) ===" | tee -a "$LOG_FILE"

# PIDs für Cleanup speichern
SERVER_PID=""
CHROMIUM_PID=""

# Funktion zum Cleanup bei Beendigung
cleanup() {
    echo "" | tee -a "$LOG_FILE"
    echo "=== Shutting down Cyber-Orakel... ===" | tee -a "$LOG_FILE"

    # Chromium beenden
    if [ ! -z "$CHROMIUM_PID" ]; then
        echo "Stopping Chromium (PID: $CHROMIUM_PID)..." | tee -a "$LOG_FILE"
        kill $CHROMIUM_PID 2>/dev/null
    fi
    pkill -f "chromium.*localhost:8000" 2>/dev/null

    # Server beenden
    if [ ! -z "$SERVER_PID" ]; then
        echo "Stopping Python server (PID: $SERVER_PID)..." | tee -a "$LOG_FILE"
        kill $SERVER_PID 2>/dev/null
    fi
    pkill -f "python3 main.py" 2>/dev/null
    pkill -f "uvicorn" 2>/dev/null

    echo "=== Cyber-Orakel stopped at $(date) ===" | tee -a "$LOG_FILE"
    exit 0
}

# Trap für sauberes Beenden bei Ctrl+C
trap cleanup SIGINT SIGTERM EXIT

# Starte den Server OHNE Auto-Restart im Hintergrund
echo "[$(date)] Starting Python server..." | tee -a "$LOG_FILE"
python3 main.py 2>&1 | tee -a "$LOG_FILE" &
SERVER_PID=$!

echo "Server PID: $SERVER_PID" | tee -a "$LOG_FILE"

# Warten Sie 5 Sekunden, um sicherzustellen, dass der Server gestartet ist
echo "Waiting for server to start..." | tee -a "$LOG_FILE"
sleep 5

# Starten Sie den Chromium-Browser im Kiosk-Modus
echo "[$(date)] Starting Chromium in kiosk mode..." | tee -a "$LOG_FILE"
chromium-browser --kiosk "http://localhost:8000" \
  --noerrdialogs \
  --disable-infobars \
  --incognito \
  --disable-features=TranslateUI \
  --disable-pinch \
  --overscroll-history-navigation=0 \
  --hide-scrollbars \
  --app="http://localhost:8000" \
  --no-cursor \
  --disable-background-networking \
  --disable-sync \
  --disable-default-apps \
  --disable-extensions \
  --no-first-run \
  --no-default-browser-check \
  --disable-logging \
  --log-level=3 &
CHROMIUM_PID=$!

echo "Chromium PID: $CHROMIUM_PID" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
echo "=== Cyber-Orakel is running ===" | tee -a "$LOG_FILE"
echo "Press Ctrl+C to stop" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# Warte auf Beendigung (Ctrl+C oder Chromium-Fenster schließen)
wait