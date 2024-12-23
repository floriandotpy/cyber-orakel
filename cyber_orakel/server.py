from dataclasses import dataclass
from typing import Optional

import uvicorn
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from langchain_ollama import ChatOllama
from starlette.responses import FileResponse

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

    def generate_fortune(self, zodiac: str, sentiment: str, num_lines: int = 2, language: str = "German") -> str:
        prompt = f"""You are a fortune teller in a cyberpunk story.
        Write a fortune cookie message for the cyber zodiac "{zodiac}"
        with a sentiment of "{sentiment}". The message should be exactly {num_lines} lines long.
        Write in {language}. Do not explain your answer. Be short and concise."""

        llm = ChatOllama(model="gemma2:2b")
        msg = llm.invoke(prompt)

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


def run_server(enable_printer: bool = True):
    settings = Settings(enable_printer=enable_printer)
    server = CyberOracleServer(settings)
    server.run()
