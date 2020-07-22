import json

from pprint import pprint
from configparser import ConfigParser
from youtube.client import YouTubeClient

PARSE_FILES = True

GRAB_CHANNEL_PLAYLISTS = False
GRAB_CHANNEL_PLAYLISTS_ITEMS = False
GRAB_CHANNEL_PLAYLISTS_ITEMS_ALL = False

GRAB_PLAYLISTS = False
GRAB_PLAYLISTS_ITEMS = False
GRAB_SPECIFIC_PLAYLIST = False

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

if GRAB_CHANNEL_PLAYLISTS:

    # Grab all Playlists for my channel.
    channel_playlists = youtube_session.grab_channel_playlists(
        parts=['snippet', 'contentDetails']
    )

    # Create a new file and save the playlists.
    new_json_file_path = youtube_session.save_to_json_file(
        file_name='channel_playlists',
        youtube_content=channel_playlists
    )

    # Print the message.
    message = "Playlist All Channel Playlists: {path}"
    print(message.format(path=new_json_file_path))

if GRAB_CHANNEL_PLAYLISTS_ITEMS:

    # Grab all the items for a particular playlist ID.
    playlist_items = youtube_session.playlists_items(
        playlist_id=playlist_id, all_pages=True
    )

    # Save the data to a JSON file.
    new_json_file_path = youtube_session.save_to_json_file(
        file_name='channel_playlists_items',
        youtube_content=playlist_items
    )

    # Print the message.
    message = "Playlist All Playlist Items Master File: {path}"
    print(message.format(path=new_json_file_path))

if GRAB_CHANNEL_PLAYLISTS_ITEMS_ALL:
    
    # Initialize the list to store all the data.
    all_playlist_items = []

    # Load the `channel_playlists_parsed` file.
    with open('data/channel_playlists_parsed.json', 'r') as channel_playlist_file:
        channel_playlists = json.load(fp=channel_playlist_file)
    
    # Grab all the Playlist IDs.
    playlist_ids = [playlist['playlist_id'] for playlist in channel_playlists]
    
    # Loop through each playlist ID.
    for playlist_id in playlist_ids:

        # Grab the playlist items.
        playlist_items = youtube_session.playlists_items(
            playlist_id=playlist_id,
            all_pages=True
        )

        # Add to the main list.
        all_playlist_items = all_playlist_items + playlist_items

    # Save the data to a JSON file.
    new_json_file_path = youtube_session.save_to_json_file(
        file_name='channel_playlists_items_all',
        youtube_content=all_playlist_items
    )

    # Print the message.
    message = "Playlist JSON File: {path}"
    print(message.format(path=new_json_file_path))

if GRAB_SPECIFIC_PLAYLIST:

    all_playlists = [
        'PLcFcktZ0wnNmdgAdv4-Yl_nzS5LiKnhnn'
    ]

    all_playlist_items = []

    # Loop through all playlists.
    for playlist_id in all_playlists:

        # Grab the playlist items.
        playlist_items = youtube_session.playlists_items(
            playlist_id=playlist_id,
            all_pages=True
        )

        # Add to the main list.
        all_playlist_items = all_playlist_items + playlist_items

    # Save the data to a JSON file.
    new_json_file_path = youtube_session.save_to_json_file(
        file_name='all_playlists_items',
        youtube_content=all_playlist_items,
        append=False
    )

    # Print the message.
    message = "Playlist Items JSON File: {path}"
    print(message.format(path=new_json_file_path))

# Grab and Parse if specified.
if GRAB_PLAYLISTS_ITEMS:

    # Initialize the list.
    all_playlist_items = []

    # Loop through each playlist.
    for playlist_dict in all_playlist_items:

        # Grab the items we need.
        playlist_id = playlist_dict['playlist_id']
        playlist_count = playlist_dict['playlist_item_count']

        if playlist_count != 0:

            # Grab the playlist items.
            playlist_items = youtube_session.playlists_items(
                playlist_id=playlist_id,
                all_pages=True
            )

            # Add to the list.
            all_playlist_items = all_playlist_items + playlist_items

    # Save the data to a JSON file.
    new_json_file_path = youtube_session.save_to_json_file(
        file_name='all_playlist_items',
        youtube_content=all_playlist_items,
        append=True
    )

    # Print the message.
    message = "Playlist Items JSON File: {path}"
    print(message.format(path=new_json_file_path))

# Grab and Parse if specified.
if PARSE_FILES:

    # Parse all the playlist items from the List.
    all_playlist_ids_parsed = youtube_session.parse_playlist_ids(
        playlist_json_path='data/channel_playlists.json'
    )

    # Parse all the playlist items from the List.
    all_playlist_items_parsed = youtube_session.parse_playlist_items(
        playlist_items_json_path='data/channel_playlists_items.json'
    )

    # Parse all the playlist items from the List.
    all_playlist_items_all_parsed = youtube_session.parse_playlist_items(
        playlist_items_json_path='data/channel_playlists_items_all.json'
    )

    # Save the data to a JSON file.
    playlist_parsed_path = youtube_session.save_to_json_file(
        file_name='channel_playlists_parsed',
        youtube_content=all_playlist_ids_parsed,
        append=False
    )

    # Save the data to a JSON file.
    playlist_items_parsed_path = youtube_session.save_to_json_file(
        file_name='channel_playlists_items_parsed',
        youtube_content=all_playlist_items_parsed,
        append=False
    )

    # Save the data to a JSON file.
    playlist_items_all_parsed_path = youtube_session.save_to_json_file(
        file_name='channel_playlists_items_all_parsed',
        youtube_content=all_playlist_items_all_parsed,
        append=False
    )

    # Print the message.
    message = """
    Playlist Parsed JSON File: {path_p}
    Playlist Items Parsed JSON File: {path_i}
    Playlist Items Parsed All JSON File: {path_a}
    """
    print(
        message.format(
            path_p=playlist_parsed_path,
            path_i=playlist_items_parsed_path,
            path_a=playlist_items_all_parsed_path
        )
    )
