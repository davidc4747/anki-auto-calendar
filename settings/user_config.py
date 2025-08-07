from typing import Callable
from dataclasses import dataclass, asdict
from aqt import mw

addon_name = mw.addonManager.addonFromModule(__name__)


@dataclass
class UserConfig:
    event_name: str = "anki"
    event_color_id: int = 10
    calendar_name: str = "auto-calendar"
    min_event_time: int = 300
    client_secret: str = ""


def get_config() -> UserConfig:
    return UserConfig(**mw.addonManager.getConfig(addon_name))


def set_config(config: UserConfig) -> None:
    mw.addonManager.writeConfig(addon_name, asdict(config))


def restore_defaults() -> None:
    default_config = mw.addonManager.addonConfigDefaults(addon_name)
    mw.addonManager.writeConfig(addon_name, default_config)


def set_config_action(func: Callable) -> None:
    mw.addonManager.setConfigAction(addon_name, func)
