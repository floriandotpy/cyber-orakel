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

            try:
                fortune_text = generate_fortune(zodiac, sentiment)
            except Exception as e:
                print(f"Error generating fortune: {e}")
                raise HTTPException(status_code=500, detail="Failed to generate fortune. Please try again.")

            # Print receipt - don't fail if printer has issues
            if self.settings.enable_printer:
                try:
                    print_receipt(fortune_text, zodiac)
                except Exception as e:
                    print(f"Printer error (continuing anyway): {e}")

            # Post to Mastodon - don't fail if network issues
            try:
                toot(fortune_text)
            except Exception as e:
                print(f"Mastodon error (continuing anyway): {e}")

            return {"fortune": fortune_text}

        @self.app.get("/zodiacs")
        def get_zodiacs():
            return [{"key": zodiac.key, "display_name": zodiac.display_name} for zodiac in ZODIAC_SIGNS]

        @self.app.get("/entropy_words")
        def get_entropy_words(zodiac: Optional[str] = None):
            # General pool - available for all zodiacs
            general_entropy_words = [
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
                "Apple",
                "Bill Gates",
                "Portfreigabe",
                "404",
                "AI",
                "LLM",
                "Dieselgate",
                "Dinogriller",
                "Zukunft",
                "Plüsch",
                "Glitzer",
                "Tu wat"
            ]

            # Get zodiac-specific words if zodiac is provided
            zodiac_specific_words = []
            if zodiac:
                zodiac_obj = next((z for z in ZODIAC_SIGNS if z.key == zodiac), None)
                if zodiac_obj and zodiac_obj.entropy_words:
                    zodiac_specific_words = zodiac_obj.entropy_words

            # Pick 2 from zodiac-specific pool (if available)
            selected_specific = []
            if zodiac_specific_words and len(zodiac_specific_words) >= 2:
                selected_specific = random.sample(zodiac_specific_words, 2)

            # Pick 7 from general pool
            selected_general = random.sample(general_entropy_words, min(7, len(general_entropy_words)))

            # Combine and shuffle (2 zodiac-specific + 7 general = 9 total)
            all_words = selected_specific + selected_general
            random.shuffle(all_words)

            return all_words

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
