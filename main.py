from googleapiclient.discovery import build

API_KEY = "XXX"

CHANNEL_ID = "XXX"

youtube = build(
    "youtube",
    "v3",
    developerKey=API_KEY
)

request = youtube.search().list(
    part="snippet",
    q="ddxmusic68",
    type="video",
    maxResults=10
)

response = request.execute()

for item in response["items"]:
    video_id = item["id"]["videoId"]
    title = item["snippet"]["title"]

    print(title)
    print(f"https://www.youtube.com/watch?v={video_id}")
    print()