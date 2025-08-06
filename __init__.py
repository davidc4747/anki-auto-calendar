import os
import sys
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "lib"))

from anki.collection import Card
from aqt import mw, gui_hooks

from .google.auth import authorize
from .google.calendar import (
    get_calendar_by_name,
    create_calendar,
    create_calendar_event,
)


user_config = mw.addonManager.getConfig(__name__)
calendar_id = None
start = None


@gui_hooks.reviewer_did_init.append
def init(_) -> None:
    global calendar_id
    access_token = authorize()

    cal_name = user_config.get("calendar_name")
    calendar = get_calendar_by_name(access_token, cal_name)

    # create calendar if calendar_name wasn't found
    if calendar:
        calendar_id = calendar.get("id")
    else:
        calendar_id = create_calendar(access_token, cal_name).get("id")


# Start
#########################################################################
@gui_hooks.reviewer_did_show_question.append
def start_timer(card: Card) -> None:
    global start

    # only set start time for the first question shown
    if start == None:
        start = datetime.now(timezone.utc)


# End
#########################################################################
def end_timer() -> None:
    global start

    # Make sure timestamp has a value
    if start and calendar_id:
        end = datetime.now(timezone.utc)
        duration = end - start
        min_time = timedelta(seconds=user_config.get("min_event_time"))

        if duration >= min_time:
            access_token = authorize()
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
