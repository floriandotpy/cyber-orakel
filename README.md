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
