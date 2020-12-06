import re
import json
import textwrap
from pprint import pprint
from configparser import ConfigParser
from youtube.client import YouTubeClient
from youtube.adobe import AdobeIllustrator

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

# Grab my channel subscriber data.
my_channel_data = youtube_session.grab_my_channel(
    parts=['snippet', 'contentDetails', 'statistics']
)

# Grab the current subscriber count.
current_subscriber_count = int(
    my_channel_data['items'][0]['statistics']['subscriberCount'])

# Set the Text
current_subscriber_text = "{curr_subs} SO FAR !!!".format(
    curr_subs='{:,}'.format(current_subscriber_count)
)

# Create a new AdobeIllustrator Client.
adobe_illustrator = AdobeIllustrator(
    file_name='thumbnail_help_me_grow.ai'
)

# Set the Text for Goal Subscriber Text.
adobe_illustrator.set_goal_subscriber_text(
    text=textwrap.dedent(
        """HELP MY CHANNEL GROW TO\n100,000 SUBSCRIBERS !!!"""
    )
)

# Set the Text for Current Subscriber Text.
adobe_illustrator.set_current_subscriber_text(
    text=current_subscriber_text
)

# Grab the Text Range for Current Subscribers.
current_text_range = adobe_illustrator.get_current_subscriber_text_range()

# Grab the Text Range for Goal Subscribers.
goal_text_range = adobe_illustrator.get_goal_subscriber_text_range()

# Make sure the last 10 characters are White.
for character in list(current_text_range.Characters)[-10:]:
    character.CharacterAttributes.FillColor = adobe_illustrator.foreground_white

# Make sure everything else is Pink.
for character in list(current_text_range.Characters)[:-10]:
    character.CharacterAttributes.FillColor = adobe_illustrator.high_contrast_pink

# Search for the Text we want to change colors.
location = re.search(
    pattern="100,000",
    string=goal_text_range.Contents
).span()

# Make sure everything else is Green.
for character in list(goal_text_range.Characters)[location[0]:location[1]]:
    character.CharacterAttributes.FillColor = adobe_illustrator.high_contrast_green

# Export the artboard to a PNG.
adobe_illustrator.export_to_png(
    file_name='current_thumbnail'
)

# Update the thumbnail.
youtube_session.upload_thumbnail(
    video_id='XEjaDFqImCk',
    thumbnail_path='thumbnails/current_thumbnail.png'
)
