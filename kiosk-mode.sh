#!/bin/bash

# Wechseln Sie in das Projektverzeichnis
cd ~/cyber-orakel/

# Aktivieren Sie die virtuelle Umgebung
source venv/bin/activate

# Starten Sie das Python-Skript im Hintergrund
python3 main.py &

# Warten Sie 5 Sekunden, um sicherzustellen, dass der Server gestartet ist
sleep 5

# Verstecke den Mauszeiger
unclutter -idle 0 -root

# Starten Sie den Chromium-Browser im Kiosk-Modus
chromium-browser --kiosk "http://localhost:8000" --noerrdialogs --disable-infobars --incognito --disable-features=TranslateUI --disable-pinch --overscroll-history-navigation=0 --hide-scrollbars --app="http://localhost:8000" --disable-infobars --no-cursor