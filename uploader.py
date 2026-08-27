import os
from gradio_client import Client

# Hugging Face Space se Video Manga rahe hain
print("Requesting video from Hugging Face API...")
client = Client("shazybha12/ai-video-generator")

# Prompt change karke aap apni marzi ka video bana sakte hain
result = client.predict(
    prompt="A majestic lion standing on a cliff at sunset, 4k, cinematic",
    api_name="/generate"
)

print(f"Video generated successfully! Path: {result}")
