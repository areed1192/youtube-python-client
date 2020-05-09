from configparser import ConfigParser

# Define your Config Parser.
config = ConfigParser()

# Define a Section.
config.add_section('main')

# Set your variables.
config.set('main', 'api_key', '')
config.set('main', 'channel_id', '')
config.set('main', 'playlist_id', '')
config.set('main', 'client_secret_path', '')
config.set('main', 'state_path', '')

# Write to the File
with open('samples/config_sample_output.ini', 'w+') as f:
    config.write(f)

# Read the File we just wrote.
config.read('samples/config_sample_output.ini')

# Get the Values.
api_key = config.get('main', 'api_key')
channel_id = config.get('main', 'channel_id')
playlist_id = config.get('main','playlist_id')
client_secret_path = config.get('main', 'client_secret_path')
state_path = config.get('main', 'state_path')