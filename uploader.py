import os
import json
import random
import requests
from gradio_client import Client
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# 1. Hugging Face Space se Video Generate Karein
def generate_video():
    topics = [
        "Cute Talking Apple",
        "Funny Talking Banana",
        "Dancing Cat in Space",
        "Little Robot Explorer"
    ]
    prompt = random.choice(topics)
    print(f"Selected Topic: {prompt}")

    # Hugging Face Token secret se uthayen
    hf_token = os.environ.get("HF_TOKEN")
    
    # Hugging Face Space Client Connect WITH CORRECT PARAMETER
    client = Client("shazybha12-ai-video-generator", token=hf_token)
    
    result = client.predict(prompt)
    print("Video generation completed:", result)
    return result

# 2. YouTube Par Video Upload Karein
def upload_to_youtube(video_path):
    token_data = os.environ.get("YOUTUBE_TOKEN")
    if not token_data:
        raise ValueError("YOUTUBE_TOKEN secret nahi mila!")

    creds_dict = json.loads(token_data)
    credentials = Credentials.from_authorized_user_info(creds_dict)
    youtube = build("youtube", "v3", credentials=credentials)

    body = {
        "snippet": {
            "title": "AI Short #Shorts",
            "description": "Auto generated video #shorts #ai",
            "tags": ["shorts", "ai", "animation"],
            "categoryId": "15"
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False
        }
    }

    media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    response = request.execute()
    print("YouTube Upload Successful! Video ID:", response.get("id"))

if __name__ == "__main__":
    video_file = generate_video()
    upload_to_youtube(video_file)
