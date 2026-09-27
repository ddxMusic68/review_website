import re
import urllib.request
from datetime import timedelta

from googleapiclient.discovery import build

from .db import (
    get_all_video_ids,
    has_video,
    save_video_metadata,
    update_video_short,
    update_video_stats,
)

API_KEY = "AIzaSyDtvUR4nzjAlFWAPkGaWpWRMkX1BjVbPqU"
CHANNEL_ID = "UCLhipOncIKAoSBacXfmxfNw"
PAGE_SIZE = 50
VERTICAL_WIDTH = "405"

youtube = build("youtube", "v3", developerKey=API_KEY)


def get_uploads_playlist_id():
    response = youtube.channels().list(
        part="contentDetails",
        id=CHANNEL_ID,
    ).execute()
    return response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]


def sync_videos():
    playlist_id = get_uploads_playlist_id()
    added = 0
    page_token = None

    while True:
        request = youtube.playlistItems().list(
            part="snippet",
            playlistId=playlist_id,
            maxResults=PAGE_SIZE,
            pageToken=page_token,
        )
        response = request.execute()

        for item in response["items"]:
            video_id = item["snippet"]["resourceId"]["videoId"]
            if has_video(video_id):
                return added

            save_video_metadata(
                video_id=video_id,
                title=item["snippet"]["title"],
                thumbnail=item["snippet"]["thumbnails"]["medium"]["url"],
                published_at=item["snippet"]["publishedAt"],
            )
            added += 1

        page_token = response.get("nextPageToken")
        if not page_token:
            return added


def check_vertical(video_id):
    """Returns True/False if the watch page reveals orientation, else None."""
    url = f"https://www.youtube.com/watch?v={video_id}"
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        html = urllib.request.urlopen(request, timeout=10).read().decode("utf-8", "ignore")
    except Exception:
        return None
    match = re.search(r'property="og:video:width" content="(\d+)"', html)
    if match is None:
        return None
    return match.group(1) == VERTICAL_WIDTH


def parse_duration(iso_duration):
    match = re.fullmatch(
        r"PT(?:(?P<hours>\d+)H)?(?:(?P<minutes>\d+)M)?(?:(?P<seconds>\d+)S)?",
        iso_duration,
    )
    if match is None:
        return 0
    hours = int(match.group("hours") or 0)
    minutes = int(match.group("minutes") or 0)
    seconds = int(match.group("seconds") or 0)
    return timedelta(hours=hours, minutes=minutes, seconds=seconds).total_seconds()


def refresh_stats():
    video_ids = get_all_video_ids()
    updated = 0

    for start in range(0, len(video_ids), PAGE_SIZE):
        chunk = video_ids[start : start + PAGE_SIZE]
        response = youtube.videos().list(
            part="statistics,contentDetails",
            id=",".join(chunk),
        ).execute()

        for item in response["items"]:
            statistics = item.get("statistics", {})
            update_video_stats(
                video_id=item["id"],
                views=int(statistics.get("viewCount", 0)),
                likes=int(statistics.get("likeCount", 0)),
                comments=int(statistics.get("commentCount", 0)),
                duration=item["contentDetails"]["duration"],
            )
            updated += 1

    for video_id in get_all_video_ids(missing_short_only=True):
        is_short = check_vertical(video_id)
        if is_short is not None:
            update_video_short(video_id, is_short)

    return updated