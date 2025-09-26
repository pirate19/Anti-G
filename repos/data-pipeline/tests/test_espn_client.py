from datetime import datetime

import pytest

from scores_api.clients.espn import parse_matches


@pytest.fixture
def sample_payload():
    return {
        "events": [
            {
                "id": "123",
                "name": "Team A vs Team B",
                "shortName": "TMA vs TMB",
                "date": "2024-02-20T15:00Z",
                "status": {
                    "type": {
                        "description": "Final",
                    }
                },
                "competitions": [
                    {
                        "venue": {"fullName": "Stadium"},
                        "competitors": [
                            {
                                "id": "1",
                                "homeAway": "home",
                                "displayName": "Team A",
                                "team": {"abbreviation": "TMA"},
                                "score": "2",
                            },
                            {
                                "id": "2",
                                "homeAway": "away",
                                "displayName": "Team B",
                                "team": {"abbreviation": "TMB"},
                                "score": "1",
                            },
                        ],
                    }
                ],
            }
        ]
    }


def test_parse_matches(sample_payload):
    matches = parse_matches(sample_payload, league_key="premier-league")
    assert len(matches) == 1

    match = matches[0]
    assert match.id == "123"
    assert match.league_key == "premier-league"
    assert match.name == "Team A vs Team B"
    assert match.short_name == "TMA vs TMB"
    assert match.status == "Final"
    assert match.venue == "Stadium"
    assert match.home_team.name == "Team A"
    assert match.home_team.home is True
    assert match.home_team.score == 2
    assert match.away_team.name == "Team B"
    assert match.away_team.home is False
    assert match.away_team.score == 1
    assert match.date == datetime(2024, 2, 20, 15, 0, tzinfo=match.date.tzinfo)
