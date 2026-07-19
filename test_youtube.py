import requests, os
from dotenv import load_dotenv
load_dotenv()

resp = requests.get(
    "https://www.googleapis.com/youtube/v3/playlistItems",
    params={
        "key": os.getenv("YOUTUBE_API_KEY"),
        "playlistId": "UU6TaYtcc4hbJPaXt6SHmyyQ",
        "part": "snippet",
        "maxResults": 5,
    }
).json()

print(resp)