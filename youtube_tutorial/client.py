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
        """Initialize the client.

        Arguments:
        ----
        api_key {str} -- [description]

        channel_id {str} -- [description]

        client_secret_path {str} -- [description]

        state_path {str} -- [description]

        Usage:
        ----
            >>> youtube_session(
                api_key='<API_KEY>',
                channel_id='<CHANNEL_ID>'
            )
        """ 

        # Define the Channel Specific Data.
        self.api_key = api_key
        self.channel_id = channel_id

        # API Services
        self.api_url = "https://www.googleapis.com"
        self.api_service = "youtube"
        self.api_version = "v3"
        self.api_upload = "/upload/youtube"

        # Session Properites
        self.client_secret_file = pathlib.Path(client_secret_path).absolute()
        self.youtube_state_file = pathlib.Path(state_path).absolute()
        self.data_folder_path: pathlib.Path = pathlib.Path(__file__).parent.parent.joinpath('data')
        self.credentials: Credentials = self.oauth_workflow()

        # Save the state
        if self.youtube_state_file.exists() == False:
            self._save_sate()

    def _save_sate(self) -> Dict:
        
        state_dict = {
            'client_id':self.credentials.client_id,
            'client_secret': self.credentials.client_secret,
            'refresh_token': self.credentials.refresh_token
        }

        # Open the State File and Save the State
        with open(self.youtube_state_file, 'w+') as state_file:
            json.dump(obj=state_dict, fp=state_file)
        
        return state_dict

    def oauth_workflow(self) -> Union[Credentials, InstalledAppFlow]:
        
        # If the state file exists, try and refresh the token.
        if self.youtube_state_file.exists():
            return self.refresh_token()
        
        # If there is no state file, then check to see if there is a Client Secret File.
        elif self.client_secret_file.exists():

            flow = InstalledAppFlow.from_client_secrets_file(self.client_secret_file, ['https://www.googleapis.com/auth/youtube'])

            return flow.run_console()

    def refresh_token(self) -> Credentials:

        # Create a new Request Object.
        request = Request()

        # Load the file
        credentials = Credentials.from_authorized_user_file(filename=self.youtube_state_file)

        # Refresh the token
        credentials.refresh(request)

        return credentials

    def _validate_token(self) -> bool:

        if self.credentials.valid:
            return True
        else:
            self.refresh_token()
            return True