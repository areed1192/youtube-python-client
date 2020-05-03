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

        API_KEY = config.get('main', 'API_KEY')
        CHANNEL_ID = config.get('main', 'CHANNEL_ID')

        # Initalize the session.
        self.youtube_session = YouTubeClient(
            api_key=API_KEY, 
            channel_id=CHANNEL_ID
        )

    def test_creates_instance_of_session(self):
        """Create an instance and make sure it's a YouTube Client."""

        self.assertIsInstance(self.youtube_session, YouTubeClient)

    def tearDown(self) -> None:
        """Teardown the YouTube Client."""

        self.youtube_session = None


if __name__ == '__main__':
    unittest.main()
