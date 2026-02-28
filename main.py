from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from youtube_transcript_api import YouTubeTranscriptApi
import re

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AskRequest(BaseModel):
    video_url: str
    topic: str

def extract_video_id(url: str):
    match = re.search(r"(?:v=|youtu\.be/)([^&]+)", url)
    if not match:
        raise HTTPException(status_code=400, detail="Invalid YouTube URL")
    return match.group(1)

def seconds_to_hms(seconds: float):
    seconds = int(seconds)
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours:02}:{minutes:02}:{secs:02}"

@app.post("/ask")
async def find_timestamp(request: AskRequest):
    try:
        video_id = extract_video_id(request.video_url)
        transcript = YouTubeTranscriptApi.list_transcripts(video_id).find_transcript(['en']).fetch()

        topic_lower = request.topic.lower()

        for entry in transcript:
            if topic_lower in entry["text"].lower():
                timestamp = seconds_to_hms(entry["start"])
                return {
                    "timestamp": timestamp,
                    "video_url": request.video_url,
                    "topic": request.topic
                }

        raise HTTPException(status_code=404, detail="Topic not found")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
