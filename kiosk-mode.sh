#!/bin/bash

# Wechseln Sie in das Projektverzeichnis
cd ~/cyber-orakel/

# Aktivieren Sie die virtuelle Umgebung
source venv/bin/activate

# Starten Sie das Python-Skript im Hintergrund
python3 main.py &

# Warten Sie 5 Sekunden, um sicherzustellen, dass der Server gestartet ist
sleep 5

# Starten Sie den Chromium-Browser im Kiosk-Modus
chromium-browser --kiosk "http://localhost:8000" --noerrdialogs --disable-infobars