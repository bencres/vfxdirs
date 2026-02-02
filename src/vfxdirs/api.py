from __future__ import annotations

from pathlib import Path
from typing import Protocol, runtime_checkable

from .context import Context
from .keys import DirKey, KeyLike


@runtime_checkable
class VFXApp(Protocol):
    """Protocol implemented by app providers"""

    id: str
    display_name: str

    def supported_keys(self) -> set[DirKey]:
        """Return the set of `DirKey`s this app provider can resolve."""

    def path(self, key: KeyLike, ctx: Context, *, version: str | None = None) -> Path:
        """Resolve a directory path for the given key and context."""
