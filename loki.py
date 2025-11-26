import os
import requests
from typing import List, Dict

YOUTUBE_KEY = os.getenv("YOUTUBE_API_KEY")

def search_youtube(query: str, max_results: int = 3) -> List[Dict]:
    """Return list of videos: {title, channel, url}"""
    if not YOUTUBE_KEY:
        raise RuntimeError("Missing YOUTUBE_API_KEY in environment")
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "maxResults": max_results,
        "key": YOUTUBE_KEY,
    }
    r = requests.get(url, params=params, timeout=15)
    r.raise_for_status()
    items = r.json().get("items", [])
    results = []
    for it in items:
        vid = it["id"].get("videoId")
        if not vid:
            continue
        results.append({
            "title": it["snippet"].get("title"),
            "channel": it["snippet"].get("channelTitle"),
            "url": f"https://www.youtube.com/watch?v={vid}"
        })
    return results