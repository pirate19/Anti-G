"""Domain models for the football scores API."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class Team(BaseModel):
    """Represents a team participating in a match."""

    id: str = Field(..., description="ESPN identifier for the team")
    name: str = Field(..., description="Full display name of the team")
    abbreviation: Optional[str] = Field(None, description="Team abbreviation")
    home: bool = Field(..., description="Whether the team is the home side")
    score: Optional[int] = Field(None, description="Current or final score")


class Match(BaseModel):
    """Simplified representation of an ESPN event."""

    id: str = Field(..., description="Unique event identifier")
    league_key: str = Field(..., description="League short code used internally")
    name: str = Field(..., description="Human readable fixture name")
    short_name: Optional[str] = Field(None, description="Compact fixture name")
    date: datetime = Field(..., description="Kick-off date and time in UTC")
    status: str = Field(..., description="Match status description")
    venue: Optional[str] = Field(None, description="Venue name if available")
    home_team: Team = Field(..., description="Home team information")
    away_team: Team = Field(..., description="Away team information")


class MatchQuery(BaseModel):
    """Parameters describing a match search request."""

    league_key: str
    date: datetime
    view: str = "date"  # date, team1, team2, head-to-head
    team1: Optional[str] = None
    team2: Optional[str] = None


class MatchResponse(BaseModel):
    """Structured response returned by the REST API."""

    query: MatchQuery
    matches: list[Match]
    generated_at: datetime = Field(default_factory=datetime.utcnow)


__all__ = ["Match", "MatchQuery", "MatchResponse", "Team"]
