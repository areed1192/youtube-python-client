import unittest
from unittest import TestCase
from configparser import ConfigParser
from youtube.client import YouTubeClient


class YoutubeSession(TestCase):

    """Will perform a unit test for the Youtube session."""

    def setUp(self) -> None:
        """Set up the Client."""

        # Grab configuration values.
        config = ConfigParser()
        config.read('configs/config.ini')

        api_key = config.get('main', 'api_key')
        channel_id = config.get('main', 'channel_id')
        state_path = config.get('main', 'state_path')
        client_secret = config.get('main', 'client_secret_path')

        # Initalize the session.
        self.youtube_session = YouTubeClient(
            api_key=api_key,
            channel_id=channel_id,
            client_secret_path=client_secret,
            state_path=state_path
        )

    def test_creates_instance_of_session(self):
        """Create an instance and make sure it's a YouTube Client."""

        self.assertIsInstance(self.youtube_session, YouTubeClient)

    def test_playlist_items(self):
        """Create an instance and make sure it's a YouTube Client."""

        # Define the playlist.
        paylist_id = 'PLcFcktZ0wnNmdgAdv4-Yl_nzS5LiKnhnn'

        # Grab the data.
        playlist_data = self.youtube_session.playlists_items(
            playlist_id=paylist_id,
            all_pages=True
        )

        # Make sure it's a list.
        self.assertIsInstance(playlist_data, list)

        # Make sure the key is right.
        self.assertIn('kind', playlist_data[0])

    def tearDown(self) -> None:
        """Teardown the YouTube Client."""

        self.youtube_session = None


if __name__ == '__main__':
    unittest.main()
