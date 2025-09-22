"""JSON Lines sink for persisting normalized matches."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from ..models import MatchRecord


class JsonLinesSink:
    """Write records to a JSON Lines document."""

    def __init__(self, path: Path | str) -> None:
        self._path = Path(path)
        self._handle = None

    @property
    def path(self) -> Path:
        return self._path

    def __enter__(self) -> "JsonLinesSink":  # noqa: D401 - context manager semantics
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._handle = self._path.open("w", encoding="utf-8")
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:  # noqa: D401
        if self._handle:
            self._handle.close()
            self._handle = None

    def write(self, record: MatchRecord) -> None:
        if self._handle is None:
            raise RuntimeError("Sink must be entered before writing")
        payload = record.to_serializable_dict()
        json.dump(payload, self._handle, ensure_ascii=False)
        self._handle.write("\n")

    def flush_all(self, records: Iterable[MatchRecord]) -> None:
        with self as sink:
            for record in records:
                sink.write(record)
