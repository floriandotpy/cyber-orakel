#!/bin/bash

# Wechseln Sie in das Projektverzeichnis
cd ~/Projects/cyber-orakel/

# Aktivieren Sie die virtuelle Umgebung
source venv/bin/activate

# Log-Datei mit Timestamp
LOG_FILE="orakel_$(date +%Y%m%d).log"

echo "=== Cyber-Orakel Kiosk Mode gestartet um $(date) ===" | tee -a "$LOG_FILE"

# Funktion zum Cleanup bei Beendigung
cleanup() {
    echo "Shutting down Cyber-Orakel..." | tee -a "$LOG_FILE"
    pkill -f "python3 main.py"
    exit 0
}

# Trap für sauberes Beenden
trap cleanup SIGINT SIGTERM

# Starte den Server mit Auto-Restart im Hintergrund
(
    while true; do
        echo "[$(date)] Starting Python server..." | tee -a "$LOG_FILE"
        python3 main.py 2>&1 | tee -a "$LOG_FILE"
        EXIT_CODE=$?
        echo "[$(date)] Server stopped with exit code $EXIT_CODE. Restarting in 5 seconds..." | tee -a "$LOG_FILE"
        sleep 5
    done
) &

SERVER_PID=$!

# Warten Sie 5 Sekunden, um sicherzustellen, dass der Server gestartet ist
sleep 5

# Starten Sie den Chromium-Browser im Kiosk-Modus
chromium-browser --kiosk "http://localhost:8000" --noerrdialogs --disable-infobars --incognito --disable-features=TranslateUI --disable-pinch --overscroll-history-navigation=0 --hide-scrollbars --app="http://localhost:8000" --disable-infobars --no-cursor

# Wenn Chromium beendet wird, cleanup ausführen
cleanup