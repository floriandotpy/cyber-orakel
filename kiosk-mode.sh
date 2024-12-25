#!/bin/bash
cd ~/cyber-orakel/
source venv/bin/activate
chromium-browser --kiosk "http://localhost:8000" --noerrdialogs --disable-infobars  &
python3 main.py
