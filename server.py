from typing import Optional

import pygame
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from gtts import gTTS
from langchain_ollama import ChatOllama

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def read_out_loud(text: str, lang: str = "de") -> str:
    tts = gTTS(text=text, lang=lang, slow=False)
    tts.save("speech.mp3")

    # play message
    pygame.mixer.init()
    pygame.mixer.music.load("speech.mp3")
    pygame.mixer.music.play()


def generate_fortune(zodiac: str, sentiment: str, num_lines: int = 2, language: str = "German") -> str:
    prompt = f"""You are a fortune teller in a cyberpunk story.
Write a fortune cookie message for the cyber zodiac "{zodiac}" 
with a sentiment of "{sentiment}". The message should be exactly {num_lines} lines long.
Write in {language}. Do not explain your answer. Be short and concise."""

    llm = ChatOllama(model="gemma2:2b")
    msg = llm.invoke(prompt)

    return msg.content


@app.get("/fortune")
def fortune(zodiac: Optional[str] = None, sentiment: Optional[str] = None):
    if not zodiac or not sentiment:
        raise HTTPException(status_code=400, detail="Missing parameters")

    # Generate a fortune cookie text based on the parameters
    fortune_text = generate_fortune(zodiac, sentiment)

    # read_out_loud(fortune_text)

    return {"fortune": fortune_text}


# Mount the static files directory
app.mount("/", StaticFiles(directory="static"), name="static")

if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
