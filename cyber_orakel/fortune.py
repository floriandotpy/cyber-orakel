import random
from dataclasses import dataclass

from langchain_ollama import ChatOllama


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
        - Cyber-Implantat
        - Hacking
        - Künstliche Intelligenz
        - Virtuelle Realität
        - Cyberspace
        - VIM
        - Fairydust
        - Chaos Computer Club
        - Chaos Communication Congress
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
        """),
    CyberZodiac(
        key="datenelch",
        display_name="Datenelch",
        prompt_snippet="""
        - Wlan Geweih
        - Empfangs-Turbo
        - High speed Internet
        - Wald
        - Wald und Wiesen Internet
        - Datenautobahn
        - Logbuch Netzpolitik
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
        - 48 Tschunk pro Stunde
        - Tschunk o'clock
        - Ohne Tschunk kein Leben
        - Ein Leben ohne Tschunk ist möglich, aber sinnlos
        """)
]


async def generate_fortune(zodiac_key: str, sentiment: str, num_lines: int = 2, language: str = "German"):
    zodiac = next((z for z in ZODIAC_SIGNS if z.key == zodiac_key), None)
    if not zodiac:
        # invalid zodiac sign, pick a random one
        print(f"Invalid zodiac sign: {zodiac_key}, picking a random one")
        zodiac = random.choice(ZODIAC_SIGNS)

    prompt = f"""You are a fortune teller in a cyberpunk story.
    Write a fortune cookie message for the cyber zodiac "{zodiac.display_name}"
    with a sentiment of "{sentiment}". The message should be exactly {num_lines} lines long.
    Write in {language}. Do not explain your answer. Be short and concise. Add no special characters.
    The following terms and phrases are typical for the cyber zodiac {zodiac.display_name}. 
    Use them as inspiration for the message but don't just copy them verbatim: 
    {zodiac.prompt_snippet}"""

    chat = ChatOllama(model="gemma2:2b")

    async for chunk in chat.astream(prompt):
        yield str(chunk.content)


def generate_many_fortunes():
    for zodiac in ZODIAC_SIGNS:
        for sentiment in SENTIMENTS:
            for _ in range(2):
                print(f"Zodiac: {zodiac.key}, Sentiment: {sentiment}")
                print(generate_fortune(zodiac.key, sentiment))
            print()


if __name__ == '__main__':
    generate_many_fortunes()
