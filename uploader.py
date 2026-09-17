import os
import json
import time
import random
import shutil
import requests
from gradio_client import Client
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SPACE_ID = "shazybha12/ai-video-generator"
SPACE_URL = "https://shazybha12-ai-video-generator.hf.space"


# ---------- 1. Hugging Face Space se video generate ----------
def _extract_video_path(result):
    """Gradio kabhi string, kabhi tuple, kabhi dict return karta hai."""
    if isinstance(result, (list, tuple)):
        for item in result:
            path = _extract_video_path(item)
            if path:
                return path
        return None
    if isinstance(result, dict):
        for key in ("video", "path", "name", "url"):
            if result.get(key):
                return _extract_video_path(result[key])
        return None
    if isinstance(result, str):
        return result
    return None


def _localize(path_or_url):
    """Agar URL mila to download karo, warna file ko working dir me copy karo."""
    if path_or_url.startswith("http://") or path_or_url.startswith("https://"):
        local = "output.mp4"
        with requests.get(path_or_url, stream=True, timeout=300) as r:
            r.raise_for_status()
            with open(local, "wb") as f:
                for chunk in r.iter_content(chunk_size=1 << 20):
                    f.write(chunk)
        return local

    if not os.path.exists(path_or_url):
        raise FileNotFoundError(f"Space ne path diya lekin file nahi mili: {path_or_url}")

    local = "output" + os.path.splitext(path_or_url)[1]
    shutil.copy(path_or_url, local)
    return local


def generate_video(max_retries=3):
    topics = [
        "Cute Talking Apple",
        "Funny Talking Banana",
        "Dancing Cat in Space",
        "Little Robot Explorer",
    ]
    prompt = random.choice(topics)
    print(f"Selected Topic: {prompt}")

    hf_token = os.environ.get("HF_TOKEN") or None
    if hf_token:
        print("HF_TOKEN mil gaya - authenticated request jayegi (zyada ZeroGPU quota milega).")
    else:
        print("WARNING: HF_TOKEN nahi mila! Anonymous request jayegi jiska ZeroGPU quota bohot kam hota hai. "
              "Check karo GitHub repo Settings > Secrets me HF_TOKEN set hai aur workflow yml me "
              "'env: HF_TOKEN: ${{ secrets.HF_TOKEN }}' step me add hai.")

    # Space ko wake up karo (sleeping space par pehli call fail ho jati hai)
    print("Waking up Hugging Face space...")
    for _ in range(6):
        try:
            r = requests.get(SPACE_URL, timeout=30)
            if r.status_code == 200:
                break
        except Exception as e:
            print("Wake-up ping warning:", e)
        time.sleep(10)

    client = Client(SPACE_ID, token=hf_token)

    # Space ka sahi endpoint khud dhoondo (is Space me ye "/generate" hai, "/predict" nahi)
    endpoints = []
    try:
        info = client.view_api(print_info=False, return_format="dict")
        endpoints = ["/" + name.lstrip("/") for name in info.get("named_endpoints", {})]
    except Exception as e:
        print("view_api warning:", e)
    if not endpoints:
        endpoints = ["/generate", "/predict"]
    print("Available endpoints:", endpoints)

    last_error = None
    for attempt in range(1, max_retries + 1):
        for api_name in endpoints:
            try:
                print(f"Predict attempt {attempt}/{max_retries} on {api_name} ...")
                result = client.predict(prompt, api_name=api_name)
                print("Raw result:", result)
                path = _extract_video_path(result)
                if not path:
                    raise RuntimeError(f"Result me koi video path nahi mila: {result!r}")
                local = _localize(path)
                print("Video ready:", local, os.path.getsize(local), "bytes")
                return local
            except Exception as e:
                last_error = e
                print(f"Failed on {api_name}: {type(e).__name__}: {e}")
        time.sleep(20)

    raise RuntimeError(
        "Video generate nahi ho saki. Agar error 'AppError' hai to masla Hugging Face Space "
        f"ke app.py me hai, GitHub code me nahi. Last error: {last_error}"
    )


# ---------- 2. YouTube par upload ----------
def upload_to_youtube(video_path):
    token_data = os.environ.get("YOUTUBE_CLIENT_SECRET")
    if not token_data:
        raise ValueError("YOUTUBE_CLIENT_SECRET secret nahi mila!")

    creds_dict = json.loads(token_data)
    credentials = Credentials.from_authorized_user_info(creds_dict)
    youtube = build("youtube", "v3", credentials=credentials)

    body = {
        "snippet": {
            "title": "AI Short #Shorts",
            "description": "Auto generated video #shorts #ai",
            "tags": ["shorts", "ai", "animation"],
            "categoryId": "15",
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False,
        },
    }

    media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    response = request.execute()
    print("YouTube Upload Successful! Video ID:", response.get("id"))


if __name__ == "__main__":
    video_file = generate_video()
    upload_to_youtube(video_file)
