#!/usr/bin/python3

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaFileUpload
from googleapiclient.discovery import build
import json
import os

class gdrive():
    def __init__(self):
        # Set initial raw creds
        self.raw_creds = {
            'token': os.environ['TOKEN'],
            'refresh_token': os.environ['REFRESH_TOKEN'],
            'token_uri': os.environ['TOKEN_URI'],
            'client_id': os.environ['CLIENT_ID'],
            'client_secret': os.environ['CLIENT_SECRET'],
            'scopes': ['https://www.googleapis.com/auth/drive.metadata.readonly', 'https://www.googleapis.com/auth/drive.file'] # Modifying these scopes will require a new token
        }
        # Authenticate credentials
        self.creds = Credentials(
            token=self.raw_creds['token'],
            refresh_token=self.raw_creds['token'],
            token_uri=self.raw_creds['token'],
            client_id=self.raw_creds['token'],
            client_secret=self.raw_creds['token'],
            scopes=self.raw_creds['scopes']
        )

    def _refresh_token(self):
        # If there are no (valid) credentials available, let the user log in.
        if not self.creds.valid and self.creds.expired and self.creds.refresh_token:
            creds.refresh(Request())
            # Update raw creds
            self.raw_creds = creds.to_json()
        else:
            print('New token required')

    def upload(self, path_to_file, mimetype='text/plain'):
        # Refresh tokens if necessary
        self._refresh_token()
        # Initialize service
        service = build('drive', 'v3', credentials=self.creds)
        # Define file metadata and file media
        filename = path_to_file.split('/')[-1]
        metadata = {
            'parents': ['1OcdnicknPOAHsf8yKr43p5mm_hmWkjFm'],
            'name': filename,
            'mimeType': mimetype
        }
        media = MediaFileUpload(path_to_file, mimetype=mimetype, resumable=True)
        # Upload
        file = service.files().create(body=metadata, media_body=media, fields='id').execute()
        return file.get('id')
