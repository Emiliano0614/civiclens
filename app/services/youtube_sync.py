import os
import requests
from youtube_transcript_api import YouTubeTranscriptApi
from app import db
from app.models.hearing import Hearing
from datetime import datetime
from dotenv import load_dotenv
from app.services.hearing_service import create_hearing

load_dotenv()

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
CHANNEL_ID = "UC6TaYtcc4hbJPaXt6SHmyyQ"

print("youtube_sync file is loading")


#this function does 2 things
# 1. it calls youtube api and pass it the channel id so that i can get the
# upload playlist id
#2.then with that playlist id, i call the the youtube api again
#but this time i pass it the playlist id and get the list of videos in that playlist
#with there title, date, and vid id,
#the order of the videos is from newest to oldest
#max results is the number of videos to return, default is 15
#returns a list of dicts, each dict looks like:
# {
#     "video_id": "abc123",
#     "title": "City Council Meeting - July 2026",
#     "published_at": date(2026, 7, 10)
# }
def get_channel_videos(max_results=15):
    channel_resp = requests.get(
        "https://www.googleapis.com/youtube/v3/channels",
        params={
            "key": YOUTUBE_API_KEY,
            "id": CHANNEL_ID,
            "part": "contentDetails",
        }
    ).json()

    uploads_playlist_id = channel_resp["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

    playlist_resp = requests.get(
        "https://www.googleapis.com/youtube/v3/playlistItems",
        params={
            "key": YOUTUBE_API_KEY,
            "playlistId": uploads_playlist_id,
            "part": "snippet",
            "maxResults": max_results,
        }
    ).json()

    # playlist_resp["items"] is a list of dicts, one per video,
    # each shaped like {"snippet": {"title": ..., "publishedAt": ..., "resourceId": {"videoId": ...}}}
    videos = []
    for item in playlist_resp.get("items", []):
        snippet = item["snippet"]#gets the snippet dict from the item dict
        video_id = snippet["resourceId"]["videoId"]#gets the video id from the snippet dict
        title = snippet["title"]#gets the title from the snippet dict
        published_at = datetime.fromisoformat(
            snippet["publishedAt"].replace("Z", "+00:00")
        ).date()
        videos.append({
            "video_id": video_id,
            "title": title,
            "published_at": published_at,
        })

    return videos
def sync_hidalgo_videos():
    #prints out the videos found in the channel
    videos = get_channel_videos(max_results=15)
    new_count = 0  

    for video in videos:
        video_id = video["video_id"]
        title = video["title"]
        published_at = video["published_at"]
        if db.session.query(Hearing).filter_by(youtube_video_id=video_id).first():
            print(f"Video already exists in database: {title} | {video_id}")
            break
        else:
            try:
                #fetch the transcript of that vid 
                fetcher = YouTubeTranscriptApi()
                try:
                    #gets the transcript
                    raw = fetcher.fetch(video_id)
                except Exception:
                    #if it didnt work the only get english or spanish
                    #
                    raw = fetcher.fetch(video_id, languages=['es', 'en'])
                transcript_text = " ".join([t.text for t in raw])
                print(f"Transcript fetched for {video_id} ✓")
            except Exception as e:
                #if no transcript found then break
                print(f"No transcript for {video_id}: {type(e).__name__}: {e}")
                continue

        create_hearing(title,published_at, transcript=transcript_text, youtube_video_id=video_id)
        new_count +=1 
        print(f"Added: {title}")
    print(f"Sync complete. {new_count} new videos added.")


