import random
from dataclasses import dataclass
from typing import Optional

import uvicorn
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse

from cyber_orakel.fortune import SENTIMENTS
from cyber_orakel.fortune import ZODIAC_SIGNS
from cyber_orakel.fortune import generate_fortune
from cyber_orakel.print import print_receipt


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

            # Generate a fortune cookie text based on the parameters
            fortune_text = generate_fortune(zodiac, sentiment)

            if self.settings.enable_printer:
                print_receipt(fortune_text)

            return {"fortune": fortune_text}

        @self.app.get("/zodiacs")
        def get_zodiacs():
            return [{"key": zodiac.key, "display_name": zodiac.display_name} for zodiac in ZODIAC_SIGNS]

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
