from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Protocol, runtime_checkable

from .context import Context
from .keys import DirKey, KeyLike, normalize_key


@runtime_checkable
class VFXApp(Protocol):
    """Protocol implemented by app providers"""

    id: str
    display_name: str

    def supported_keys(self) -> set[DirKey]:
        """Return the set of `DirKey`s this app provider can resolve."""

    def path(self, key: KeyLike, ctx: Context, *, version: str | None = None) -> Path:
        """Resolve a directory path for the given key and context."""


@dataclass(frozen=True, slots=True)
class AppDirs:
    """Key-based directory access scoped to an app (and optional version)."""

    provider: VFXApp
    ctx: Context
    version: str | None = None

    @property
    def app_id(self) -> str:
        return self.provider.id

    def path(self, key: KeyLike) -> Path:
        return self.provider.path(normalize_key(key), self.ctx, version=self.version)

    def paths(self) -> dict[DirKey, Path]:
        return {k: self.path(k) for k in self.provider.supported_keys()}


class VFXDirs:
    """Primary entry point for resolving per-app directories."""

    def __init__(
        self,
        *,
        config: object | None = None,
        registry: Mapping[str, VFXApp] | None = None,
        env: Mapping[str, str] | None = None,
        context: Context | None = None,
    ) -> None:
        self._config = config
        self._ctx = context or Context.from_env(env)
        self._registry: dict[str, VFXApp] = {
            str(k).strip().lower(): v for (k, v) in (registry or {}).items()
        }

    @property
    def ctx(self) -> Context:
        return self._ctx

    def registered_apps(self) -> tuple[str, ...]:
        return tuple(sorted(self._registry.keys()))

    def app(self, app_id: str, *, version: str | None = None) -> AppDirs:
        key = app_id.strip().lower()
        try:
            provider = self._registry[key]
        except KeyError as err:
            available = ", ".join(self.registered_apps()) or "<none>"
            raise KeyError(
                f"Unknown app_id {app_id!r}. Registered apps: {available}") from err
        return AppDirs(provider=provider, ctx=self._ctx, version=version)

    def path(self, app_id: str, key: KeyLike, *, version: str | None = None) -> Path:
        return self.app(app_id, version=version).path(key)


def path(
    app_id: str,
    key: KeyLike,
    version: str | None = None,
    *,
    config: object | None = None,
    registry: Mapping[str, VFXApp] | None = None,
    env: Mapping[str, str] | None = None,
    context: Context | None = None,
) -> Path:
    """convenience function to resolve a single path without dealing with a full instance."""

    return VFXDirs(config=config, registry=registry, env=env, context=context).path(
        app_id, key, version=version
    )
