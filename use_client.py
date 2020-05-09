from pprint import pprint
from configparser import ConfigParser
from youtube.client import YouTubeClient

# Grab configuration values.
config = ConfigParser()
config.read('configs/config.ini')

api_key = config.get('main', 'api_key_tutorial')
channel_id = config.get('main', 'channel_id')
playlist_id = config.get('main','playlist_id')
client_secret_path = config.get('main', 'client_secret_path_tutorial')
state_path = config.get('main', 'state_path_tutorial')

# Create a new instance of the Client.
youtube_session = YouTubeClient(
    api_key=api_key,
    channel_id=channel_id,
    client_secret_path=client_secret_path,
    state_path=state_path
)

# Grab all Playlists for my channel.
channel_playlists = youtube_session.grab_channel_playlists(parts = ['snippet','contentDetails'])

# Create a new file and save the playlists.
new_json_file_path = youtube_session.save_to_json_file(
    file_name='channel_playlists',
    youtube_content=channel_playlists
)

# Grab all the items for a particular playlist ID.
playlist_items = youtube_session.playlists_items(playlist_id=playlist_id, all_pages=True)

# Save the data to a JSON file.
new_json_file_path = youtube_session.save_to_json_file(
    file_name='all_playlist_items',
    youtube_content=playlist_items
)
print(new_json_file_path)
