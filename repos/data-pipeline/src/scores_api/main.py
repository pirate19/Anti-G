"""FastAPI application exposing football match data via REST and HTML."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Optional

import httpx
from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from .config import DEFAULT_LEAGUE, LEAGUES
from .models import MatchQuery, MatchResponse
from .service import (
    get_head_to_head_matches,
    get_matches_for_date,
    get_matches_for_team,
    list_leagues,
)

app = FastAPI(title="Football Scores API", version="0.1.0")

templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent / "templates"))


async def get_http_client() -> httpx.AsyncClient:
    async with httpx.AsyncClient(headers={"User-Agent": "Anti-G-ScoreScraper/0.1"}) as client:
        yield client


def _resolve_league(league: str) -> str:
    if league not in LEAGUES:
        raise HTTPException(status_code=400, detail=f"Unsupported league '{league}'.")
    return league


def _parse_date(date_str: Optional[str]) -> datetime:
    if not date_str:
        return datetime.utcnow()
    try:
        return datetime.fromisoformat(date_str)
    except ValueError as exc:  # pragma: no cover - defensive
        raise HTTPException(status_code=400, detail="Invalid date format. Use ISO YYYY-MM-DD.") from exc


@app.get("/healthz")
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


async def _load_matches(
    *,
    client: httpx.AsyncClient,
    league_key: str,
    match_date: datetime,
    view: str,
    team1: Optional[str],
    team2: Optional[str],
    raise_on_error: bool,
):
    if view == "date":
        try:
            matches = await get_matches_for_date(client, league_key=league_key, date=match_date)
        except httpx.HTTPError as exc:
            if raise_on_error:
                raise HTTPException(status_code=502, detail="Unable to reach upstream scoreboard.") from exc
            return [], "Unable to reach upstream scoreboard. Please retry later."
    elif view == "team1":
        if not team1:
            raise HTTPException(status_code=400, detail="team1 query parameter required for view=team1")
        try:
            matches = await get_matches_for_team(client, league_key=league_key, date=match_date, team_name=team1)
        except httpx.HTTPError as exc:
            if raise_on_error:
                raise HTTPException(status_code=502, detail="Unable to reach upstream scoreboard.") from exc
            return [], "Unable to reach upstream scoreboard. Please retry later."
    elif view == "team2":
        if not team2:
            raise HTTPException(status_code=400, detail="team2 query parameter required for view=team2")
        try:
            matches = await get_matches_for_team(client, league_key=league_key, date=match_date, team_name=team2)
        except httpx.HTTPError as exc:
            if raise_on_error:
                raise HTTPException(status_code=502, detail="Unable to reach upstream scoreboard.") from exc
            return [], "Unable to reach upstream scoreboard. Please retry later."
    elif view == "head-to-head":
        if not team1 or not team2:
            raise HTTPException(status_code=400, detail="team1 and team2 parameters required for head-to-head view")
        try:
            matches = await get_head_to_head_matches(
                client,
                league_key=league_key,
                date=match_date,
                team_one=team1,
                team_two=team2,
            )
        except httpx.HTTPError as exc:
            if raise_on_error:
                raise HTTPException(status_code=502, detail="Unable to reach upstream scoreboard.") from exc
            return [], "Unable to reach upstream scoreboard. Please retry later."
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported view '{view}'.")

    return matches, None


@app.get("/api/matches", response_model=MatchResponse)
async def api_matches(
    league: str = Query(DEFAULT_LEAGUE, description="League identifier"),
    date: Optional[str] = Query(None, description="Target date in ISO format"),
    view: str = Query("date", description="date | team1 | team2 | head-to-head"),
    team1: Optional[str] = Query(None, description="Team 1 name"),
    team2: Optional[str] = Query(None, description="Team 2 name"),
    client: httpx.AsyncClient = Depends(get_http_client),
) -> MatchResponse:
    league_key = _resolve_league(league)
    match_date = _parse_date(date)

    matches, _ = await _load_matches(
        client=client,
        league_key=league_key,
        match_date=match_date,
        view=view,
        team1=team1,
        team2=team2,
        raise_on_error=True,
    )

    query = MatchQuery(
        league_key=league_key,
        date=match_date,
        view=view,
        team1=team1,
        team2=team2,
    )
    return MatchResponse(query=query, matches=matches)


@app.get("/", response_class=HTMLResponse)
async def homepage(
    request: Request,
    league: str = Query(DEFAULT_LEAGUE),
    date: Optional[str] = Query(None),
    view: str = Query("date"),
    team1: Optional[str] = Query(None),
    team2: Optional[str] = Query(None),
    client: httpx.AsyncClient = Depends(get_http_client),
) -> HTMLResponse:
    league_key = _resolve_league(league)
    match_date = _parse_date(date)

    matches, error_message = await _load_matches(
        client=client,
        league_key=league_key,
        match_date=match_date,
        view=view,
        team1=team1,
        team2=team2,
        raise_on_error=False,
    )

    context = {
        "request": request,
        "leagues": list_leagues(),
        "selected_league": league_key,
        "query": MatchQuery(
            league_key=league_key,
            date=match_date,
            view=view,
            team1=team1,
            team2=team2,
        ),
        "matches": matches,
        "team1": team1 or "",
        "team2": team2 or "",
        "view": view,
        "date": match_date.date().isoformat(),
        "error_message": error_message,
    }
    return templates.TemplateResponse("index.html", context)


__all__ = ["app"]
