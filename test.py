import unittest
import datetime

from yt_post_generator import *

class MyTests(unittest.TestCase):
    def test(self):
        self.assertTrue(True)

    def test_hugo_post_str(self):
        post = HugoPost(
            frontmatter = {
                "title": "Some Title",
                "date": "2023-05-23",
                "tags": ["foo", "bar"]
            },
            content = "ipsum lorem"
        )

        post_s = f'{post}'
        self.assertTrue(True)

    def test_video_to_post(self):
        video = Video (
            title = "My Fab Video",
            publish_date = datetime.now(),
            video_id = "a3J0b"
        )

        post = video_to_post(video) 
        print(f'{post}')

if __name__ == '__main__':
    unittest.main()