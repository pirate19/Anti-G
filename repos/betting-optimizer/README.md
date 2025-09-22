# Betting Optimizer Repository

## Mission
Leverage predictive insights and live bookmaker data to build an automated betting recommendation engine that maximizes risk-adjusted returns while adhering to regulatory constraints.

## Scope
- **Odds Acquisition**: Scrape and aggregate prices, limits, and market availability across targeted bookmakers.
- **Edge Calculation**: Compare model-derived probabilities vs. odds to detect value bets, accounting for overround and vig removal.
- **Portfolio Optimization**: Construct single and multi-leg tickets using optimization techniques (integer programming, heuristics, simulation) aligned with bankroll strategies.
- **Risk Controls**: Enforce staking rules, exposure limits, and compliance checks (jurisdiction, responsible gambling policies).
- **Delivery**: Provide APIs, alerting systems, and dashboards for recommended bets and performance tracking.

## Proposed Stack
- **Languages**: Python for optimization, Node.js or Python for API delivery.
- **Scraping**: Playwright, Selenium, or bookmaker APIs with proxy & captcha handling.
- **Optimization**: OR-Tools, PuLP, cvxpy, or Pyomo; Monte Carlo simulations for scenario testing.
- **APIs/UI**: FastAPI backend, React/Next.js or Streamlit for dashboards.
- **Monitoring**: Custom telemetry for bet execution, ROI tracking, and alerting.

## Directory Structure
```
src/
  odds/
    collectors/
    normalizers/
  edge/
    calculators/
    margin_adjustment/
  optimizer/
    ticket_builders/
    bankroll/
    simulations/
  delivery/
    api/
    notifications/
    dashboard/
  utils/
config/
  bookmakers/
  optimization/
notebooks/
  strategy_research/
```

## Initial Milestones
1. Build odds collection service for two primary bookmakers with redundancy and latency monitoring.
2. Implement edge calculation pipeline referencing prediction-service outputs.
3. Prototype bankroll management strategies (Kelly, fixed stake) and evaluate historical performance.
4. Develop optimization engine producing recommended singles and accumulator tickets.
5. Create reporting dashboard to visualize ROI, hit rate, and exposure by league/market.

## Compliance & Ethics
- Log all scraping activity and adhere to bookmaker terms of service; integrate kill switch for legal escalations.
- Provide transparent rationale for each bet recommendation (probabilities, edge, stake suggestion).
- Enforce configurable betting limits aligned with responsible gambling guidelines.
