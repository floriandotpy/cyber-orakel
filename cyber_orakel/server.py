from typing import Optional

import pygame
import uvicorn
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from gtts import gTTS
from langchain_ollama import ChatOllama
from starlette.responses import FileResponse
from cyber_orakel.print import print_receipt


class Settings:
    def __init__(self, enable_printer: bool = True, enable_tts: bool = False):
        self.enable_printer = enable_printer
        self.enable_tts = enable_tts


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

    def read_out_loud(self, text: str, lang: str = "de") -> str:
        tts = gTTS(text=text, lang=lang, slow=False)
        tts.save("speech.mp3")

        # play message
        pygame.mixer.init()
        pygame.mixer.music.load("../speech.mp3")
        pygame.mixer.music.play()

    def generate_fortune(self, zodiac: str, sentiment: str, num_lines: int = 2, language: str = "German") -> str:
        prompt = f"""You are a fortune teller in a cyberpunk story.
        Write a fortune cookie message for the cyber zodiac "{zodiac}"
        with a sentiment of "{sentiment}". The message should be exactly {num_lines} lines long.
        Write in {language}. Do not explain your answer. Be short and concise."""

        llm = ChatOllama(model="gemma2:2b")
        msg = llm.invoke(prompt)

        if self.settings.enable_tts:
            self.read_out_loud(msg.content)

        return msg.content

    def setup_routes(self):
        @self.app.get("/fortune")
        def fortune(zodiac: Optional[str] = None, sentiment: Optional[str] = None):
            if not zodiac or not sentiment:
                raise HTTPException(status_code=400, detail="Missing parameters")

            # Generate a fortune cookie text based on the parameters
            fortune_text = self.generate_fortune(zodiac, sentiment)

            if self.settings.enable_printer:
                print_receipt(fortune_text)

            return {"fortune": fortune_text}

        @self.app.get("/")
        def read_root():
            # render the index.html file
            return FileResponse("static/index.html")

        # Mount the static files directory
        self.app.mount("/static", StaticFiles(directory="static"), name="static")

    def run(self):
        uvicorn.run(self.app, host="0.0.0.0", port=8000)


def run_server(enable_printer: bool = True, enable_tts: bool = False):
    settings = Settings(enable_printer=enable_printer, enable_tts=enable_tts)
    server = CyberOracleServer(settings)
    server.run()
