"""Ingestion orchestration."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import List, Sequence

from .ingestion import SourceAdapter
from .models import MatchRecord, PipelineError, PipelineResult
from .processing.transformations import MatchTransformer
from .processing.validations import BasicMatchValidator
from .storage import JsonLinesSink


class IngestionPipeline:
    """Minimal ingestion pipeline for transforming and persisting matches."""

    def __init__(
        self,
        adapter: SourceAdapter,
        transformer: MatchTransformer | None = None,
        validators: Sequence[BasicMatchValidator] | None = None,
        sink: JsonLinesSink | None = None,
        logger: logging.Logger | None = None,
    ) -> None:
        self._adapter = adapter
        self._transformer = transformer or MatchTransformer()
        self._validators = list(validators or [BasicMatchValidator()])
        self._sink = sink or JsonLinesSink("./artifacts/matches.jsonl")
        self._logger = logger or logging.getLogger(__name__)

    def run(self) -> PipelineResult:
        processed = 0
        failed = 0
        errors: List[PipelineError] = []
        output_locations: List[str] = []

        with self._sink as sink:
            output_locations.append(str(sink.path))
            for raw in self._adapter.load():
                identifier = _extract_identifier(raw)
                try:
                    match = self._transformer.transform(raw)
                    self._apply_validators(match)
                    sink.write(match)
                    processed += 1
                except Exception as exc:  # pragma: no cover - logging path
                    failed += 1
                    reason = str(exc)
                    errors.append(PipelineError(identifier=identifier, reason=reason))
                    self._logger.warning("Failed to process record %s: %s", identifier, reason)

        return PipelineResult(
            processed=processed,
            failed=failed,
            errors=errors,
            output_locations=output_locations,
        )

    def _apply_validators(self, match: MatchRecord) -> None:
        for validator in self._validators:
            validator.validate(match)


def _extract_identifier(raw: object) -> str:
    if isinstance(raw, dict):
        for key in ("id", "match_id", "uuid"):
            value = raw.get(key)
            if isinstance(value, str) and value:
                return value
    return "<unknown>"


def main() -> None:  # pragma: no cover - exercised manually
    """Run the sample ingestion pipeline."""

    from .ingestion import StaticJSONAdapter

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    project_root = Path(__file__).resolve().parents[3]
    sample_path = project_root / "tests" / "data" / "sample_matches.json"
    if not sample_path.exists():
        raise SystemExit(
            "Sample dataset not found. Expected to locate tests/data/sample_matches.json"
        )

    pipeline = IngestionPipeline(adapter=StaticJSONAdapter(sample_path))
    result = pipeline.run()

    logging.info(
        "Processed %s records (%s failed)",
        result.processed,
        result.failed,
    )
    logging.info("Outputs written to: %s", ", ".join(result.output_locations))
    if result.failed:
        for error in result.errors:
            logging.error("%s -> %s", error.identifier, error.reason)


if __name__ == "__main__":  # pragma: no cover - module CLI
    main()
