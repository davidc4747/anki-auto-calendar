import os

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

from ..utils import get_credential_file_path, get_token_file_path


# Google Authorization
#########################################################################
def authorize():
    SCOPES = ["https://www.googleapis.com/auth/calendar"]
    creds = None
    credentialsfile = get_credential_file_path()
    tokenfile = get_token_file_path()

    if os.path.exists(tokenfile):
        creds = Credentials.from_authorized_user_file(tokenfile, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentialsfile, SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open(tokenfile, "w") as token:
            token.write(creds.to_json())

    return creds.token
