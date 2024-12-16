from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import Optional

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/fortune")
def fortune(zodiac: Optional[str] = None, sentiment: Optional[str] = None):
    if not zodiac or not sentiment:
        raise HTTPException(status_code=400, detail="Missing parameters")

    # Generate a fortune cookie text based on the parameters
    fortune_text = f"Your {zodiac} sign indicates a {sentiment} day ahead!"

    return {"fortune": fortune_text}


# Mount the static files directory
app.mount("/", StaticFiles(directory="static"), name="static")

if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
