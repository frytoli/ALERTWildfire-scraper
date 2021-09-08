from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaFileUpload
from googleapiclient.discovery import build
import sys
import os

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly', 'https://www.googleapis.com/auth/drive.file']

def upload(testfile=None, parentdir_id=None):
    '''
        Fetch auth tokens for Google Drive API app and (optionally) upload a test file to Drive
    '''
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    # If a test file is included to test upload to Drive, upload it to drive
    if testfile:
        service = build('drive', 'v3', credentials=creds)

        if parentdir_id:
            file_metadata = {
                'parents': [parentdir_id],
                'name': testfile,
                'mimeType': '*/*'
            }
        else:
            file_metadata = {
                'name': testfile,
                'mimeType': '*/*'
            }

        media = MediaFileUpload(testfile,
                                mimetype='*/*',
                                resumable=True)
        file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        print ('File ID: ' + file.get('id'))

if __name__ == '__main__':
    if len(sys.argv) > 1:
        testfile = sys.argv[1]
        if len(sys.argv) > 2:
            parentdir_id = sys.argv[2]
            upload(testfile=testfile, parentdir_id=parentdir_id)
        else:
            upload(testfile=testfile)
    else:
        upload()
