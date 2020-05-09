from configparser import ConfigParser
from youtube_tutorial.client import YouTubeClient

# Read the config file and load the values.
config = ConfigParser()
config.read('configs/config_sample.ini')

api_key = config.get('main', 'api_key')
channel_id = config.get('main', 'channel_id')
playlist_id = config.get('main','playlist_id')
client_secret_path = config.get('main', 'client_secret_path')
state_path = config.get('main', 'state_path')

# Create a new instance of the client.
youtube_session = YouTubeClient(
    api_key=api_key,
    channel_id=channel_id,
    client_secret_path=client_secret_path,
    state_path=state_path
)