import os
from gradio_client import Client

print("Connecting to Hugging Face API...")
try:
    client = Client("shazybha12/ai-video-generator")
    
    print("Generating video...")
    result = client.predict(
        prompt="A majestic lion standing on a cliff at sunset, 4k, cinematic",
        api_name="/predict"
    )
    
    print(f"Video generated successfully! Path: {result}")
except Exception as e:
    print(f"Error while generating video: {e}")
