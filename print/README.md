# cyber-orakel

Drucke deine Zukunft auf einen Cyber-Keks

# Setup
Modify ssh config:

```commandline
code .ssh/config
```
add:
```
Host cyberorakel
  User pablo
  HostName pablopi.local
```

# Run
Credentials in company 1P:
https://start.1password.com/open/i?a=2Q5JDWR65RBWLPXINOB3QLIQXM&v=dumjuqu3tedivnkyt2yqrnvfzy&i=ywv3vddvivldz6iiuhdhhd4kna&h=theyconsultinggmbh.1password.eu

```commandline
ssh cyberorakel
source orakel/bin/activate
cd cyberorakel/
python3 print.py "Die digitale Schlacht wird schwer fallen."
```

Look into `kiosk-mode.txt` to use chromium in full kiosk mode:
```commandline
chromium-browser --kiosk URL --noerrdialogs --disable-infobars
```