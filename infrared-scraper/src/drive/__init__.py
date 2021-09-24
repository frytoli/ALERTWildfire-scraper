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
        # Set vars
        self.CLIENT_ID = os.environ['CLIENT_ID']
        self.CLIENT_SECRET = os.environ['CLIENT_SECRET']
        self.PROJECT_ID = os.environ['PROJECT_ID']
        self.TOKEN_URI = 'https://oauth2.googleapis.com/token'
        self.AUTH_URI = 'https://accounts.google.com/o/oauth2/auth'
        self.AUTH_PROVIDER_X509_CERT_URL = 'https://www.googleapis.com/oauth2/v1/certs'
        self.REDIRECT_URIS = ['urn:ietf:wg:oauth:2.0:oob', 'http://localhost']
        self.SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly', 'https://www.googleapis.com/auth/drive.file'] # Modifying these scopes will require a new token
        self.PARENT_DIR = os.environ['GDRIVE_PARENT_DIR']
        # Authenticate credentials
        self.creds = Credentials(
            token=os.environ['TOKEN'],
            refresh_token=os.environ['REFRESH_TOKEN'],
            token_uri=self.TOKEN_URI,
            client_id=self.CLIENT_ID,
            client_secret=self.CLIENT_SECRET,
            scopes=self.SCOPES
        )

    def _refresh_token(self):
        # If there are no (valid) credentials available, let the user log in.
        if not self.creds or not self.creds.valid:
            if self.creds.expired and self.creds.refresh_token:
                creds.refresh(Request())
                # Update raw creds
                #self.raw_creds = creds.to_json()
            else:
                flow = InstalledAppFlow.from_client_config(
                    client_config={
                        'installed': {
                            'client_id': self.CLIENT_ID,
                            'project_id': self.PROJECT_ID,
                            'auth_uri': self.AUTH_URI,
                            'token_uri': self.TOKEN_URI,
                            'auth_provider_x509_cert_url': self.AUTH_PROVIDER_X509_CERT_URL,
                            'client_secret': self.CLIENT_SECRET,
                            'redirect_uris': self.REDIRECT_URIS
                        }
                    },
                    scopes=self.SCOPES
                )
                creds = flow.run_local_server(port=0)

    def upload(self, path_to_file, mimetype='text/plain'):
        # Refresh tokens if necessary
        self._refresh_token()
        # Initialize service
        service = build('drive', 'v3', credentials=self.creds)
        # Define file metadata and file media
        filename = path_to_file.split('/')[-1]
        metadata = {
            'parents': [self.PARENT_DIR],
            'name': filename,
            'mimeType': mimetype
        }
        media = MediaFileUpload(path_to_file, mimetype=mimetype, resumable=True)
        # Upload
        file = service.files().create(body=metadata, media_body=media, fields='id').execute()
        return file.get('id')
