import json
import os
import pathlib
import urllib.parse

import requests

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaFileUpload

from typing import Dict
from typing import List
from typing import Union


class YouTubeClient():
    

    def __init__(self, api_key: str, channel_id: str, client_secret_path: str, state_path: str) -> None:    
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

        # API Services.
        self.API_URL = "https://www.googleapis.com"
        self.API_SERVICE = "youtube"
        self.API_VERSION = "v3"
        self.API_UPLOAD = "/upload/youtube"

        # Auth Endpoints.
        self.AUTH_URI = "https://accounts.google.com/o/oauth2/auth"
        self.AUTH_TOKEN_URI = "https://oauth2.googleapis.com/token"

        # self.CLIENT_SECRET_FILE = pathlib.Path(__file__).parent.parent.joinpath('configs/google_api_credentials.json').absolute()
        # self.YOUTUBE_STATE_FILE = pathlib.Path(__file__).parent.parent.joinpath('configs/youtube_state.json').absolute()

        self.CLIENT_SECRET_FILE = pathlib.Path(client_secret_path).absolute()
        self.YOUTUBE_STATE_FILE = pathlib.Path(state_path).absolute()
        self.DATA_FOLDER_PATH :pathlib.Path = pathlib.Path(__file__).parent.parent.joinpath('data')

        self.AUTHORIZATION_URL = None
        self.CREDENTIALS = self.oauth_workflow()

    def refresh_token(self) -> Credentials:
        """Refreshes the token before starting the new session.

        Returns:
        ----
        {dict{} -- Dictionary containing authentication protocol.
        """

        # create a new request transport.
        request = Request()

        # load the file.
        credentials = Credentials.from_authorized_user_file(filename=self.YOUTUBE_STATE_FILE)

        # refresh the token.
        credentials.refresh(request)

        return credentials

    def _validate_token(self) -> bool:
        """Validates a token, before making a request.

        If the token is not valid, it will attempt to refresh it
        using the `refresh_token()` method.

        Returns:
        ----
        {bool} -- `True` if the token is valid, `False` if it's not.
        """

        if self.CREDENTIALS.valid:
            return True
        else:
            self.refresh_token()
            return True
            
    def oauth_workflow(self) -> Union[Credentials, InstalledAppFlow]:
        """Handles oAuth workflow.

        Will authorize the session so that we can make requests to the YouTube API. 
        If a `state` file exists it will grab the state and attempt to do a silent 
        SSO by refreshing an expired token if it is expired.
        """

        # load the previous state if it exists and then refresh the token.
        if os.path.isfile(self.YOUTUBE_STATE_FILE):
            return self.refresh_token()
        else:
            # Initalize the flow workflow.
            flow = InstalledAppFlow.from_client_secrets_file(self.CLIENT_SECRET_FILE, ['https://www.googleapis.com/auth/youtube'])
            return  flow.run_console()

    def _headers(self, json: bool = False, images: bool = False) -> Dict:
        """Builds the headers for a requests.

        Arguments:
        ----
        json {bool} -- If `True` then changes the headers to send JSON content.

        images {bool} -- If `True` then preps the headers to send an image content.
    
        Returns:
        ----
        {Dict} -- A headers dictionary used in requests.
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
            headers['Accepted Media MIME types'] = 'image/png'

        return headers

    def _build_url(self, endpoint: str) -> str:
        """Builds a full url to a specified endpoint.

        Arguments:
        ----
        endpoint {str} -- The endpoint we wish to build a full URL for.

        Returns:
        ----
        {str} -- A full url path.
        """
        return urllib.parse.urljoin(base ='/'.join([self.API_URL, self.API_SERVICE, self.API_VERSION, '/']), url = endpoint)

    def _channel_sections(self) -> Dict:
        """Makes a request to the Channels Section endpoint."""

        url = self._build_url(endpoint = 'channelSections')

    def _load_playlists(self) -> Dict:
        """Loads a playlist file.

        Raises:
        ----
        FileNotFoundError: The content file does not exist, so must be created.

        Returns:
        ----
        {Dict} -- Playlist file content.
        """

        playlist_path = self.DATA_FOLDER_PATH.joinpath('playlists.json')

        # Load the JSON file if it exists.
        if playlist_path.exists():
            with open(playlist_path.absolute(), 'r') as file:
                return json.load(file)
        else:
            raise FileNotFoundError("Content doesn't exist")
    
    def _load_desc(self) -> Dict:
        """Loads description files used for videos.
        
        Loads the description JSON file so we can populate it 
        with the new values.

        Raises:
        ----
        FileNotFoundError: The content file does not exist, so must be created.

        Returns:
        ----
        {Dict} -- Description file content.
        """

        desc_path = self.DATA_FOLDER_PATH('descriptions/video_desc.json')

        # laod the previous state if it exists and then refresh the token.
        if desc_path.exists():
            with open(desc_path.absolute(), 'r') as file:
                return json.load(file)
        else:
            raise FileNotFoundError("Description templates do not exist.")

    def playlists_items(self, playlist_id: str, all_pages: bool = False) -> List[Dict]:      
        """Makes a request to the Playlist Items endpoint.

        Arguments:
        ----
        playlist_id {str} -- The ID of the playlist you wish to get items for.

        Keyword Arguments:
        ----
        all_pages {bool} -- Specifies the number of pages you want back if there are multiple pages.
            if set to -1 then returns all pages. (default: {False})

        Returns:
        ----
        {List[Dict]} - A list of playlist items.
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

            # Grab the response.
            playlist_response = requests.get(url=url, params=params, verify=True)
            
            if playlist_response.status_code == 200:
                playlist_data = playlist_response.json()

                master_list = []  
                master_list.append(playlist_data)

                if all_pages:
                    while 'nextPageToken' in playlist_data.keys():
                        params['pageToken'] = playlist_data['nextPageToken']

                        # add to master list.
                        playlist_data = requests.get(url=url, params=params, verify=True).json()
                        master_list.append(playlist_data)

                return master_list

    def update_video(self, part: List[str], data: dict) -> Dict:
        """Updates the specified part of a video using the YouTube API.

        Arguments:
        ----
        part {List[str]} -- The part of the video you wish to update.

        data {dict} -- The content you wish to set the part to.

        Returns:
        ----
        {Dict} -- The JSON content from the updated video.
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
        """Updates the specified part of a Playlist using the YouTube API.

        Arguments:
        ----
        part {List[str]} -- The part of the playlist you wish to update.

        data {dict} -- The content you wish to set the part to.

        Returns:
        ----
        {Dict} -- The JSON content from the updated playlist.
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
        """Inserts a new playlist to the Channel.

        Arguments:
        ----
        part {List[str]} -- The part of the video you wish to insert.

        data {dict} -- The content you wish to set the part to.

        Returns:
        ----
        {Dict} -- The JSON content from the newly inserted video.
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
        """Updates the specified part of a Playlist using the YouTube API.

        Arguments:
        ----
        part {List[str]} -- The part of the playlist items you wish to update.

        data {dict} -- The content you wish to set the part to.

        Returns:
        ----
        {Dict} -- The JSON content from the updated playlist items.
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
        """Deletes the specified item from the playlist.

        Arguments:
        ----
        playlist_item_id {str} -- The playlist item ID of the object
            you want to delete from the playlist.

        Returns:
        ----
        {Dict} -- Message specifying the result of delete operation.
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
        """Inserts the specified item from the playlist.

        Arguments:
        ----
        part {List[str]} -- The part of the video you wish to insert.

        data {dict} -- The content you wish to set the part to.


        Returns:
        ----
        {Dict} -- Message specifying the result of Insert operation.
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
        """Uploads the specified file to the specific video as a thumbnail.


        Arguments:
        ----
        video_id {str} -- The ID of the Video that will have the thumbnail added to it.

        thumbnail_path {str} -- The file path of the thumbnail image.


        Returns:
        ----
        {Dict} -- Message specifying the result of Insert operation.
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
        """Grabs a specified playlist.

        Arguments:
        ----
        playlist_id {str} -- A playlist ID you want to pull.

        part {List[str]} -- The part of the playlist you want to pull.

        Returns:
        ----
        {Dict} -- A Playlist resource objects.
        """
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

    def clear_playlist_items(self, playlist_id: str) -> None:
        """Deletes all the exisiting items for a Playlist.

        Arguments:
        ----
        playlist_id {str} -- The ID of the playlist you want to clear all 
            the items from.

        """
        
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

    def grab_playlists(self, parts:List[str], playlist_ids: List[str]) -> Dict:
        """Grabs all the playlists for the specified channel.

        Arguments:
        ----
        playlist_id {List[str]} -- A list of playlist IDs you want to pull.

        Returns:
        ----
        {Dict} -- A list of Playlist resource objects.
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
        """Grabs all the specified videos and parts requested

        Arguments:
        ----
        video_id {str} -- A video ID you want to pull.

        part {List[str]} -- The parts of the video you wish to pull.

        Returns:
        ----
        {Dict} -- A list of Video resource objects.
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