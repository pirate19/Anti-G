"""Core domain models for the Anti-G data pipeline."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional


@dataclass(frozen=True)
class MatchRecord:
    """Normalized representation of a football match."""

    match_id: str
    competition: str
    season: str
    kickoff: datetime
    home_team: str
    away_team: str
    home_score: Optional[int]
    away_score: Optional[int]
    venue: Optional[str]
    surface: Optional[str]
    weather: Optional[str]
    home_form: Optional[float]
    away_form: Optional[float]
    extras: Dict[str, Any] = field(default_factory=dict, repr=False)

    def to_serializable_dict(self) -> Dict[str, Any]:
        """Return a JSON-ready dictionary."""

        payload = asdict(self)
        payload["kickoff"] = self.kickoff.isoformat()
        return payload


@dataclass(frozen=True)
class PipelineError:
    """Represents an error encountered while running a pipeline."""

    identifier: str
    reason: str


@dataclass(frozen=True)
class PipelineResult:
    """Summary emitted after the ingestion pipeline completes."""

    processed: int
    failed: int
    errors: List[PipelineError]
    output_locations: Iterable[str]

    @property
    def success(self) -> bool:
        """Return ``True`` when all records were processed successfully."""

        return self.failed == 0
