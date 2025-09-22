"""Transformation logic for football match data."""

from __future__ import annotations

from datetime import datetime
from typing import Mapping, MutableMapping, Optional

from ...models import MatchRecord


class MatchTransformer:
    """Convert raw payloads from various feeds into :class:`MatchRecord`."""

    def __init__(self, default_competition: str | None = None) -> None:
        self._default_competition = default_competition

    def transform(self, raw: Mapping[str, object]) -> MatchRecord:
        """Normalize a raw record.

        Parameters
        ----------
        raw:
            Mapping returned by a :class:`~data_pipeline.ingestion.SourceAdapter`.
        """

        record = _as_mutable(raw)
        match_id = _require_str(record, {"id", "match_id"})
        competition = self._extract_competition(record)
        season = str(record.get("season") or "")
        kickoff = self._parse_datetime(record)

        home_team, home_score, home_form = self._extract_team(record, "home")
        away_team, away_score, away_form = self._extract_team(record, "away")

        venue = _nested_str(record, ["venue", "name"])
        surface = _nested_str(record, ["venue", "surface"])
        weather = record.get("weather")
        extras = {
            "source": record.get("source"),
            "referee": record.get("referee"),
            "round": record.get("round"),
        }

        return MatchRecord(
            match_id=match_id,
            competition=competition,
            season=season,
            kickoff=kickoff,
            home_team=home_team,
            away_team=away_team,
            home_score=home_score,
            away_score=away_score,
            venue=venue,
            surface=surface,
            weather=weather if isinstance(weather, str) else None,
            home_form=home_form,
            away_form=away_form,
            extras={k: v for k, v in extras.items() if v is not None},
        )

    def _extract_competition(self, record: MutableMapping[str, object]) -> str:
        competition = record.get("competition")
        if isinstance(competition, Mapping):
            name = competition.get("name")
            if isinstance(name, str) and name:
                return name
        if isinstance(competition, str) and competition:
            return competition
        if self._default_competition:
            return self._default_competition
        raise ValueError("Missing competition in raw record")

    def _extract_team(
        self, record: MutableMapping[str, object], key: str
    ) -> tuple[str, Optional[int], Optional[float]]:
        team = record.get(key)
        if not isinstance(team, Mapping):
            raise ValueError(f"Missing {key} team block")

        name = team.get("name")
        if not isinstance(name, str) or not name:
            raise ValueError(f"Missing {key} team name")

        score = _safe_int(team.get("score"))
        form = _safe_float(team.get("form"))
        return name, score, form

    def _parse_datetime(self, record: MutableMapping[str, object]) -> datetime:
        raw_value = record.get("kickoff") or record.get("date")
        if not isinstance(raw_value, str):
            raise ValueError("Kickoff timestamp missing")

        normalized = raw_value.replace("Z", "+00:00")
        try:
            return datetime.fromisoformat(normalized)
        except ValueError as exc:
            raise ValueError(f"Invalid kickoff timestamp: {raw_value}") from exc


def _as_mutable(raw: Mapping[str, object]) -> MutableMapping[str, object]:
    if isinstance(raw, MutableMapping):
        return raw
    return dict(raw)


def _nested_str(record: Mapping[str, object], path: list[str]) -> Optional[str]:
    cursor: object = record
    for segment in path:
        if not isinstance(cursor, Mapping):
            return None
        cursor = cursor.get(segment)
    return cursor if isinstance(cursor, str) else None


def _require_str(record: Mapping[str, object], keys: set[str]) -> str:
    for key in keys:
        value = record.get(key)
        if isinstance(value, str) and value:
            return value
    raise ValueError(f"Missing string identifier, checked keys: {sorted(keys)}")


def _safe_int(value: object) -> Optional[int]:
    if value is None:
        return None
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, (int,)):
        return value
    if isinstance(value, str) and value.strip():
        try:
            return int(value)
        except ValueError:
            return None
    return None


def _safe_float(value: object) -> Optional[float]:
    if value is None:
        return None
    if isinstance(value, bool):
        return float(int(value))
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str) and value.strip():
        try:
            return float(value)
        except ValueError:
            return None
    return None
