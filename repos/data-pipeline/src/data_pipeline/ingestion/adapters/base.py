"""Base interfaces for ingestion adapters."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable, Mapping


class SourceAdapter(ABC):
    """Abstract interface for raw data providers."""

    @abstractmethod
    def load(self) -> Iterable[Mapping[str, object]]:
        """Yield raw records from an upstream source."""

        raise NotImplementedError
