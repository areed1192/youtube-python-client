import json
import os
import pathlib
import urllib.parse

import requests
import google.auth.transport.requests
import google.oauth2.credentials
import google_auth_oauthlib.flow
from googleapiclient.http import MediaFileUpload

from typing import Dict
from typing import List


class YouTubeClient():
    

    def __init__(self, api_key: str, channel_id: str) -> None:    
        """Initalizes a new instance of the YouTube Client Manager.
        
        Arguments:
        ----
        api_key {str} -- Your YouTube API key issued from the Google Developer
            console.
            
        channel_id {str} -- Your YouTube Channel Id.

        Usage:
        ----
            >>> youtube_session(
                api_key='<API_KEY>',
                channel_id='<CHANNEL_ID>'
            )
        """
        
        # Define Channel Specific Items.
        self.API_KEY = api_key
        self.CHANNEL_ID = channel_id
        self.UPLOADS_PLAYLIST = 'UUBsTB02yO0QGwtlfiv5m25Q'

        self.API_URL = "https://www.googleapis.com"
        self.API_SERVICE = "youtube"
        self.API_VERSION = "v3"
        self.API_UPLOAD = "/upload/youtube"

        self.AUTH_URI = "https://accounts.google.com/o/oauth2/auth"
        self.AUTH_TOKEN_URI = "https://oauth2.googleapis.com/token"

        self.CLIENT_SECRET_FILE = pathlib.Path(__file__).parent.joinpath('credentials/google_api_credentials.json').absolute()
        self.YOUTUBE_STATE_FILE = pathlib.Path(__file__).parent.joinpath('credentials/youtube_state.json').absolute()
        self.AUTHORIZATION_URL = None
        self.CREDENTIALS = self.oauth_workflow()

    def refresh_token(self) -> google.oauth2.credentials.Credentials:
        """Refreshes the token before starting the new session.

        Returns:
        ----
        dict -- Dictionary containing authentication protocol.
        """

        # create a new request transport.
        request = google.auth.transport.requests.Request()

        # load the file.
        credentials = google.oauth2.credentials.Credentials.from_authorized_user_file(filename = self.YOUTUBE_STATE_FILE)

        # refresh the token.
        credentials.refresh(request)

        return credentials

    def _validate_token(self) -> bool:
        """Validates a token, before making a request.

        If the token is not valid, it will attempt to refresh it
        using the `refresh_token()` method.

        Returns:
        ----
        bool -- `True` if the token is valid, `False` if it's not.
        """

        if self.CREDENTIALS.valid:
            return True
        else:
            self.refresh_token()
            return True
            
    def oauth_workflow(self) -> None:
        """

        Will authorize the session so that we can make requests to the YouTube API. 
        If a `state` file exists it will grab the state and attempt to do a silent 
        SSO by refreshing an expired token if it is expired.
        """

        # load the previous state if it exists and then refresh the token.
        if os.path.isfile(self.YOUTUBE_STATE_FILE):
            return self.refresh_token()
        else:
            # Initalize the flow workflow.
            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(self.CLIENT_SECRET_FILE, ['https://www.googleapis.com/auth/youtube'])
            return  flow.run_console()

    def _headers(self, json: bool = False, images: bool = False) -> Dict:
        """
            Builds the headers for a requests.

            NAME: json
            DESC: If true then changes the content type of the request.
            TYPE: Boolean

            RTYPE: Dictionary
        """

        # initalize the headers.
        headers = {
            'Authorization':'Bearer {}'.format(self.CREDENTIALS.token)
        }

        # add content type if needed.
        if json == True:
            headers['Accept'] = 'application/json'
            headers['Content-Type'] = 'application/json'
        
        if images == True:

            # headers['Accept'] = 'image/png'
            headers['Accepted Media MIME types'] = 'image/png'

        return headers

    def _build_url(self, endpoint: str) -> str:
        """
            Builds a full url to a specified endpoint.

            NAME: endpoint
            DESC: The endpoint we wish to build a full URL for.
            TYPE: String

            RTYPE: String
        """
        return urllib.parse.urljoin(base ='/'.join([self.API_URL, self.API_SERVICE, self.API_VERSION, '/']), url = endpoint)

    def channel_sections(self):
        """
            Makes a request to the Channels Section endpoint.
        """

        url = self._build_url(endpoint = 'channelSections')

    def _load_playlists(self):

        playlist_path = pathlib.Path(__file__).parent.joinpath('data/youtube/playlists.json').absolute()

        # laod the previous state if it exists and then refresh the token.
        if os.path.isfile(playlist_path):
            with open(playlist_path, 'r') as file:
                playlists_content = json.load(file)
                return playlists_content
        else:
            raise ValueError("Content doesn't exist")

    
    def _load_desc(self):
        """
            Loads the description JSON file so we can populate it with the new values.

            RTYPE: Dictionary.
        """

        desc_path = pathlib.Path(__file__).parent.joinpath('templates/video_desc.json').absolute()

        # laod the previous state if it exists and then refresh the token.
        if os.path.isfile(desc_path):
            with open(desc_path, 'r') as file:
                video_desc = json.load(file)
                return video_desc
        else:
            raise ValueError("Content doesn't exist")

    def playlists_items(self, playlist_id: str, pages = -1):
        """
            Makes a request to the Playlist Items endpoint.

            NAME: playlist_id
            DESC: The ID of the playlist you wish to get items for.
            TYPE: String

            NAME: all
            DESC: Specifies the number of pages you want back if there are multiple pages.
                  if set to -1 then returns all pages.
            TYPE: Integer

            RTYPE: List
        """

        # validate the token.
        if self._validate_token():

            # define the url
            url = self._build_url(endpoint = 'playlistItems')

            # define the arguments
            params = {
                'part':'contentDetails,id,snippet,status',
                'playlistId':playlist_id,
                'maxResults':50,
                'key':self.API_KEY
            }

            playlist_data = requests.get(url = url, params = params, verify = True).json()         
            master_list = []  
            master_list.append(playlist_data)

            if pages == -1:
                while 'nextPageToken' in playlist_data.keys():
                    params['pageToken'] = playlist_data['nextPageToken']

                    # add to master list.
                    playlist_data = requests.get(url = url, params = params, verify = True).json()
                    master_list.append(playlist_data)

            return master_list

    def update_video(self, part: List[str], data: dict) -> Dict:
        """
            Updates the specified part of a video using the YouTube API.

            NAME: part
            DESC: The part of the video you wish to update.
            TYPE: Dictionary

            NAME: data
            DESC: The content you wish to set the part to.
            TYPE: Dicitonary

            RTYPE: Dictionary
        """

        # validate the token.
        if self._validate_token():

            # define the url
            url = self._build_url(endpoint = 'videos')

            # Redfine arguments.
            params = {'key':self.API_KEY, 'part':",".join(part)}
            headers = self._headers(json = True)
            response = requests.put(url = url, params = params, headers = headers, data = json.dumps(data), verify = True)

            if response.status_code == 200:
                return response.json()
            else:
                print("Error Updating the Video.")
                print(response.json())
                return response.json()

    def update_playlist(self, part: List[str], data: dict) -> Dict:
        """
            Updates the specified part of a Playlist using the YouTube API.

            NAME: part
            DESC: The part of the video you wish to update.
            TYPE: Dictionary

            NAME: data
            DESC: The content you wish to set the part to.
            TYPE: Dicitonary

            RTYPE: Dictionary
        """

        # validate the token.
        if self._validate_token():

            # define the url
            url = self._build_url(endpoint = 'playlists')

            # Redfine arguments.
            params = {
                'key':self.API_KEY, 
                'part':",".join(part)
            }

            headers = self._headers(json=True)

            response = requests.put(url = url, params = params, headers = headers, data = json.dumps(data), verify = True)

            if response.status_code == 200:
                return response.json()
            else:
                print("Error Updating the Video.")
                print(response.json())
                return response.json()

    def insert_playlist(self, part: List[str], data: dict) -> Dict:
        """
            Inserts a new playlist to the Channel.

            NAME: part
            DESC: The part of the video you wish to update.
            TYPE: Dictionary

            NAME: data
            DESC: The content you wish to set the part to.
            TYPE: Dicitonary

            RTYPE: Dictionary
        """

        # validate the token.
        if self._validate_token():

            # define the url
            url = self._build_url(endpoint = 'playlists')

            # Redfine arguments.
            params = {
                'key':self.API_KEY,
                'part':",".join(part)
            }
            
            # Define the headers.
            headers = self._headers(json = True)

            # Insert the new playlist
            response = requests.post(url = url, params = params, headers = headers, json = data, verify = True)

            if response.status_code == 200:
                return response.json()
            else:
                print("Error Creating New Playlist.")
                return response.json()


    def update_playlist_items(self, part: List[str], data: dict) -> Dict:
        """
            Updates the specified part of a Playlist using the YouTube API.

            NAME: part
            DESC: The part of the video you wish to update.
            TYPE: Dictionary

            NAME: data
            DESC: The content you wish to set the part to.
            TYPE: Dicitonary

            RTYPE: Dictionary
        """

        # validate the token.
        if self._validate_token():

            # define the url
            url = self._build_url(endpoint = 'playlistItems')

            # Redfine arguments.
            params = {'key':self.API_KEY, 'part':",".join(part)}
            headers = self._headers(json = True)
            response = requests.put(url = url, params = params, headers = headers, data = json.dumps(data), verify = True)

            if response.status_code == 200:
                return response.json()
            else:
                print("Error Updating the Video.")
                return response.json()

    def delete_playlist_items(self, playlist_item_id: str) -> Dict:
        """
            Deletes the specified item from the playlist.

            NAME: playlist_item_id
            DESC: The ID of the playlist item you want to delete.
            TYPE: String

            RTYPE: Dictionary.
        """

        # validate the token.
        if self._validate_token():

            # define the url
            url = self._build_url(endpoint = 'playlistItems')

            # Redfine arguments.
            params = {
                'key':self.API_KEY,
                'id':playlist_item_id
            }
            
            # Define the headers.
            headers = self._headers(json = True)

            # Delete the playlist item.
            response = requests.delete(url = url, params = params, headers = headers, verify = True)

            if response.status_code == 204:
                print("playlist item successfully deleted.")
                return {"message":"playlist item successfully deleted."}
            else:
                print("Error deleting the playlist item.")
                return response.json()

    def insert_playlist_items(self, part: List[str], data: dict) -> Dict:
        """
            Inserts the specified item from the playlist.

            NAME: playlist_item_id
            DESC: The ID of the playlist item you want to Insert.
            TYPE: String

            RTYPE: Dictionary
        """

        # validate the token.
        if self._validate_token():

            # define the url
            url = self._build_url(endpoint = 'playlistItems')

            # Redfine arguments.
            params = {
                'key':self.API_KEY,
                'part':",".join(part)
            }
            
            # Define the headers.
            headers = self._headers(json = True)

            # Delete the playlist item.
            response = requests.post(url = url, params = params, headers = headers, data = json.dumps(data), verify = True)

            if response.status_code == 200:
                return response.json()
            else:
                print("Error Inserting the Playlist Item.")
                return response.json()

    def upload_thumbnail(self, video_id: str, thumbnail_path: str) -> Dict:
        """
            Uploads the specified file to the specific video as a thumbnail.

            NAME: video_id
            DESC: The ID of the Video that will have the thumbnail added to it.
            TYPE: String

            NAME: thumbnail_path
            DESC: The file path of the thumbnail image.
            TYPE: String

            RTYPE: Dictionary

        """
        
        # validate the token.
        if self._validate_token():

            # define the url
            url = self._build_url(endpoint = 'thumbnails/set')

            # Define video parameters.
            params = {
                'videoId': video_id,
                'key':self.API_KEY
            }
            
            # define the file media content.
            files = {
                'media': open(thumbnail_path, 'rb')
            }

            # Defin the headers.
            headers = self._headers(images = True)

            # Define the URL.
            url = "https://www.googleapis.com/upload/youtube/v3/thumbnails/set"

            # Upload the Media
            response = requests.post(url = url, headers = headers, files = files, params = params).json()
            
            return response

    def grab_playlist(self, parts: List[str], playlist_id: str) -> Dict:

        # validate the token.
        if self._validate_token():

            # define the url
            url = self._build_url(endpoint = 'playlists')

            if isinstance(parts, list):
                parts = ','.join(parts)

            # define the parameters
            params = {
                'key':self.API_KEY,
                'maxResults':50,
                'id':playlist_id,
                'part':parts
            }

            # Define the headers
            headers = self._headers()

            # make the request
            playlist_response = requests.get(url = url, params = params, headers = headers, verify = True)

            if playlist_response.status_code == 200:
                return playlist_response.json()
            else:
                print("COULD NOT PULL PLAYLIST.")
                return playlist_response.json()

    def clear_playlist_items(self, playlist_id: str) -> Dict:
        '''
            Deletes all the exisiting items for a Playlist.

            NAME: playlist_id
            DESC: The ID of the playlist you want to clear all the items from.
            TYPE: String

            RTYPE: Boolean
        '''
        
        # Grab all the items for a particular playlist.
        playlist_items = self.playlists_items(playlist_id= playlist_id)

        # Loop through each page in the playlist.
        for playlists_item_response in playlist_items:

            # Loop through each video in the playlist.
            for playlist_item in playlists_item_response['items']:
                
                # Grab the ID
                playlist_item_id = playlist_item['id']

                # Remove it from the playlist.
                self.delete_playlist_items(playlist_item_id = playlist_item_id)

    def grab_playlists(self, parts: List[str]) -> Dict:
        """
            Grabs all the playlists for the specified channel.

            NAME: parts
            DESC: The parts of the playlist that you want returned.
            TYPE: List

            RTYPE: Dictionary
        """

        # Master list.
        playlists_list = []

        # validate the token.
        if self._validate_token():

            # define the url
            url = self._build_url(endpoint = 'playlists')

            if isinstance(parts, list):
                parts = ','.join(parts)

            # define the parameters
            params = {
                'mine': True,
                'key':self.API_KEY,
                'maxResults':50,
                'part':parts
            }

            # Define the headers
            headers = self._headers()

            # make the request
            playlist_response = requests.get(url = url, params = params, headers = headers, verify = True)

            # keep going if it was successful.
            if playlist_response.status_code == 200:

                # add the data
                data = playlist_response.json()
                playlists_list.append(data)
                total_results = data['pageInfo']['totalResults']

                while 'nextPageToken' in data.keys():
                    params['pageToken'] = data['nextPageToken']

                    # add to master list.
                    video_response = requests.get(url = url, params = params, verify = True).json()

                    # add the data.
                    if video_response.status_code == 200:
                        data = video_response.json()
                        playlists_list.append(data)

                return playlists_list


    def grab_videos(self, video_id: str, parts: List[str]) -> Dict:
        """
            Grabs all the specified videos and parts requested

            NAME: video_id
            DESC: A list of video IDs you wish to pull.
            TYPE: List

            NAME: parts
            DESC: The parts of the video you wish to pull.
            TYPE: List
        """

        video_ids_list = []

        if self._validate_token():

            # define the url
            url = self._build_url(endpoint = 'videos')
            headers = self._headers()

            # build the ids list
            if isinstance(video_id, list):
                video_ids = ','.join(video_id)
            
            if isinstance(parts, list):
                parts = ','.join(parts)

            # define arguments.
            params = {'part':parts,
                      'id':video_ids,
                      'maxResults':50,
                      'key':self.API_KEY}

            # make the request
            video_response = requests.get(url = url, params = params, headers = headers, verify = True)

            if video_response.status_code == 200:
                
                # add the data
                data = video_response.json()
                video_ids_list.append(data)
                total_results = data['pageInfo']['totalResults']

                while 'nextPageToken' in data.keys():
                    params['pageToken'] = data['nextPageToken']

                    # add to master list.
                    video_response = requests.get(url = url, params = params, verify = True).json()

                    # add the data.
                    if video_response.status_code == 200:
                        data = video_response.json()
                        video_ids_list.append(data)

                return video_ids_list