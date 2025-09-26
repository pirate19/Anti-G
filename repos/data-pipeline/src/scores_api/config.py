"""Configuration constants for the scores API service."""
from __future__ import annotations

from datetime import timedelta

# Mapping between UI facing league keys and ESPN API paths.
LEAGUES = {
    "premier-league": {
        "name": "Premier League",
        "espn_path": "eng.1",
    },
    "la-liga": {
        "name": "La Liga",
        "espn_path": "esp.1",
    },
    "serie-a": {
        "name": "Serie A",
        "espn_path": "ita.1",
    },
    "bundesliga": {
        "name": "Bundesliga",
        "espn_path": "ger.1",
    },
    "ligue-1": {
        "name": "Ligue 1",
        "espn_path": "fra.1",
    },
}

DEFAULT_LEAGUE = "premier-league"

# Lookback period used when searching for previous results of a given team.
TEAM_LOOKBACK_WINDOW = timedelta(days=120)

# Timeout applied to outbound HTTP requests.
HTTP_TIMEOUT_SECONDS = 10.0

__all__ = [
    "DEFAULT_LEAGUE",
    "HTTP_TIMEOUT_SECONDS",
    "LEAGUES",
    "TEAM_LOOKBACK_WINDOW",
]
