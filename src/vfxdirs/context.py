from __future__ import annotations

import os
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Mapping, TypeAlias

OSName: TypeAlias = Literal["windows", "macos", "linux"]


def _detect_os_name() -> OSName:
    if sys.platform.startswith("win"):
        return "windows"
    if sys.platform == "darwin":
        return "macos"
    if sys.platform.startswith("linux"):
        return "linux"
    raise RuntimeError(f"Unsupported platform: {sys.platform!r}")


def _home_from_env(os_name: OSName, env: Mapping[str, str]) -> Path:
    # pref env values so tests can inject a fake env
    if os_name == "windows":
        value = env.get("USERPROFILE")
    else:
        value = env.get("HOME")
    return Path(value) if value else Path.home()


@dataclass(frozen=True, slots=True)
class Context:
    """OS/environment facts used during path resolution."""

    os: OSName
    env: Mapping[str, str]
    home: Path
    cwd: Path
    temp_dir: Path
    config_home: Path
    data_home: Path
    cache_home: Path
    install_roots: tuple[Path, ...]

    @classmethod
    def from_env(
        cls,
        env: Mapping[str, str] | None = None,
        *,  # force all following args to be keyword-only
        os_name: OSName | None = None,
        home: Path | None = None,
        cwd: Path | None = None,
    ) -> "Context":
        env_map: Mapping[str, str]
        if env is None:
            # TODO: is this stable enough for all callers?
            env_map = os.environ
        else:
            env_map = env

        detected_os = os_name or _detect_os_name()
        resolved_home = home or _home_from_env(detected_os, env_map)
        resolved_cwd = cwd or Path.cwd()
        temp_dir = Path(tempfile.gettempdir())

        # TODO: worth using platformdirs? Would like to avoid external deps
        if detected_os == "linux":
            config_home = Path(env_map.get(
                "XDG_CONFIG_HOME", resolved_home / ".config"))
            data_home = Path(env_map.get(
                "XDG_DATA_HOME", resolved_home / ".local" / "share"))
            cache_home = Path(env_map.get(
                "XDG_CACHE_HOME", resolved_home / ".cache"))
            install_roots = (Path("/opt"), Path("/usr/local"), Path("/usr"))
        elif detected_os == "macos":
            library = resolved_home / "Library"
            config_home = library / "Application Support"
            data_home = library / "Application Support"
            cache_home = library / "Caches"
            install_roots = (Path("/Applications"),
                             Path("/Applications/Utilities"))
        else:  # windows
            appdata = env_map.get("APPDATA")
            localappdata = env_map.get("LOCALAPPDATA")

            config_home = Path(
                appdata) if appdata else resolved_home / "AppData" / "Roaming"
            data_home = config_home
            cache_home = (
                Path(localappdata) if localappdata else resolved_home /
                "AppData" / "Local"
            )

            roots: list[Path] = []
            for key in ("ProgramFiles", "ProgramW6432", "ProgramFiles(x86)"):
                value = env_map.get(key)
                if value:
                    roots.append(Path(value))
            install_roots = tuple(roots) if roots else (
                Path("C:/Program Files"),)

        return cls(
            os=detected_os,
            env=env_map,
            home=resolved_home,
            cwd=resolved_cwd,
            temp_dir=temp_dir,
            config_home=config_home,
            data_home=data_home,
            cache_home=cache_home,
            install_roots=install_roots,
        )
