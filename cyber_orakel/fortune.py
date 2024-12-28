import json
import random
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from langchain_ollama import ChatOllama

from cyber_orakel.log_db import Fortune
from cyber_orakel.log_db import log_to_sqlite


@dataclass
class CyberZodiac:
    key: str
    display_name: str
    prompt_snippet: str


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
        """),
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
        """),
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
        """),
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
        """),
    CyberZodiac(
        key="codeglaeubig",
        display_name="Codegläubig",
        prompt_snippet="""
        - Code ist Gesetz
        - Alles ist 1 außer der 0
        - Code ist Poesie
        - Code ist Kunst
        - Code hat immer Recht
        - Misstraue Autoritäten
        - Computer können dein Leben zum Besseren verändern
        - Der Code ist mit dir
        - Code ist Schönheit
        """),
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
        """),
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
        """),
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
        """),
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
        """)
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

    prompt = f"""You are a fortune teller in a cyberpunk story.
    Write a fortune cookie message for the cyber zodiac "{zodiac.display_name}"
    with a sentiment of "{sentiment}". The message should be exactly {num_lines} lines long.
    Write in {language}. Do not explain your answer. Be short and concise. Add no special characters.
    The following terms and phrases are typical for the cyber zodiac {zodiac.display_name}. 
    Use them as inspiration for the message but don't just copy them verbatim: 
    {zodiac.prompt_snippet}\n{entropy_snippet}"""
    # cleanup prompt: remove leading whitespace in every line and remove double line breaks
    prompt = "\n".join([line.strip() for line in prompt.split("\n")]).replace("\n\n", "\n")
    print(prompt)

    start_time = time.time()
    chat = ChatOllama(model="gemma2:2b")
    duration = time.time() - start_time

    fortune_obj = Fortune(
        generation_time=datetime.now(),
        fortune=chat.invoke(prompt).content,
        prompt=prompt,
        generation_duration=duration,
        zodiac_key=zodiac_key,
        sentiment=sentiment
    )
    log_to_sqlite(fortune_obj)

    response = chat.invoke(prompt)
    return response.content


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
