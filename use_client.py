from pprint import pprint
from configparser import ConfigParser
from youtube.client import YouTubeClient

# Grab configuration values.
config = ConfigParser()
config.read('configs/config.ini')

API_KEY = config.get('main', 'API_KEY_TUTORIAL')
CHANNEL_ID = config.get('main', 'CHANNEL_ID')
PLAYLIST_ID = config.get('main','playlist_id')
CLIENT_SECRET_PATH = config.get('main', 'CLIENT_SECRET_PATH_TUTORIAL')
STATE_PATH = config.get('main', 'STATE_PATH_TUTORIAL')

# Create a new instance of the Client.
youtube_session = YouTubeClient(
    api_key=API_KEY,
    channel_id=CHANNEL_ID,
    client_secret_path=CLIENT_SECRET_PATH,
    state_path=STATE_PATH
)

# Grab all Playlists for my channel.
channel_playlists = youtube_session.grab_channel_playlists(parts = ['snippet','contentDetails'])

# Create a new file and save the playlists.
new_json_file_path = youtube_session.save_to_json_file(
    file_name='channel_playlists',
    youtube_content=channel_playlists
)

# # Grab all the items for a particular playlist ID.
# playlist_items = youtube_session.playlists_items(playlist_id=PLAYLIST_ID, all_pages=True)


# new_json_file_path = youtube_session.save_to_json_file(
#     file_name='all_playlist_items',
#     youtube_content=playlist_items
# )
# print(new_json_file_path)
