import os
import requests
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)
YOUTUBE_KEY = os.getenv("YOUTUBE_API_KEY")


def search_youtube(query: str, max_results: int = 3) -> List[Dict]:
    """Return list of videos: {title, channel, url, thumbnail}"""
    if not YOUTUBE_KEY:
        logger.warning("YOUTUBE_API_KEY not set; returning empty results")
        return []

    try:
        url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            "part": "snippet",
            "q": query,
            "type": "video",
            "maxResults": max_results,
            "key": YOUTUBE_KEY,
            "videoDuration": "medium",
        }
        r = requests.get(url, params=params, timeout=15)
        r.raise_for_status()
        items = r.json().get("items", [])
        results = []
        for it in items:
            vid_id = it.get("id", {}).get("videoId")
            if not vid_id:
                continue
            results.append({
                "title": it.get("snippet", {}).get("title"),
                "channel": it.get("snippet", {}).get("channelTitle"),
                "url": f"https://www.youtube.com/watch?v={vid_id}",
                "thumbnail": it.get("snippet", {}).get("thumbnails", {}).get("default", {}).get("url"),
            })
        return results
    except Exception:
        logger.exception("YouTube search failed for query: %s", query)
        return []