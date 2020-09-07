import json
from pprint import pprint
from configparser import ConfigParser
from youtube.client import YouTubeClient

# This assumes you have the following Scopes Specified:
#
#   [
#       'https://www.googleapis.com/auth/youtube',
#       'https://www.googleapis.com/auth/youtube.force-ssl'
#   ]
#
# If you don't then you won't be able to pull comments.

# Grab configuration values.
config = ConfigParser()
config.read('configs/config.ini')

# Grab the values.
api_key = config.get('main', 'api_key')
state_path = config.get('main', 'state_path')
channel_id = config.get('main', 'channel_id')
playlist_id = config.get('main', 'playlist_id')
client_secret_path = config.get('main', 'client_secret_path')

# Create a new instance of the Client.
youtube_session = YouTubeClient(
    api_key=api_key,
    channel_id=channel_id,
    client_secret_path=client_secret_path,
    state_path=state_path
)

# Grab the comments.
video_comments = youtube_session.grab_comments(
    video_ids=['rlHcrAb2_fs'],
    parts=['id', 'snippet', 'replies']
)
pprint(video_comments)
