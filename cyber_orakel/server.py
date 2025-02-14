import json
import random
from dataclasses import dataclass
from typing import Optional

import uvicorn
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse

from cyber_orakel.fortune import PATH_CURRENT_ENTROPY_JSON
from cyber_orakel.fortune import SENTIMENTS
from cyber_orakel.fortune import ZODIAC_SIGNS
from cyber_orakel.fortune import generate_fortune
from cyber_orakel.print import print_receipt
from mastodon import Mastodon
import os


def toot(fortune_text: str):
    try:
        mastodon_access_token = os.getenv('MASTODON_ACCESS_TOKEN')
        if not mastodon_access_token:
            print("No Mastodon access token found. Skipping toot.")
            return
        # push the fortune to mastodon
        mastodon = Mastodon(
            access_token=mastodon_access_token,
            api_base_url='https://mastodon.social'
        )

        toot_text = fortune_text.strip().replace("\n", " ")

        mastodon.toot(toot_text)
    except Exception as e:
        print(f"Failed to post to Mastodon: {e}")


@dataclass
class Settings:
    enable_printer: bool = True


class CyberOracleServer:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.app = FastAPI()
        self.setup_middleware()
        self.setup_routes()

    def setup_middleware(self):
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Allow all origins
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    def setup_routes(self):
        @self.app.get("/fortune")
        def fortune(zodiac: Optional[str] = None, sentiment: Optional[str] = None):
            if not zodiac or not sentiment:
                raise HTTPException(status_code=400, detail="Missing parameters")

            sentiment = random.choice(SENTIMENTS) if sentiment == "random" else sentiment

            fortune_text = generate_fortune(zodiac, sentiment)

            if self.settings.enable_printer:
                print_receipt(fortune_text, zodiac)

            toot(fortune_text)

            return {"fortune": fortune_text}

        @self.app.get("/zodiacs")
        def get_zodiacs():
            return [{"key": zodiac.key, "display_name": zodiac.display_name} for zodiac in ZODIAC_SIGNS]

        @self.app.get("/entropy_words")
        def get_entropy_words():
            entropy_words = [
                "Klimaschutz",
                "Corona",
                "Impfpflicht",
                "Bällebad",
                "Lötkolben",
                "5G",
                "Assembly",
                "Engel",
                "Arduino",
                "Android",
                "Blinkenlights",
                "Bundestrojaner",
                "Bundeswehr",
                "CCC",
                "Chaos",
                "Chaosdorf",
                "Chaosradio",
                "Chaoswest",
                "Chaospost",
                "Cocktail",
                "Congress",
                "Saal 1",
                "3D-Druck",
                "3D-Drucker",
                "5G",
                "KI",
                "Aluburka",
                "Android",
                "Angela Merkel",
                "Arduino",
                "Assembly",
                "Backup",
                "Bällebad",
                "Blinkenlights",
                "Bundestrojaner",
                "Chaos",
                "Club",
                "Code",
                "Computer",
                "Congress",
                "Cyber",
                "Cyberwar",
                "Das geht nicht in Saal 1",
                "Datenschutz",
                "Datensicherheit",
                "De-Mail",
                "DECT",
                "Demoszene",
                "DSGVO",
                "Engel",
                "EU",
                "Europaparlament",
                "Fahrplan",
                "FPGA",
                "Freie Software",
                "Freifunk",
                "Glitzer",
                "GNU",
                "GSM",
                "Hacken",
                "Hacker Jeopardy",
                "Hacker",
                "Hackerethik",
                "hacktivism",
                "Haeckse",
                "Heaven",
                "Illegal instructions",
                "Informationsfreiheitgesetz",
                "Internet",
                "Katzenohren",
                "Kryptographie",
                "Linux",
                "Löten mit Kolben",
                "Löten ohne Kolben",
                "Löten",
                "Netzpolitik",
                "Neuland",
                "Obama",
                "Olaf Scholz",
                "Open Source",
                "Raspberry Pi",
                "Saal 1",
                "Späti",
                "Staatstrojaner",
                "Tschunk",
                "Überwachung",
                "Überwachungsstaat",
                "Ursula von der Leyen",
                "VoC",
                "Vorratsdatenspeicherung",
                "Wiki",
            ]

            # pick 9 random words
            return random.sample(entropy_words, 9)

        @self.app.post("/entropy")
        def save_entropy(data: dict):

            words = data.get("words")
            with PATH_CURRENT_ENTROPY_JSON.open("w") as f:
                json.dump(words, f)
                print(f"Saved entropy data to file: {words}")

            return {"success": True}

        @self.app.get("/")
        def read_root():
            # render the index.html file
            return FileResponse("static/index.html")

        # Mount the static files directory
        self.app.mount("/static", StaticFiles(directory="static"), name="static")

    def run(self):
        uvicorn.run(self.app, host="0.0.0.0", port=8000)


def run_server(enable_printer: bool = True):
    settings = Settings(enable_printer=enable_printer)
    server = CyberOracleServer(settings)
    server.run()
