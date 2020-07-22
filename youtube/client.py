
import os
import json
import pathlib
import requests
import urllib.parse

from typing import Dict
from typing import List
from typing import Union
from typing import Tuple

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaFileUpload


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
                channel_id='<CHANNEL_ID>',
                client_secret_path='<CLIENT_SECRET_PATH>',
                state_path='<STATE_PATH>'
            )
        """

        # Define Channel Specific Items.
        self.api_key = api_key
        self.channel_id = channel_id

        # API Services.
        self.api_url = "https://www.googleapis.com"
        self.api_service = "youtube"
        self.api_version = "v3"
        self.api_upload = "/upload/youtube"

        # Session properties.
        self.client_secret_file = pathlib.Path(client_secret_path).absolute()
        self.youtube_state_file = pathlib.Path(state_path).absolute()
        self.data_folder_path: pathlib.Path = pathlib.Path(__file__).parents[1].joinpath('data')
        self.credentials = self.oauth_workflow()

        # If we don't have a state file, then create it.
        if self.youtube_state_file.exists() == False:
            self._save_state()

    def _save_state(self) -> Dict:
        """Saves the Credential State.

        Returns:
        ----
        Dict -- A dictionary containing state info.
        """

        # Define the state dict.
        state_dict = {
            'client_id': self.credentials.client_id,
            'client_secret': self.credentials.client_secret,
            'refresh_token': self.credentials.refresh_token
        }

        # Open the JSON file and save it.
        with open(self.youtube_state_file, 'w+') as state_file:
            json.dump(obj=state_dict, fp=state_file)

        return state_dict

    def refresh_token(self) -> Credentials:
        """Refreshes the token before starting the new session.

        Returns:
        ----
        (Credentials) -- Dictionary containing authentication protocol.
        """

        # create a new request transport.
        request = Request()

        # load the file.
        credentials = Credentials.from_authorized_user_file(
            filename=self.youtube_state_file
        )

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

        if self.credentials.valid:
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
        if self.youtube_state_file.exists():
            return self.refresh_token()

        # Otherwise grab the Client Secret file.
        elif self.client_secret_file.exists():

            # Initalize the flow workflow.
            flow = InstalledAppFlow.from_client_secrets_file(
                self.client_secret_file,
                ['https://www.googleapis.com/auth/youtube']
            )
            return flow.run_console()

        else:
            raise FileNotFoundError(
                "Client Secret File Does Not Exist, please check your path.")

    def _headers(self, mode: str = 'json') -> Dict:
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
            'Authorization': 'Bearer {}'.format(self.credentials.token)
        }

        # add content type if needed.
        if mode == 'json':
            headers['Accept'] = 'application/json'
            headers['Content-Type'] = 'application/json'

        if mode == 'image':
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

        # Define the parts.
        parts = [self.api_url, self.api_service, self.api_version, '/']

        # Build the URL.
        return urllib.parse.urljoin(
            base='/'.join(parts),
            url=endpoint
        )

    def _make_request(self, endpoint: str, method: str, headers: str = 'json', params: dict = None, json: dict = None, data: dict = None) -> List[Dict]:
        """Used to make a request for each of the news clients.

        Arguments:
        ----
        endpoint (str): The endpoint to build the URL.

        method (str): The Request method, can be one of the
            following: ['get','post','put','delete','patch'].

        mode (str): The content-type mode, can be one of the
            following: ['form','json'].

        params (dict): The URL params for the request.

        json (dict): A json data payload for a request.

        data (dict): A data payload for a request.

        Returns:
        ----
        List[Dict]: A list of news items objects.
        """

        # First validate the token before making the request.
        if not self._validate_token():
            return {
                'token': 'Expired or invalid.'
            }

        # Build the URL.
        url = self._build_url(endpoint=endpoint)

        # Grab the headers.
        headers = self._headers(mode=headers)

        # Define a new session.
        new_session = requests.Session()
        new_session.verify = True

        # Prepare the request.
        new_request = requests.Request(
            method=method.upper(),
            headers=headers,
            params=params,
            data=data,
            json=json,
            url=url
        ).prepare()

        # Send the request.
        response: requests.Response = new_session.send(
            request=new_request
        )

        # If it was okay return the data.
        if response.ok:
            return response.json()
        else:
            print('Invalid Request')
            return response.json()

    def _load_playlists(self) -> Dict:
        """Loads a playlist file.

        Raises:
        ----
        FileNotFoundError: The content file does not exist, so must be created.

        Returns:
        ----
        {Dict} -- Playlist file content.
        """

        playlist_path = self.data_folder_path.joinpath('playlists.json')

        # Load the JSON file if it exists.
        if playlist_path.exists():
            with open(playlist_path.absolute(), 'r') as file:
                return json.load(file)
        else:
            raise FileNotFoundError("Playlist content file doesn't exist.")

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

        desc_path = self.data_folder_path.joinpath(
            'descriptions/video_desc.json'
        )

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

        # Initialize the list to store the data.
        master_list = []

        # Define the params.
        params = {
            'part': 'contentDetails,id,snippet,status',
            'playlistId': playlist_id,
            'maxResults': 50,
            'key': self.api_key
        }

        # Define the endpoint.
        endpoint = 'playlistItems'

        # Grab the data.
        playlist_data = self._make_request(
            endpoint=endpoint,
            method='get',
            headers='json',
            params=params
        )

        # Add it to the list.
        master_list.append(playlist_data)

        # Print the ID.
        print('Pulling Playlist ID: {playlist_id}'.format(
            playlist_id=playlist_id
        )
        )

        # If they want all pages then keep going while there is a `nextPage`.
        if all_pages:

            while 'nextPageToken' in playlist_data:

                # Print the message for the User to see.
                print('''
                Pulling Playlist ID: {playlist_id}
                Pulling Page: {url}
                '''.format(
                    playlist_id=playlist_id,
                    url=playlist_data['nextPageToken'])
                )

                # Add the next page token.
                params['pageToken'] = playlist_data['nextPageToken']

                # Grab the data.
                playlist_data = self._make_request(
                    endpoint=endpoint,
                    method='get',
                    headers='json',
                    params=params
                )
                # Add the data.
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

        # Define the arguments.
        params = {
            'key': self.api_key,
            'part': ','.join(part)
        }

        # Define the endpoint.
        endpoint = 'videos'

        # Grab the data.
        update_video_data = self._make_request(
            endpoint=endpoint,
            params=params,
            method='put',
            headers='json',
            json=data
        )

        return update_video_data

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

        # Define the arguments.
        params = {
            'key': self.api_key,
            'part': ','.join(part)
        }

        # Define the endpoint.
        endpoint = 'playlists'

        # Grab the data.
        update_playlist_data = self._make_request(
            endpoint=endpoint,
            params=params,
            method='put',
            headers='json',
            json=data
        )

        return update_playlist_data

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

        # Define the arguments.
        params = {
            'key': self.api_key,
            'part': ','.join(part)
        }

        # Define the endpoint.
        endpoint = 'playlists'

        # Grab the data.
        response = self._make_request(
            endpoint=endpoint,
            method='post',
            headers='json',
            params=params,
            json=data
        )

        return response

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

        # Define the arguments.
        params = {
            'key': self.api_key,
            'part': ','.join(part)
        }

        # Define the endpoint.
        endpoint = 'playlistItems'

        # Grab the data.
        response = self._make_request(
            endpoint=endpoint,
            method='put',
            headers='json',
            params=params,
            json=data
        )

        return response

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

        # Define the arguments.
        params = {
            'key': self.api_key,
            'id': playlist_item_id
        }

        # Define the endpoint.
        endpoint = 'playlistItems'

        # Grab the data.
        response = self._make_request(
            endpoint=endpoint,
            method='delete',
            headers='json',
            params=params
        )

        return response

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

        # Define the arguments.
        params = {
            'key': self.api_key,
            'part': ','.join(part)
        }

        # Define the endpoint.
        endpoint = 'playlistItems'

        # Grab the data.
        response = self._make_request(
            endpoint=endpoint,
            method='delete',
            headers='json',
            params=params,
            json=data
        )

        return response

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
            url = self._build_url(endpoint='thumbnails/set')

            # Define video parameters.
            params = {
                'videoId': video_id,
                'key': self.api_key
            }

            # define the file media content.
            files = {
                'media': open(thumbnail_path, 'rb')
            }

            # Defin the headers.
            headers = self._headers(mode='image')

            # Define the URL.
            url = "https://www.googleapis.com/upload/youtube/v3/thumbnails/set"

            # Upload the Media
            response = requests.post(
                url=url,
                headers=headers,
                files=files,
                params=params
            ).json()

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

        # Define the arguments.
        params = {
            'key': self.api_key,
            'maxResults': 50,
            'id': playlist_id,
            'part': parts
        }

        # Define the endpoint.
        endpoint = 'playlists'

        # Grab the data.
        response = self._make_request(
            endpoint=endpoint,
            method='get',
            headers='json',
            params=params
        )

        return response

    def clear_playlist_items(self, playlist_id: str) -> None:
        """Deletes all the exisiting items for a Playlist.

        Arguments:
        ----
        playlist_id {str} -- The ID of the playlist you want to clear all 
            the items from.
        """

        # Grab all the items for a particular playlist.
        playlist_items = self.playlists_items(playlist_id=playlist_id)

        # Loop through each page in the playlist.
        for playlists_item_response in playlist_items:

            # Loop through each video in the playlist.
            for playlist_item in playlists_item_response['items']:

                # Grab the ID
                playlist_item_id = playlist_item['id']

                # Remove it from the playlist.
                self.delete_playlist_items(playlist_item_id=playlist_item_id)

    def grab_playlists(self, parts: List[str], playlist_ids: List[str]) -> Dict:
        """Grabs all the playlists for the specified channel.

        Arguments:
        ----
        part {List[str]} -- The part of the playlist you want to pull.

        playlist_id {List[str]} -- A list of playlist IDs you want to pull.

        Returns:
        ----
        {Dict} -- A list of Playlist resource objects.
        """

        # Master list.
        playlists_list = []

        # Define the arguments.
        params = {
            'mine': True,
            'key': self.api_key,
            'maxResults': 50,
            'part': parts
        }

        # Define the endpoint.
        endpoint = 'playlists'

        # Grab the data.
        data = self._make_request(
            endpoint=endpoint,
            method='get',
            headers='json',
            params=params
        )

        # Add it to the list.
        playlists_list.append(data)

        # Keep going while we have a key.
        while 'nextPageToken' in data.keys():

            # Add the next page.
            params['pageToken'] = data['nextPageToken']

            # Grab the data.
            data = self._make_request(
                endpoint=endpoint,
                method='get',
                headers='json',
                params=params
            )

            # Add it to the list.
            playlists_list.append(data)

        return playlists_list

    def grab_channel_playlists(self, parts: List[str]) -> Dict:
        """Grabs all the playlists for the specified channel.

        Arguments:
        ----
        part {List[str]} -- The part of the playlist you want to pull.

        Returns:
        ----
        {Dict} -- A list of Playlist resource objects.
        """

        # Master list.
        playlists_list = []

        # Define the arguments.
        params = {
            'mine': True,
            'key': self.api_key,
            'maxResults': 50,
            'part': parts
        }

        # Define the endpoint.
        endpoint = 'playlists'

        # Grab the data.
        data = self._make_request(
            endpoint=endpoint,
            method='get',
            headers='json',
            params=params
        )

        # Add it to the list.
        playlists_list.append(data)

        # Keep going while we have a key.
        while 'nextPageToken' in data.keys():

            # Add the next page.
            params['pageToken'] = data['nextPageToken']

            # Grab the data.
            data = self._make_request(
                endpoint=endpoint,
                method='get',
                headers='json',
                params=params
            )

            # Add it to the list.
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

        # Initialize a list to store the Video IDs.
        video_ids_list = []

        # Define the arguments.
        params = {
            'part': ','.join(parts),
            'id': ','.join(video_id),
            'maxResults': 50,
            'key': self.api_key
        }

        # Define the endpoint.
        endpoint = 'videos'

        # Grab the data.
        data = self._make_request(
            endpoint=endpoint,
            method='get',
            headers='json',
            params=params
        )

        # Add it to the list.
        video_ids_list.append(data)

        # Keep going while we have a key.
        while 'nextPageToken' in data.keys():

            # Add the next page.
            params['pageToken'] = data['nextPageToken']

            # Grab the data.
            data = self._make_request(
                endpoint=endpoint,
                method='get',
                headers='json',
                params=params
            )

            # Add it to the list.
            video_ids_list.append(data)

        return video_ids_list

    def parse_playlist_ids(self, playlist_json_path: str) -> List[Dict]:
        """Simplifies the Playlist Objects to a more simplified object.

        Arguments:
        ----
        playlist_json_path (str): The path to the JSON file.

        Returns:
        ----
        List[Dict]: A list of playlist objects.
        """

        # Initial the playlist list.
        playlists = []

        # Open the file.
        with open(playlist_json_path, 'r') as playlist_json_file:
            playlists_resources = json.load(fp=playlist_json_file)

        # Loop through each playlist.
        for playlist_resource in playlists_resources:

            # Then each Item.
            for playlist in playlist_resource['items']:

                # Grab the items we want.
                playlist_id = playlist['id']
                playlist_title = playlist['snippet']['title']
                playlist_item_count = playlist['contentDetails']['itemCount']

                # Assign it.
                playlist_dict = {
                    'playlist_id': playlist_id,
                    'playlist_title': playlist_title,
                    'playlist_item_count': playlist_item_count
                }

                # Store it.
                playlists.append(playlist_dict)

        return playlists

    def parse_playlist_items(self, playlist_items_json_path: str) -> List[Dict]:
        """Simplifies the PlaylistItem Objects to a more simplified object.

        Arguments:
        ----
        playlist_items_json_path (str): The path to the JSON file.

        Returns:
        ----
        List[Dict]: A list of playlist item objects.
        """

        # Initialize the list.
        playlists_items = []

        # Open the file.
        with open(playlist_items_json_path, 'r') as playlist_json_file:
            playlists = json.load(fp=playlist_json_file)

        # Loop through each playlist.
        for playlist_resource in playlists:

            # Then each video.
            for playlist in playlist_resource['items']:

                # Grab the items we want.
                playlist_item_id = playlist['id']
                playlist_item_title = playlist['snippet']['title']
                playlist_item_position = playlist['snippet']['position']
                playlist_item_playlist_id = playlist['snippet']['playlistId']
                playlist_item_publish_time = playlist['snippet']['publishedAt']
                playlist_item_video_id = playlist['snippet']['resourceId']['videoId']

                # Assign it.
                playlist_item_dict = {
                    'playlist_item_id': playlist_item_id,
                    'playlist_item_title': playlist_item_title,
                    'playlist_item_position': playlist_item_position,
                    'playlist_item_publish_time': playlist_item_publish_time,
                    'playlist_item_video_id': playlist_item_video_id,
                    'playlist_item_playlist_id': playlist_item_playlist_id
                }

                # Store it.
                playlists_items.append(playlist_item_dict)

        return playlists_items

    def save_to_json_file(self, file_name: str, youtube_content: dict, append: bool = False) -> str:
        """Saves the content to a JSON file in the Data Folder.

        Arguments:
        ----
        file_name {str} -- The name of your JSON file.

        youtube_content {dict} -- A youtube API JSON response.

        append {bool} -- If `True` will merge the original file with the new content. `False` will
            overwrite the existing file.

        Returns:
        ----
        str -- The file path of the new file.
        """

        # Create a Path object.
        file_path = self.data_folder_path.joinpath(
            '{file_name}.json'.format(file_name=file_name)
        )

        # Open the JSON file and save it
        if not append:
            with open(file_path, 'w+') as content_file:
                json.dump(obj=youtube_content, fp=content_file, indent=2)

        # If in append mode, merge the two files.
        else:
            with open(file_path, 'r') as content_file:
                content = json.load(fp=content_file)
                youtube_content = youtube_content + content

            with open(file_path, 'w+') as content_file:
                json.dump(obj=youtube_content, fp=content_file, indent=2)

        return file_path.resolve()
