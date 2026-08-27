import os
import random
import requests
from gradio_client import Client
from gtts import gTTS
from moviepy.editor import VideoFileClip, AudioFileClip

# 1. Kids Content Topics Pool
TOPICS = [
    {"name": "Cute Talking Apple", "prompt": "3D animated cute smiling Apple dancing, vibrant colors, Pixar style, 4k"},
    {"name": "Baby Elephant Playing", "prompt": "3D animated baby elephant running in a magical jungle, cute, Pixar style"},
    {"name": "Dancing Banana", "prompt": "3D animated banana wearing sunglasses dancing happily, kids video, 4k"}
]

def generate_automation():
    item = random.choice(TOPICS)
    print(f"Selected Trend/Topic: {item['name']}")
    
    # 2. Audio Script (Voiceover) Generation
    script_text = f"Hello kids! Look at this cute {item['name']}. Isn't it super fun? Subscribe for more!"
    tts = gTTS(text=script_text, lang='en', slow=False)
    tts.save("voice.mp3")
    print("Voiceover generated.")

    # 3. Call Hugging Face API for Video
    print("Calling Hugging Face Video API...")
    client = Client("shazybha12/ai-video-generator")
    video_temp_path = client.predict(
        prompt=item['prompt'],
        api_name="/predict"
    )

    # 4. Merge Audio with Generated Video (MoviePy)
    print("Merging Video and Audio...")
    video_clip = VideoFileClip(video_temp_path)
    audio_clip = AudioFileClip("voice.mp3")
    
    # Loop audio or set video duration to match audio
    final_clip = video_clip.set_audio(audio_clip)
    final_output = "final_short.mp4"
    final_clip.write_videofile(final_output, codec="libx264", audio_codec="aac")
    
    print("Final Short Video Created with Sound!")
    return final_output, script_text

if __name__ == "__main__":
    generate_automation()
