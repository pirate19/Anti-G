"""Business logic for assembling match queries."""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Iterable

import httpx

from .clients.espn import fetch_scoreboard, fetch_scoreboards
from .config import LEAGUES, TEAM_LOOKBACK_WINDOW
from .models import Match


def list_leagues() -> list[dict[str, str]]:
    """Return configured leagues ordered alphabetically by display name."""
    return [
        {"key": key, "name": data["name"]}
        for key, data in sorted(LEAGUES.items(), key=lambda item: item[1]["name"])
    ]


def _normalize(name: str | None) -> str:
    return (name or "").strip().casefold()


async def get_matches_for_date(client: httpx.AsyncClient, *, league_key: str, date: datetime) -> list[Match]:
    """Retrieve matches scheduled for a specific date."""
    return await fetch_scoreboard(client, league_key=league_key, date=date)


async def _get_matches_for_range(
    client: httpx.AsyncClient,
    *,
    league_key: str,
    start_date: datetime,
    end_date: datetime,
) -> list[Match]:
    if start_date > end_date:
        start_date, end_date = end_date, start_date
    delta = end_date - start_date
    dates: Iterable[datetime] = (start_date + timedelta(days=offset) for offset in range(delta.days + 1))
    return await fetch_scoreboards(client, league_key=league_key, dates=dates)


async def get_matches_for_team(
    client: httpx.AsyncClient,
    *,
    league_key: str,
    date: datetime,
    team_name: str,
) -> list[Match]:
    """Return matches involving a specific team within the configured lookback window."""
    lookback_start = date - TEAM_LOOKBACK_WINDOW
    matches = await _get_matches_for_range(client, league_key=league_key, start_date=lookback_start, end_date=date)
    normalized = _normalize(team_name)
    return [
        match
        for match in matches
        if normalized
        and (
            _normalize(match.home_team.name) == normalized
            or _normalize(match.away_team.name) == normalized
        )
    ]


async def get_head_to_head_matches(
    client: httpx.AsyncClient,
    *,
    league_key: str,
    date: datetime,
    team_one: str,
    team_two: str,
) -> list[Match]:
    """Return historical matches between the two provided teams."""
    lookback_start = date - TEAM_LOOKBACK_WINDOW
    matches = await _get_matches_for_range(client, league_key=league_key, start_date=lookback_start, end_date=date)

    team_one_norm = _normalize(team_one)
    team_two_norm = _normalize(team_two)
    if not team_one_norm or not team_two_norm:
        return []

    return [
        match
        for match in matches
        if {team_one_norm, team_two_norm}
        == {
            _normalize(match.home_team.name),
            _normalize(match.away_team.name),
        }
    ]


__all__ = [
    "get_head_to_head_matches",
    "get_matches_for_date",
    "get_matches_for_team",
    "list_leagues",
]
