import os

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

from ..utils import get_token_file_path


# Google Authorization
#########################################################################
def authorize(client_secret: str):
    SCOPES = ["https://www.googleapis.com/auth/calendar"]
    creds = None
    credentials = {
        "installed": {
            "client_id": "361697807204-8mrbsc320a8291l3pr50c5h15oq5bu8v.apps.googleusercontent.com",
            "client_secret": client_secret,
            "redirect_uris": [],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://accounts.google.com/o/oauth2/token",
            "revoke_uri": "https://accounts.google.com/o/oauth2/revoke",
        }
    }
    tokenfile = get_token_file_path()

    if os.path.exists(tokenfile):
        creds = Credentials.from_authorized_user_file(tokenfile, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except:
                flow = InstalledAppFlow.from_client_config(credentials, SCOPES)
                creds = flow.run_local_server(port=0)

        else:
            flow = InstalledAppFlow.from_client_config(credentials, SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open(tokenfile, "w") as token:
            token.write(creds.to_json())

    return creds.token
