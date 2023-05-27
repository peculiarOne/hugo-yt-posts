import os

from dotenv import load_dotenv
from dateutil import parser
from datetime import datetime

import googleapiclient.discovery
import googleapiclient.errors

FRONTMATTER_DELIM = '+++'

class Video:
    def __init__(self, title, video_id, publish_date):
        self.title = title
        self.video_id = video_id
        self.publish_date = publish_date

    def __str__(self):
        return self.title + ", id: " + self.video_id + ", published: " + self.publish_date.strftime('%c')

    def __repr__(self):
        return self.__str__()

class HugoPost:
    def __init__(self, frontmatter, content):
        self.frontmatter = frontmatter
        self.content = content

    def __str__(self):
        # TODO what about array frontmatter items?
        lines = [FRONTMATTER_DELIM]
        for key,value in self.frontmatter.items:
            lines.append(f'{key} = {value}')
        lines.append(FRONTMATTER_DELIM)
        lines.append(self.content)

        return '\n'.join(lines)

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
        maxResults=count
    )
    playlist_items_response = playlist_items_request.execute()

    def item_to_video(playlist_item):
        print("playlist item:\n", playlist_item)
        return Video(
            publish_date = parser.isoparse(playlist_item["snippet"]["publishedAt"]),
            title = playlist_item["snippet"]["title"],
            video_id = playlist_item["snippet"]["resourceId"]["videoId"],
        )

    videos = list(map(item_to_video, playlist_items_response["items"]))
    print("\n")
    print("found videos:\n", videos)

def main():

    load_dotenv()

    api_key = os.getenv("API_KEY")
    channel_id = os.getenv("CHANNEL_ID")

    fetch_uploads(api_key, channel_id, 15)

if __name__ == "__main__":
    main()
