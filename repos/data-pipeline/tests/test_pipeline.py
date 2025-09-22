import json
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from data_pipeline.ingestion import StaticJSONAdapter  # noqa: E402
from data_pipeline.pipeline import IngestionPipeline  # noqa: E402
from data_pipeline.processing.transformations import MatchTransformer  # noqa: E402
from data_pipeline.processing.validations import BasicMatchValidator  # noqa: E402
from data_pipeline.storage import JsonLinesSink  # noqa: E402
from data_pipeline.models import MatchRecord  # noqa: E402


class IngestionPipelineTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.sample_file = ROOT / "tests" / "data" / "sample_matches.json"

    def test_pipeline_processes_and_writes_jsonl(self) -> None:
        adapter = StaticJSONAdapter(self.sample_file)
        transformer = MatchTransformer()
        validator = BasicMatchValidator()

        with tempfile.TemporaryDirectory() as tmpdir:
            sink_path = Path(tmpdir) / "matches.jsonl"
            sink = JsonLinesSink(sink_path)
            pipeline = IngestionPipeline(
                adapter=adapter,
                transformer=transformer,
                validators=[validator],
                sink=sink,
            )

            result = pipeline.run()

            self.assertEqual(result.processed, 1)
            self.assertEqual(result.failed, 1)
            self.assertFalse(result.success)
            self.assertIn(str(sink_path), result.output_locations)

            with sink_path.open("r", encoding="utf-8") as handle:
                lines = handle.readlines()

        self.assertEqual(len(lines), 1)
        record = json.loads(lines[0])
        self.assertEqual(record["match_id"], "EPL2023-001")
        self.assertEqual(record["home_team"], "Arsenal")
        self.assertEqual(record["away_team"], "Liverpool")
        self.assertEqual(record["home_score"], 2)
        self.assertEqual(record["away_score"], 1)
        self.assertIn("kickoff", record)

    def test_validator_rejects_duplicate_teams(self) -> None:
        validator = BasicMatchValidator()
        match = MatchRecord(
            match_id="TEST-1",
            competition="Test League",
            season="2024",
            kickoff=datetime(2024, 1, 1, tzinfo=timezone.utc),
            home_team="Same Team",
            away_team="Same Team",
            home_score=1,
            away_score=1,
            venue=None,
            surface=None,
            weather=None,
            home_form=0.5,
            away_form=0.5,
        )
        with self.assertRaises(ValueError):
            validator.validate(match)

    def test_transformer_uses_default_competition(self) -> None:
        transformer = MatchTransformer(default_competition="Liga MX")
        raw = {
            "id": "LIGA-100",
            "season": "2024",
            "kickoff": "2024-03-14T02:00:00+00:00",
            "home": {"name": "Club America", "form": "0.7"},
            "away": {"name": "Pumas", "form": 0.6},
        }

        match = transformer.transform(raw)

        self.assertEqual(match.competition, "Liga MX")
        self.assertEqual(match.home_form, 0.7)
        self.assertEqual(match.away_form, 0.6)
        self.assertEqual(match.home_score, None)
        self.assertIsNotNone(match.kickoff.tzinfo)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
