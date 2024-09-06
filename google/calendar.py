from typing import Optional, Union
from datetime import datetime
import requests


# Calendar API Calls
#########################################################################
def get_all_calendars(token: str):
    res = requests.get(
        f"https://www.googleapis.com/calendar/v3/users/me/calendarList",
        headers={"Authorization": f"Bearer {token}"},
    )
    res.raise_for_status()
    return res.json()


def get_calendar_by_name(token: str, calendar_name: str) -> Optional[dict]:
    # Search to the calendar in the list
    calendars = get_all_calendars(token).get("items")
    selected_calendar = [
        cal for cal in calendars if cal.get("summary") == calendar_name
    ]

    # Return Calendar if found
    if len(selected_calendar) > 0:
        return selected_calendar[0]
    else:
        return None


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
