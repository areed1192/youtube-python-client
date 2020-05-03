from youtube.client import YouTubeClient
from configs.config import API_KEY
from configs.config import CHANNEL_ID

youtube_session = YouTubeClient(api_key=API_KEY, channel_id=CHANNEL_ID)
