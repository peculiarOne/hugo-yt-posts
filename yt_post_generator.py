import os
import requests
import argparse

from pathlib import Path
from dotenv import load_dotenv
from dateutil import parser
from datetime import datetime

import googleapiclient.discovery
import googleapiclient.errors

FRONTMATTER_DELIM = '+++'

class Video:
    def __init__(self, title, video_id, publish_date, thumbnail_url):
        self.title = title
        self.video_id = video_id
        self.publish_date = publish_date
        self.thumbnail_url = thumbnail_url

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
        for key,value in self.frontmatter.items():
            lines.append(f'''{key} = "{value}"''')
        lines.append(FRONTMATTER_DELIM)
        lines.append(self.content)

        return '\n'.join(lines)

def video_to_post(video, thumbnail):
    return HugoPost(
        frontmatter = {
            "title": video.title,
            "date": video.publish_date.strftime("%Y-%m-%d"),
            "video_id": video.video_id,
            "thumbnail": thumbnail
        },
        content = ""
    )

def write_video(video, section, out_dir):
    rel_thumbnail = f'img/{section}/{video.video_id}.jpg'
    thumbnail_file = f'{out_dir}/static/{rel_thumbnail}'
    download_thumbnail(video.thumbnail_url, thumbnail_file)

    hugo_post = video_to_post(video, rel_thumbnail)
    post_file = f'{out_dir}/content/{section}/{video.video_id}.md'
    parent = Path(post_file).parent
    os.makedirs(parent, exist_ok=True)
    with open(post_file, mode='w') as f:
        f.write(f'{hugo_post}')
    


def download_thumbnail(url, dest):
    response = requests.get(url)

    parent = Path(dest).parent
    os.makedirs(parent, exist_ok=True)
    with open(dest, mode='wb') as f:
        f.write(response.content)

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
        snippet = playlist_item["snippet"]
        thumbnail = snippet["thumbnails"].get("standard")
        if thumbnail is None:
            thumbnail = snippet["thumbnails"].get("default")

        return Video(
            publish_date = parser.isoparse(snippet["publishedAt"]),
            title = snippet["title"],
            video_id = snippet["resourceId"]["videoId"],
            thumbnail_url = thumbnail["url"]
        )

    videos = list(map(item_to_video, playlist_items_response["items"]))
    return videos

def main():

    load_dotenv()

    api_key = os.getenv("API_KEY")
    channel_id = os.getenv("CHANNEL_ID")
    if api_key is None:
        raise(NameError('API_KEY wasn\'t provided'))
    if channel_id is None:
        raise(NameError('CHANNEL_ID wasn\'t provided'))

    parser = argparse.ArgumentParser()
    parser.add_argument('section_name')
    parser.add_argument('out_dir')
    args = parser.parse_args()

    videos = fetch_uploads(api_key, channel_id, 8)
    for video in videos:
        write_video(video, args.section_name, args.out_dir)

if __name__ == "__main__":
    main()
