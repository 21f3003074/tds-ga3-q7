from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import subprocess
import re
import os

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

def seconds_to_hms(seconds: float):
    seconds = int(float(seconds))
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours:02}:{minutes:02}:{secs:02}"

@app.post("/ask")
async def find_timestamp(request: AskRequest):
    try:
        video_url = request.video_url
        topic = request.topic.lower()

        # Download auto-generated subtitles using yt-dlp
        subprocess.run([
            "yt-dlp",
            "--write-auto-sub",
            "--sub-lang", "en",
            "--skip-download",
            video_url
        ], check=True)

        # Find downloaded subtitle file
        subtitle_file = None
        for file in os.listdir():
            if file.endswith(".vtt"):
                subtitle_file = file
                break

        if not subtitle_file:
            raise HTTPException(status_code=404, detail="No subtitles found")

        # Read subtitles
        with open(subtitle_file, "r", encoding="utf-8") as f:
            content = f.read()

        # Search for topic
        blocks = content.split("\n\n")

        for block in blocks:
            if topic in block.lower():
                lines = block.split("\n")
                if len(lines) > 1:
                    timestamp_line = lines[0]
                    start_time = timestamp_line.split(" --> ")[0]
                    hh, mm, ss = start_time.split(":")
                    ss = ss.split(".")[0]
                    return {
                        "timestamp": f"{hh}:{mm}:{ss}",
                        "video_url": video_url,
                        "topic": request.topic
                    }

        raise HTTPException(status_code=404, detail="Topic not found")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
