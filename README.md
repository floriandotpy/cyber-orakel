# cyber-orakel

> Erfahre deine Zukunft per Cyber-Keks.

This is a local-only project to generate cyber-style fortune cookie messages using a small LLM and a primitive web-based UI.

Ideally, you follow our example and deploy it on a RaspberryPi with a connected thermo printer.

## Preview of the final project

Blog post about the project: https://casualcoding.com/building-a-cyber-oracle-using-a-local-llm-on-a-raspberry-pi-5/

![cyber-orakel-photo-1](https://github.com/user-attachments/assets/ab9660e5-86b5-4ce3-8e68-d49f98d47ad8)

![cyber-orakel-photo-3](https://github.com/user-attachments/assets/ecaa91f9-e60c-4aac-9268-43b0b56a0027)

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
source venv/bin/activate
pip install -r requirements.txt
```

# Run

Without printer support:

```commandline
python main.py --no-printer
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
