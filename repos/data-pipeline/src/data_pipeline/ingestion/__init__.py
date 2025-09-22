"""Ingestion utilities."""

from .adapters.base import SourceAdapter
from .adapters.static import StaticJSONAdapter

__all__ = ["SourceAdapter", "StaticJSONAdapter"]
