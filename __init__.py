import os
import sys
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "lib"))

from anki.collection import Card
from aqt import mw, gui_hooks
from .settings.settings_window import SettingDialog
from .settings.user_config import (
    UserConfig,
    set_config_action,
    get_config,
    set_config,
    restore_defaults,
)

from .google.auth import authorize
from .google.calendar import (
    get_calendar_by_name,
    create_calendar,
    create_calendar_event,
)


calendar_id = None
start = None


# Init
#########################################################################
@gui_hooks.reviewer_did_init.append
def init(_) -> None:
    global calendar_id
    user_config = get_config()
    access_token = authorize(user_config.client_secret)

    cal_name = user_config.calendar_name
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
    user_config = get_config()

    # Make sure timestamp has a value
    if start and calendar_id:
        end = datetime.now(timezone.utc)
        duration = end - start
        min_time = timedelta(seconds=user_config.min_event_time)

        if duration >= min_time:
            access_token = authorize(user_config.client_secret)
            create_calendar_event(
                access_token,
                calendar_id,
                user_config.event_name,
                user_config.event_color_id,
                start,
                end,
            )

    start = None  # Reset Timer


gui_hooks.reviewer_will_end.append(end_timer)
mw.destroyed.connect(end_timer)


# Settings Window
#########################################################################
# @gui_hooks.main_window_did_init.append
@set_config_action
def show_settings_window() -> None:
    dialog = SettingDialog(get_config())

    def handle_save() -> None:
        set_config(
            UserConfig(
                calendar_name=dialog.calendar_name_txt.text(),
                event_name=dialog.event_name_txt.text(),
                event_color_id=dialog.color_id_cbx.currentData(),
                min_event_time=int(dialog.min_time_txt.text()),
                client_secret=dialog.client_secret_txt.text(),
            )
        )

    dialog.saved.connect(handle_save)
    dialog.default_restored.connect(restore_defaults)

    dialog.open()
    dialog.activateWindow()
