from configparser import ConfigParser
from youtube.client import YouTubeClient

# Grab configuration values.
config = ConfigParser()
config.read('configs/config.ini')

API_KEY = config.get('main', 'API_KEY')
CHANNEL_ID = config.get('main', 'CHANNEL_ID')
CLIENT_SECRET_PATH = config.get('main', 'CLIENT_SECRET_PATH')
STATE_PATH = config.get('main', 'STATE_PATH')

# Create a new instance of the Client.
youtube_session = YouTubeClient(
    api_key=API_KEY,
    channel_id=CHANNEL_ID,
    client_secret_path=CLIENT_SECRET_PATH,
    state_path=STATE_PATH
)

print(youtube_session.DATA_FOLDER_PATH)
