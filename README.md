# Anti-G Project Blueprint

Anti-G is a multi-repository initiative focused on building a production-grade football match prediction and betting optimization platform. This repository serves as the umbrella project plan that orchestrates the data, modeling, and betting strategy services required for profitable wagering on gambling sites.

## Program Objectives

1. **Predictive Accuracy** – Design machine-learning services that leverage historical performance, squad conditions, contextual metadata (venue, turf, weather, schedule), and circular match information to forecast football match outcomes and derived markets (1X2, BTTS, totals, handicaps).
2. **Market Exploitation** – Continuously scrape regulated bookmakers, detect mispriced odds, and synthesize betting tickets that maximize risk-adjusted return given bankroll and market constraints.
3. **Operational Excellence** – Deliver an automated, observable, and secure platform that can be deployed to production-grade infrastructure with CI/CD, feature governance, and compliance guardrails.

## Workstreams & Repository Layout

| Repository | Focus | Key Responsibilities |
|------------|-------|----------------------|
| [`repos/data-pipeline`](repos/data-pipeline/README.md) | Data acquisition & quality | Scrape fixtures, results, injuries, player metrics, bookmaker odds; orchestrate ETL, validations, and storage. |
| [`repos/feature-engineering`](repos/feature-engineering/README.md) | Feature store & analytics | Transform raw data into model-ready datasets, maintain feature catalog, handle circular and contextual signals. |
| [`repos/prediction-service`](repos/prediction-service/README.md) | Machine learning | Build, train, evaluate, and serve predictive models (classification, probabilistic, simulation-based). |
| [`repos/betting-optimizer`](repos/betting-optimizer/README.md) | Betting strategy engine | Scrape odds, compare against predicted edges, generate optimal bet combinations per risk profile. |
| [`repos/platform-infra`](repos/platform-infra/README.md) | Infrastructure & DevOps | Manage infrastructure-as-code, CI/CD, observability, secrets, and MLOps tooling. |

Supporting documentation lives in [`docs/`](docs/) and includes the delivery roadmap, system architecture, and governance processes.

## Delivery Roadmap

See [`docs/roadmap.md`](docs/roadmap.md) for a phased execution plan that covers discovery, MVP delivery, scaling, and optimization milestones.

## Collaboration Guidelines

- Treat each directory under `repos/` as an independent codebase with its own lifecycle, tooling, and deployment target.
- Use trunk-based development within each repository; adopt feature branches per workstream when collaborating.
- Enforce automated testing, linting, and data-quality checks through CI pipelines defined in each repo.
- Follow the documented coding standards and modeling best practices in `docs/` before contributing.

## Next Steps

1. Align stakeholders on roadmap milestones and budget allocation.
2. Prioritize data acquisition tasks that unlock model prototyping (fixtures, results, injuries, betting odds).
3. Stand up the data-pipeline repository and implement incremental ingestion jobs.
4. Deliver an MVP prediction model and calibrate it against bookmaker odds for selected leagues.
5. Iterate on betting optimization strategies and integrate bankroll management.

For detailed architectural decisions and technology selections, consult [`docs/architecture.md`](docs/architecture.md).
