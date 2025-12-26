import json
import random
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

from langchain_ollama import ChatOllama

from cyber_orakel.log_db import Fortune
from cyber_orakel.log_db import log_to_sqlite


@dataclass
class CyberZodiac:
    key: str
    display_name: str
    prompt_snippet: str
    entropy_words: Optional[list[str]] = field(default_factory=lambda: None)  # Zodiac-specific entropy words


# Global ChatOllama instance - reused across requests but stateless (no chat history)
# This prevents memory leaks from creating new instances for every fortune
_chat_instance = None


def get_chat_instance():
    """Get or create the global ChatOllama instance."""
    global _chat_instance
    if _chat_instance is None:
        _chat_instance = ChatOllama(
            model="gemma3:1b-it-qat",
            timeout=30.0  # 30 second timeout for LLM responses
        )
    return _chat_instance


SENTIMENTS = ["positive", "ecstatic", "optimistic", "dismal", "neutral", "mythical"]
ZODIAC_SIGNS: list[CyberZodiac] = [
    CyberZodiac(
        key="cyber_krieger",
        display_name="Cyber-Krieger",
        prompt_snippet="""
        - Hacking
        - Virtuelle Realität
        - Cyberspace
        - VIM
        - Fairydust
        - Chaos Computer Club
        - Chaos Communication Congress
        - Cyberdeck
        - Cyber-Angriff
        - Cyber-Attacke
        - Intrusion
        - Virus
        - Antivirus
        """,
        entropy_words=[
            "Firewall",
            "Exploit",
            "Zero-Day",
            "Penetration Test",
            "Backdoor",
            "Rootkit",
        ]),
    CyberZodiac(
        key="wissensanarcho",
        display_name="Wissensanarcho",
        prompt_snippet="""
        - Open Source
        - Datenschutz
        - Verschlüsselung
        - Whistleblowing
        - Anonymität
        - Hackerethik
        - Wissen ist Macht
        - Wissen teilen
        - Wissen ist frei
        - Creative Commons
        """,
        entropy_words=[
            "Wikileaks",
            "Tor Browser",
            "VPN",
            "Edward Snowden",
            "Informationsfreiheit",
            "Transparenz",
        ]),
    CyberZodiac(
        key="einhorn",
        display_name="Einhorn",
        prompt_snippet="""
        - Regenbogen
        - Glitzer
        - Einhörner
        - Magie
        - Liebe
        - Freundschaft
        - Konfetti
        - Kreativität
        - Chaos ist schön
        - Lächeln
        - Löten
        - Lötkolben
        - Lichterkette
        - Blinkende Lichter
        """,
        entropy_words=[
            "Glitzerstaub",
            "Regenbogenfarben",
            "Herzchen",
            "Sternchen",
            "Ponyhof",
            "Zauber",
            "Liebe"
        ]),
    CyberZodiac(
        key="cryptogeek",
        display_name="Cryptogeek",
        prompt_snippet="""
        - Public Key
        - Private Key
        - Alles verschlüsseln
        - Blockchain
        - Keysigning Party
        - GPG Key
        - https everywhere
        - Private Daten schützen, öffentliche Daten nützen
        """,
        entropy_words=[
            "AES-256",
            "RSA",
            "Hash",
            "Signatur",
            "Zertifikat",
            "End-to-End",
        ]),
    CyberZodiac(
        key="codeglaeubig",
        display_name="Codegläubig",
        prompt_snippet="""
        - Code ist Gesetz
        - Alles ist 1 außer der 0
        - Code ist Poesie
        - Code ist Kunst
        - Wer Vibe Coded lügt
        - Code hat immer Recht
        - Misstraue Autoritäten
        - Computer können dein Leben zum Besseren verändern
        - Der Code ist mit dir
        - Code ist Schönheit
        """,
        entropy_words=[
            "Git",
            "Commit",
            "Pull Request",
            "Refactoring",
            "Clean Code",
            "Debugging",
            "Vibe Coding"
        ]),
    CyberZodiac(
        key="schwurbler",
        display_name="Schwurbler",
        prompt_snippet="""
        - Chemtrails
        - Die Erde ist eine Scheibe
        - 5G
        - Globuli
        - Aluhut
        - Aluburka
        - Verschwörungstheorie
        - Bill Gates
        - Flat earther
        - Impfgegner
        """,
        entropy_words=[
            "Echsenmenschen",
            "Illuminati",
            "Neue Weltordnung",
            "Reptiloiden",
            "Mondlandung",
            "Hohlwelt",
            "Flat Earth"
        ]),
    CyberZodiac(
        key="retrohacker",
        display_name="Retrohacker",
        prompt_snippet="""
        - 8-Bit
        - C64
        - Floppy Disk
        - Retro
        - Hacker Manifest
        - Funkausstellung
        - BTX
        - Demoszene
        - Atari
        - Lötkolben
        - Löten
        """,
        entropy_words=[
            "Floppy Disk",
            "Modem",
            "CD",
            "Bitte 8-Bit",
            "ASCII Art",
            "Chiptune",
            "Pixelart",
        ]),
    CyberZodiac(
        key="datenelch",
        display_name="Datenelch",
        prompt_snippet="""
        - Wlan Geweih
        - Empfangs-Turbo
        - High speed Internet
        - Wald
        - Dorf-Internet
        - Datenautobahn
        - Logbuch Netzpolitik
        - Neuland
        """,
        entropy_words=[
            "Glasfaser",
            "Breitband",
            "Ping",
            "Latenz",
            "Bandbreite",
            "Router",
            "Große Elchwanderung"
        ]),
    CyberZodiac(
        key="tschunky",
        display_name="Tschunky",
        prompt_snippet="""
        - Tschunk ist Liebe
        - Mate macht wach
        - Limetten sind die neuen Zitronen
        - Tschunk ist Leben
        - Um 3 an der Tschunk-Bar
        - Tschunk ist die Antwort
        - 42 Tschunk pro Stunde
        - Tschunk o'clock
        - Ohne Tschunk kein Leben
        - Ein Leben ohne Tschunk ist möglich, aber sinnlos
        """,
        entropy_words=[
            "Club-Mate",
            "Flora Power",
            "Rum",
            "Brauner Zucker",
            "Minze",
            "Eiswürfel",
        ])
]


