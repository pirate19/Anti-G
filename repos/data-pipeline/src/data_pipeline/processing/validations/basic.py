"""Simple guard-rail validations for normalized matches."""

from __future__ import annotations

from datetime import datetime, timezone

from ...models import MatchRecord


class BasicMatchValidator:
    """Minimal validation rules before persisting matches."""

    def __init__(self, earliest_year: int = 2000) -> None:
        self._earliest_year = earliest_year

    def validate(self, match: MatchRecord) -> None:
        """Raise :class:`ValueError` if the record violates basic assumptions."""

        if match.home_team == match.away_team:
            raise ValueError("Home and away teams must differ")

        if match.kickoff.tzinfo is None:
            raise ValueError("Kickoff timestamp must include timezone info")

        min_dt = datetime(self._earliest_year, 1, 1, tzinfo=timezone.utc)
        if match.kickoff < min_dt:
            raise ValueError("Kickoff predates allowed window")

        if match.home_score is not None and match.home_score < 0:
            raise ValueError("Home score cannot be negative")

        if match.away_score is not None and match.away_score < 0:
            raise ValueError("Away score cannot be negative")

        if match.home_form is not None and not 0 <= match.home_form <= 1:
            raise ValueError("Home form must be within [0, 1]")

        if match.away_form is not None and not 0 <= match.away_form <= 1:
            raise ValueError("Away form must be within [0, 1]")
