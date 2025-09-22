# Data Pipeline Repository

## Mission
Build resilient ingestion and transformation workflows that consolidate all football and betting-related data sources into trusted datasets for downstream modeling and optimization.

## Scope
- **Source Integration**: Fixtures, historical results, player stats, injuries/suspensions, team news, weather, betting odds, and market limits.
- **Ingestion Modes**: REST APIs, websocket feeds, headless browser scraping, CSV ingestion, third-party webhooks.
- **Processing**: Batch (hourly/daily) and near-real-time pipelines orchestrated via Airflow/Dagster.
- **Data Lakehouse**: Bronze (raw), silver (validated), gold (aggregated) layers with schema evolution support.
- **Quality Assurance**: Automated validation suites, anomaly detection, latency SLAs, data contract enforcement.

## Proposed Stack
- **Language**: Python 3.11+
- **Orchestration**: Apache Airflow or Dagster
- **Storage**: S3/GCS for files, Snowflake/BigQuery/Postgres for structured tables
- **Validation**: Great Expectations, Soda Core
- **Testing**: pytest, dbt tests for transformations
- **Infrastructure**: Dockerized tasks, Kubernetes/ECS deployment

## Directory Structure
```
src/
  ingestion/
    adapters/        # Source-specific connectors (APIs, scrapers)
    schedules/       # Airflow DAGs or Dagster jobs
  processing/
    transformations/ # dbt or Pandas/SQL transformations
    validations/     # Data quality suites
  utils/             # Shared helpers (logging, retry logic)
config/
  credentials/       # Encrypted secrets references (Vault/SM)
  schemas/           # JSON schemas for validation
notebooks/
  exploration/       # Data profiling and exploratory analysis
```

## Initial Milestones
1. Finalize list of priority leagues, markets, and bookmakers.
2. Stand up ingestion DAGs for fixtures/results and odds for top leagues.
3. Implement bronze→silver normalization with schema tests.
4. Automate quality checks and alerting for data latency/missingness.
5. Document data contracts and publish sample datasets for modeling team.

## Key Risks & Mitigations
- **Website Blocking**: Employ rotating proxies, captcha solvers, and fall back to paid APIs.
- **Schema Drift**: Implement contract tests with automated alerts and fallback parsers.
- **Latency**: Prioritize asynchronous scraping and incremental updates to meet pre-match windows.
- **Compliance**: Maintain legal review of scraping activities, respect robots.txt where applicable.

## Development Setup
1. Create and activate a virtual environment targeting Python 3.10+.
2. Install the project in editable mode (append `.[dev]` if you prefer to work with pytest):
   ```bash
   pip install -e .
   ```
3. Execute the unit test suite:
   ```bash
   python -m unittest discover -s tests
   ```

## Quickstart
The repository ships with a thin ingestion pipeline that demonstrates how we will normalize raw
fixtures into curated JSON Lines artifacts. To try it locally:

```bash
cd repos/data-pipeline
python -m data_pipeline.pipeline
```

By default the pipeline will read from the sample dataset in `tests/data/sample_matches.json` and
write the normalized matches to `./artifacts/matches.jsonl`.