def generate_fortune(zodiac_key: str, sentiment: str, num_lines: int = 2, language: str = "German",
                     include_entropy_words: bool = True) -> str:
    zodiac = next((z for z in ZODIAC_SIGNS if z.key == zodiac_key), None)
    if not zodiac:
        # invalid zodiac sign, pick a random one
        print(f"Invalid zodiac sign: {zodiac_key}, picking a random one")
        zodiac = random.choice(ZODIAC_SIGNS)

    entropy_snippet = ""
    if include_entropy_words:
        if PATH_CURRENT_ENTROPY_JSON.exists():
            with open(PATH_CURRENT_ENTROPY_JSON, "r") as f:
                entropy_words = json.load(f)
                entropy_snippet = "\n".join([f"- {word}" for word in entropy_words])

    prompt = f"""
    Du bist ein Orakel in einer Cyber-Nerd-Welt und schreibst Glückskeks-Zettel für die/den Benutzer auf dem Chaos Computer Congress. 

    Aufgabe:
    - Schreibe GENAU {num_lines} Zeilen.
    - Sprache: Deutsch.
    - Jede Zeile ist ein ganzer Satz, kurz und prägnant.
    - Kein Markdown, keine Bulletpoints, keine Emojis, keine ASCII-Art.
    - Keine Erklärungen, kein "Hier ist dein Text:".

    Wichtigstes Sternzeichen des Benutzers/Archetyp des Orakels (baue dies gerne mit ein!): {zodiac.display_name}
    Stimmung: {sentiment}

    Stil-Inspiration (kreativ einbauen, nicht unbedingt 1:1 kopieren):
    {zodiac.prompt_snippet}

    Zusätzliche Zufallswörter (wenn vorhanden, optional einbauen):
    {entropy_snippet}

    Gib NUR den Text aus, ohne Anführungszeichen.
    """.strip()
    
    # cleanup prompt: remove leading whitespace in every line and remove double line breaks
    prompt = "\n".join([line.strip() for line in prompt.split("\n")]).replace("\n\n", "\n")
    print(prompt)

    # Get the reusable chat instance (no history, stateless)
    chat = get_chat_instance()

    # Generate fortune
    start_time = time.time()
    response = chat.invoke(prompt)
    duration = time.time() - start_time

    fortune_text = response.content

    # Print the generated fortune for debugging/testing
    print("\n" + "="*50)
    print("GENERATED FORTUNE:")
    print("="*50)
    print(fortune_text)
    print("="*50 + "\n")

    # Log to database
    fortune_obj = Fortune(
        generation_time=datetime.now(),
        fortune=fortune_text,
        prompt=prompt,
        generation_duration=duration,
        zodiac_key=zodiac_key,
        sentiment=sentiment
    )
    log_to_sqlite(fortune_obj)

    return fortune_text


def generate_many_fortunes():
    for zodiac in ZODIAC_SIGNS:
        for sentiment in SENTIMENTS:
            for _ in range(2):
                print(f"Zodiac: {zodiac.key}, Sentiment: {sentiment}")
                print(generate_fortune(zodiac.key, sentiment))
            print()


if __name__ == '__main__':
    generate_many_fortunes()
PATH_CURRENT_ENTROPY_JSON = Path(__file__).parent.parent / "current_entropy.json"
