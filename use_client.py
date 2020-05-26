from pprint import pprint
from configparser import ConfigParser
from youtube.client import YouTubeClient

# Grab configuration values.
config = ConfigParser()
config.read('configs/config.ini')

GRAB_CHANNEL_PLAYLISTS = True
GRAB_CHANNEL_PLAYLISTS_ITEMS = False
GRAB_PLAYLISTS = False
GRAB_SPECIFIC_PLAYLIST = True
GRAB_PLAYLISTS_ITEMS = False
PARSE_PLAYLISTS_ITEMS = True

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

if GRAB_CHANNEL_PLAYLISTS:

    # Grab all Playlists for my channel.
    channel_playlists = youtube_session.grab_channel_playlists(parts = ['snippet','contentDetails'])

    # Create a new file and save the playlists.
    new_json_file_path = youtube_session.save_to_json_file(
        file_name='channel_playlists',
        youtube_content=channel_playlists
    )
    print("Playlist All Channel Playlists: {path}".format(path=new_json_file_path))

if GRAB_CHANNEL_PLAYLISTS_ITEMS:

    # Grab all the items for a particular playlist ID.
    playlist_items = youtube_session.playlists_items(playlist_id=playlist_id, all_pages=True)

    # Save the data to a JSON file.
    new_json_file_path = youtube_session.save_to_json_file(
        file_name='all_playlist_items_master_playlist',
        youtube_content=playlist_items
    )

    print("Playlist All Playlist Items Master File: {path}".format(path=new_json_file_path))


if GRAB_PLAYLISTS:

    # Parse all the playlists from the List.
    all_playlists = youtube_session.parse_playlist_ids(playlist_json_path='data/channel_playlists.json')

    # Save the data to a JSON file.
    new_json_file_path = youtube_session.save_to_json_file(
        file_name='all_playlist_parsed',
        youtube_content=all_playlists
    )
    
    print("Playlist JSON File: {path}".format(path=new_json_file_path))


if GRAB_SPECIFIC_PLAYLIST:

    all_playlists = [
        'PLcFcktZ0wnNmdgAdv4-Yl_nzS5LiKnhnn'
    ]

    all_playlist_items = []

    for playlist_id in all_playlists:

        playlist_items = youtube_session.playlists_items(playlist_id=playlist_id, all_pages=True)
        all_playlist_items = all_playlist_items + playlist_items
    
    # Save the data to a JSON file.
    new_json_file_path = youtube_session.save_to_json_file(
        file_name='all_playlist_items',
        youtube_content=all_playlist_items,
        append=False
    )

    print("Playlist Items JSON File: {path}".format(path=new_json_file_path))


# Grab and Parse if specified.
if GRAB_PLAYLISTS_ITEMS:

    all_playlist_items = []

    # Loop through each playlist.
    for playlist_dict in all_playlists:

        playlist_id = playlist_dict['playlist_id']
        playlist_count = playlist_dict['playlist_item_count']

        if playlist_count != 0:
            playlist_items = youtube_session.playlists_items(playlist_id=playlist_id, all_pages=True)
            all_playlist_items = all_playlist_items + playlist_items

    # Save the data to a JSON file.
    new_json_file_path = youtube_session.save_to_json_file(
        file_name='all_playlist_items',
        youtube_content=all_playlist_items,
        append=True
    )

    print("Playlist Items JSON File: {path}".format(path=new_json_file_path))

# Grab and Parse if specified.
if PARSE_PLAYLISTS_ITEMS:

    # Parse all the playlist items from the List.
    all_playlist_items_parsed = youtube_session.parse_playlist_items(playlist_items_json_path='data/all_playlist_items.json')

    # Save the data to a JSON file.
    new_json_file_path = youtube_session.save_to_json_file(
        file_name='all_playlist_items_parsed',
        youtube_content=all_playlist_items_parsed,
        append=False
    )

    print("Playlist Items Parsed JSON File: {path}".format(path=new_json_file_path))