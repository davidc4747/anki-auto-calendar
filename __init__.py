import os
import sys
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "lib"))

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from anki.collection import Card
from anki.hooks import wrap
from aqt import mw, gui_hooks
from aqt.utils import showInfo
import requests


user_config = mw.addonManager.getConfig(__name__)
access_token = None
calendar_id = None
start = None


def init(_reviewer) -> None:
    global access_token
    global calendar_id
    access_token = authorize()

    # Get Calendar info by it's name
    calendars = get_all_calendars(access_token)
    selected_calendar = [
        cal
        for cal in calendars.get("items")
        if cal.get("summary") == user_config.get("calendar_name")
    ]

    # create calendar if calendar_name wasn't found
    if len(selected_calendar) > 0:
        calendar_id = selected_calendar[0].get("id")
    else:
        cal = create_calendar(access_token, user_config.get(("calendar_name")))
        calendar_id = cal.get("id")


gui_hooks.reviewer_did_init.append(init)


def start_timer(card: Card) -> None:
    global start

    # only set start time for the first question shown
    if start == None:
        start = datetime.now(timezone.utc)


gui_hooks.reviewer_did_show_question.append(start_timer)


def end_timer() -> None:
    global start

    # Make sure timestamp has a value
    if start and calendar_id:
        end = datetime.now(timezone.utc)
        duration = end - start
        min_time = timedelta(seconds=user_config.get("min_event_time"))

        if duration >= min_time:
            debug_to_file(f"{duration.total_seconds()}")
            create_calendar_event(
                access_token,
                calendar_id,
                user_config.get("event_name"),
                user_config.get("event_color_id"),
                start,
                end,
            )

    start = None  # Reset Timer


gui_hooks.reviewer_will_end.append(end_timer)
mw.destroyed.connect(end_timer)


# Google Authorization
#########################################################################
def authorize():
    SCOPES = ["https://www.googleapis.com/auth/calendar"]
    creds = None
    credentialsfile = os.path.join(os.path.dirname(__file__), "credentials.json")
    tokenfile = os.path.join(os.path.dirname(__file__), "token.json")

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


# Calendar API Calls
#########################################################################
def get_all_calendars(token: str):
    res = requests.get(
        f"https://www.googleapis.com/calendar/v3/users/me/calendarList",
        headers={"Authorization": f"Bearer {token}"},
    )
    res.raise_for_status()
    return res.json()


def create_calendar(token: str, name: str):
    res = requests.post(
        f"https://www.googleapis.com/calendar/v3/calendars",
        headers={"Authorization": f"Bearer {token}"},
        json={"summary": name},
    )
    res.raise_for_status()
    return res.json()


def create_calendar_event(
    token: str,
    calendar_id: str,
    event_name: str,
    event_color_id: int,
    start_time: datetime,
    end_time: datetime,
):
    res = requests.post(
        f"https://www.googleapis.com/calendar/v3/calendars/{calendar_id}/events",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "summary": event_name,
            "start": {"dateTime": start_time.isoformat()},
            "end": {"dateTime": end_time.isoformat()},
            "colorId": event_color_id,
        },
    )
    res.raise_for_status()


# Helpers
#########################################################################
def debug_to_file(text: str) -> None:
    debug = os.path.join(os.path.dirname(__file__), "debug.txt")
    with open(debug, "w") as token:
        token.write(text)
