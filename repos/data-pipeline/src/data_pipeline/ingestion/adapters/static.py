"""Static file based adapters for local development and testing."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, Mapping, Sequence

from .base import SourceAdapter


class StaticJSONAdapter(SourceAdapter):
    """Loads match data from a JSON document on disk."""

    def __init__(self, path: Path | str) -> None:
        self._path = Path(path)

    @property
    def path(self) -> Path:
        """Return the backing file path."""

        return self._path

    def load(self) -> Iterable[Mapping[str, object]]:
        """Yield items from the JSON document."""

        with self._path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)

        if isinstance(payload, Mapping):
            yield payload
            return

        if isinstance(payload, Sequence):
            for item in payload:
                if isinstance(item, Mapping):
                    yield item
            return

        raise ValueError(f"Unsupported JSON payload in {self._path}")
