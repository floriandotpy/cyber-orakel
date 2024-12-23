# cyber-orakel

Erfahre deine Zukunft per Cyber-Keks

# Setup

Install Ollama (needed for running a local LLM)

- https://ollama.com/download/

Fetch the following LLM. It's small and should run on current local machines all the way down to a Raspberry Pi 5.

```commandline
ollama pull gemma2:2b

# optional: try if the model runs properly
ollama run gemma2:2b
```


```commandline
python3 -m venv venv
pip install -r requirements.txt
```

# Run

Without printer support:

```commandline
python main.py --noprinter
```

With printer support:
    
```commandline
python main.py
```


Then open your browser and go to `http://localhost:8000/`

## Raspberry Pi setup

### Setup
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

### Run
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
