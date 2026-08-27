import os
from gradio_client import Client

print("Connecting to Hugging Face API...")
client = Client("shazybha12/ai-video-generator")

print("Generating video...")
video_path = client.predict(
    prompt="A majestic lion standing on a cliff at sunset, cinematic lighting, 4k",
    api_name="/generate"
)

print(f"Video generated successfully at: {video_path}")
