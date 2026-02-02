from __future__ import annotations

from enum import StrEnum
from typing import TypeAlias


class DirKey(StrEnum):
    """Common per-application directory "kinds".

    This is intentionally small and shared across many DCCs. Individual apps may
    support only a subset. Callers may also pass custom string keys to API's.
    """

    PREFS = "prefs"
    CONFIG = "config"
    DATA = "data"
    CACHE = "cache"
    LOGS = "logs"
    TEMP = "temp"
    SCRIPTS = "scripts"
    PLUGINS = "plugins"
    PACKAGES = "packages"


KeyLike: TypeAlias = DirKey | str
