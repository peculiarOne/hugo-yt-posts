import os
from dotenv import load_dotenv

import googleapiclient.discovery
import googleapiclient.errors

def fetch_uploads(api_key, channel_id, count):
    api_service_name = "youtube"
    api_version = "v3"

    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey=api_key)

    request = youtube.channels().list(
        part="snippet,contentDetails",
        id=channel_id
    )
    response = request.execute()

    uploads = response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
    print("uploads ", uploads)

    playlist_items_request = youtube.playlistItems().list(
        playlistId=uploads,
        part="snippet",
        maxResults=15
    )
    playlist_items_response = playlist_items_request.execute()
    print("\n")
    print("playlist:\n", playlist_items_response)

def main():

    load_dotenv()

    api_key = os.getenv("API_KEY")
    channel_id = os.getenv("CHANNEL_ID")

    fetch_uploads(api_key, channel_id, 15)

if __name__ == "__main__":
    main()