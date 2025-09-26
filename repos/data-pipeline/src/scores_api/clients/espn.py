"""Client helpers for interacting with ESPN's public soccer scoreboards."""
from __future__ import annotations

from datetime import datetime
from typing import Iterable

import httpx

from ..config import HTTP_TIMEOUT_SECONDS, LEAGUES
from ..models import Match, Team

SCOREBOARD_URL_TEMPLATE = "https://site.api.espn.com/apis/site/v2/sports/soccer/{league_path}/scoreboard"


def _parse_team(data: dict, home: bool) -> Team:
    score = data.get("score")
    try:
        parsed_score = int(score) if score not in (None, "") else None
    except ValueError:
        parsed_score = None

    return Team(
        id=str(data.get("id", "")),
        name=data.get("displayName") or data.get("team", {}).get("displayName", "Unknown"),
        abbreviation=(data.get("team") or {}).get("abbreviation"),
        home=home,
        score=parsed_score,
    )


def _parse_match(event: dict, *, league_key: str) -> Match:
    competitions = event.get("competitions") or []
    competition = competitions[0] if competitions else {}
    competitors = competition.get("competitors") or []

    home_raw = next((team for team in competitors if team.get("homeAway") == "home"), competitors[0] if competitors else {})
    away_raw = next((team for team in competitors if team.get("homeAway") == "away"), competitors[1] if len(competitors) > 1 else {})

    status = event.get("status", {}).get("type", {}).get("description") or event.get("status", {}).get("type", {}).get("detail") or "Unknown"

    return Match(
        id=str(event.get("id", "")),
        league_key=league_key,
        name=event.get("name") or "",
        short_name=event.get("shortName"),
        date=datetime.fromisoformat(event.get("date", "").replace("Z", "+00:00")),
        status=status,
        venue=competition.get("venue", {}).get("fullName"),
        home_team=_parse_team(home_raw, True),
        away_team=_parse_team(away_raw, False),
    )


def parse_matches(payload: dict, *, league_key: str) -> list[Match]:
    """Parse the scoreboard payload returned by ESPN into match objects."""
    events = payload.get("events") or []
    matches: list[Match] = []
    for event in events:
        try:
            matches.append(_parse_match(event, league_key=league_key))
        except Exception:  # pragma: no cover - guard against payload drift
            continue
    return matches


async def fetch_scoreboard(client: httpx.AsyncClient, *, league_key: str, date: datetime) -> list[Match]:
    """Fetch and parse the scoreboard for a league on a specific date."""
    league = LEAGUES[league_key]
    url = SCOREBOARD_URL_TEMPLATE.format(league_path=league["espn_path"])
    params = {"dates": date.strftime("%Y%m%d")}

    response = await client.get(url, params=params, timeout=HTTP_TIMEOUT_SECONDS)
    response.raise_for_status()
    payload = response.json()
    return parse_matches(payload, league_key=league_key)


async def fetch_scoreboards(
    client: httpx.AsyncClient,
    *,
    league_key: str,
    dates: Iterable[datetime],
) -> list[Match]:
    """Fetch scoreboards for multiple dates and flatten the results."""
    matches: list[Match] = []
    for date in dates:
        try:
            matches.extend(await fetch_scoreboard(client, league_key=league_key, date=date))
        except httpx.HTTPError:
            continue
    return matches


__all__ = ["fetch_scoreboard", "fetch_scoreboards", "parse_matches"]
