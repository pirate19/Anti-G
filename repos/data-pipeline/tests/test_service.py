import asyncio
from datetime import datetime, timedelta

import pytest

from scores_api.models import Match, Team
from scores_api.service import get_head_to_head_matches


@pytest.fixture
def sample_matches():
    now = datetime.utcnow()
    base = Match(
        id="1",
        league_key="premier-league",
        name="A vs B",
        short_name="A-B",
        date=now,
        status="Final",
        venue="Arena",
        home_team=Team(id="1", name="Team One", abbreviation="ONE", home=True, score=1),
        away_team=Team(id="2", name="Team Two", abbreviation="TWO", home=False, score=1),
    )
    second = base.copy(update={
        "id": "2",
        "date": now - timedelta(days=30),
        "home_team": Team(id="1", name="Team Two", abbreviation="TWO", home=True, score=2),
        "away_team": Team(id="2", name="Team One", abbreviation="ONE", home=False, score=0),
    })
    return [base, second]


def test_get_head_to_head_matches(monkeypatch, sample_matches):
    async def fake_range(client, *, league_key, start_date, end_date):  # noqa: D401
        return sample_matches

    monkeypatch.setattr("scores_api.service._get_matches_for_range", fake_range)

    matches = asyncio.run(
        get_head_to_head_matches(
            None,
            league_key="premier-league",
            date=datetime.utcnow(),
            team_one="Team One",
            team_two="Team Two",
        )
    )
    assert len(matches) == 2


def test_get_head_to_head_matches_requires_names(monkeypatch):
    async def fake_range(client, *, league_key, start_date, end_date):
        return []

    monkeypatch.setattr("scores_api.service._get_matches_for_range", fake_range)

    matches = asyncio.run(
        get_head_to_head_matches(
            None,
            league_key="premier-league",
            date=datetime.utcnow(),
            team_one="",
            team_two="Team Two",
        )
    )
    assert matches == []
