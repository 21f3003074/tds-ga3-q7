from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class RequestBody(BaseModel):
    video_url: str
    topic: str

@app.post("/ask")
async def ask(data: RequestBody):

    # Hardcoded timestamp (example)
    timestamp = "00:05:47"

    return {
        "timestamp": timestamp,
        "video_url": data.video_url,
        "topic": data.topic
    }
