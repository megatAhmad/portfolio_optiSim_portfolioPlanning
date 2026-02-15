# CLAUDE.md - Enterprise Portfolio Optimization Platform

## Project Overview

Cloud-native, AI-augmented multi-year portfolio optimization platform for energy and capital-intensive industries. Replaces static spreadsheet-based planning with stochastic modeling and constraint-based solvers to maximize portfolio value under fiscal and environmental uncertainty.

**Primary market:** Oil & gas companies with $500M+ annual capex budgets.
**Secondary markets:** Utilities, mining, renewable energy developers, energy-sector private equity.

**Key differentiators vs. competitors (PlanningSpace Portfolio / Product Y):**
1. Network-aware interdependency modeling at scale (500+ projects with shared infrastructure, synergies, resource constraints)
2. Native stochastic optimization (SDDP) — not a separate tool
3. Integrated real options valuation (binomial lattice, Longstaff-Schwartz LSM)
4. Unified energy transition portfolio optimization (hydrocarbons + renewables + decommissioning)
5. C-suite executive UX with narrative insights and visual portfolio storytelling

**Current state:** Pre-development. Only `README.md`, `prd.md`, and `.gitignore` exist. All source code must be created from scratch. Refer to `prd.md` for the full Product Requirements Document (3,959 lines).

---

## Tech Stack

### Backend (Python 3.11+)
- **API Framework:** FastAPI with Uvicorn
- **ORM / DB Access:** SQLAlchemy + Alembic (migrations) + Pydantic (validation)
- **Database:** PostgreSQL with TimescaleDB extension (time-series optimization results)
- **Cache:** Redis (scenario results, optimization cache)
- **Task Queue:** Celery with Redis broker (long-running optimizations)
- **Optimization:**
  - Pyomo (algebraic modeling language for MILP)
  - Gurobi (primary commercial MILP solver — requires license, ~$100K/yr commercial)
  - Google OR-Tools (open-source fallback for freemium tier / <200 projects)
  - SciPy / CVXPY (convex optimization)
- **Stochastic Optimization:** Custom SDDP (Stochastic Dual Dynamic Programming) implementation
- **Real Options:** Custom binomial lattice + Longstaff-Schwartz LSM implementation
- **Data Processing:** Pandas, NumPy, Polars
- **Graph Analysis:** NetworkX (dependency modeling, cycle detection, topological sort, centrality)
- **ML / Surrogate Modeling:** Scikit-learn, XGBoost
- **Linting:** Ruff
- **Type Checking:** mypy (strict mode)
- **Testing:** Pytest, Coverage.py, Locust (load testing)

### Frontend (TypeScript)
- **Framework:** Next.js 14+ (React, SSR/SSG)
- **State Management:** Zustand or Redux Toolkit
- **Visualization:** Recharts (charts), D3.js (network dependency diagrams), Plotly React (3D Pareto frontiers), React Flow (decision trees)
- **UI Components:** shadcn/ui or Ant Design
- **Tables:** TanStack Table (formerly React Table)
- **Forms:** React Hook Form + Zod (validation)
- **API Client:** TanStack Query (React Query)

### Infrastructure
- **Cloud:** AWS or Azure (multi-region)
- **Compute:** ECS/Fargate or Kubernetes (API servers), EC2 spot instances (optimization workers)
- **Storage:** S3 / Blob Storage (scenario archives, exports)
- **CDN:** CloudFront / Azure CDN
- **CI/CD:** GitHub Actions
- **IaC:** Terraform
- **Monitoring:** DataDog or New Relic
- **Containerization:** Docker

---

## Architecture Overview

```
CLIENT LAYER (Browser)
  Next.js App (React) — Executive Dashboard, Scenario Builder
      |
      | HTTPS / WebSocket
      v
API GATEWAY (FastAPI)
  Authentication, Rate Limiting, Request Routing
      |
      +-------------------+--------------------+
      |                   |                    |
      v                   v                    v
  Data Service      Optimization Service    Analytics Service
  - Import          - MILP Solver           - Monte Carlo
  - Validate        - SDDP Engine           - Sensitivity
  - Transform       - Real Options          - Risk Metrics
  - Graph Analysis  - Multi-Objective       - Reporting
                    - Temporal State Mgmt
                          |
                          v
                    Celery Workers
                    (Async Tasks)
                          |
      +-------------------+--------------------+
      |                   |                    |
      v                   v                    v
  PostgreSQL/        Redis Cache          S3/Blob Storage
  TimescaleDB
```

Three backend services communicate through the FastAPI gateway:
1. **Data Service** — project import/validation/transformation, graph analysis (NetworkX), expression engine evaluation
2. **Optimization Service** — MILP model construction (Pyomo), solver dispatch (Gurobi/OR-Tools), temporal state management, dependency constraint generation, SDDP, real options, multi-objective
3. **Analytics Service** — Monte Carlo simulation, sensitivity analysis (tornado charts), risk metrics (CVaR, VaR), reporting/export (Excel, PowerPoint, PDF)

Long-running optimizations and Monte Carlo simulations are dispatched to Celery workers. Results stored in TimescaleDB hypertables for fast time-series queries. Dashboard queries use continuous aggregates.

---

## Planned Directory Structure

```
/
├── CLAUDE.md
├── README.md
├── prd.md
├── .gitignore
├── docker-compose.yml
├── Makefile
│
├── backend/
│   ├── pyproject.toml                  # Python project config (deps, ruff, mypy)
│   ├── alembic.ini
│   ├── alembic/
│   │   └── versions/                   # Database migration files
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                     # FastAPI app entry point
│   │   ├── config.py                   # Settings via pydantic-settings
│   │   ├── dependencies.py             # FastAPI dependency injection
│   │   │
│   │   ├── api/                        # Route handlers
│   │   │   ├── v1/
│   │   │   │   ├── projects.py
│   │   │   │   ├── scenarios.py
│   │   │   │   ├── optimization.py
│   │   │   │   ├── analytics.py
│   │   │   │   ├── dependencies_api.py # Project interdependencies CRUD
│   │   │   │   ├── price_decks.py
│   │   │   │   ├── reports.py
│   │   │   │   └── auth.py
│   │   │   └── router.py
│   │   │
│   │   ├── models/                     # SQLAlchemy ORM models
│   │   │   ├── project.py              # Opportunity, Outcome, OpportunityMetricTimeSeries
│   │   │   ├── dependency.py           # SelectionDependency, SelectionGroup, GroupMember
│   │   │   ├── scenario.py             # Scenario, ScenarioInput, ScenarioResult
│   │   │   ├── price_deck.py           # PriceDeck, MasterDataSet, MasterDataMetric
│   │   │   ├── constraint.py           # SelectionConstraint, MetricConstraint
│   │   │   ├── expression.py           # MetricExpression
│   │   │   ├── optimization_result.py  # TimescaleDB hypertable model
│   │   │   └── user.py
│   │   │
│   │   ├── schemas/                    # Pydantic request/response schemas
│   │   │   ├── project.py
│   │   │   ├── scenario.py
│   │   │   ├── optimization.py
│   │   │   └── ...
│   │   │
│   │   ├── services/                   # Business logic layer
│   │   │   ├── data_service.py
│   │   │   ├── optimization_service.py
│   │   │   └── analytics_service.py
│   │   │
│   │   ├── optimization/               # Core optimization engine
│   │   │   ├── temporal_state_manager.py   # TimeSeriesStateManager class
│   │   │   ├── hybrid_optimizer.py         # HybridPortfolioOptimizer class
│   │   │   ├── milp_builder.py             # Pyomo ConcreteModel construction
│   │   │   ├── solver_interface.py         # Gurobi / OR-Tools abstraction layer
│   │   │   ├── constraint_generators.py    # Selection, dependency, group, metric constraints
│   │   │   ├── linearization.py            # Big-M reformulations for max/min
│   │   │   ├── sddp_engine.py             # Stochastic Dual Dynamic Programming (P1)
│   │   │   ├── real_options.py             # Binomial lattice + LSM (P2)
│   │   │   └── multi_objective.py          # Pareto frontier generation (P1)
│   │   │
│   │   ├── expression_engine/          # PlanningSpace-compatible formula system
│   │   │   ├── registry.py             # ExpressionRegistry, MetricDefinition
│   │   │   ├── compiler.py             # FormulaCompiler (AST-based, security-validated)
│   │   │   └── executor.py             # ExecutionEngine (topological sort evaluation)
│   │   │
│   │   ├── graph/                      # Dependency graph operations
│   │   │   ├── dependency_graph.py     # NetworkX DiGraph builder
│   │   │   ├── cycle_detection.py      # Circular dependency detection + reporting
│   │   │   └── constraint_converter.py # Graph edges → Pyomo MILP constraints
│   │   │
│   │   ├── importers/                  # Data import modules
│   │   │   ├── excel_importer.py       # PlanningSpace Excel template parser (openpyxl)
│   │   │   ├── csv_importer.py
│   │   │   └── validators.py           # Import validation rules
│   │   │
│   │   └── tasks/                      # Celery async tasks
│   │       ├── optimization_tasks.py
│   │       ├── monte_carlo_tasks.py
│   │       └── report_tasks.py
│   │
│   └── tests/
│       ├── conftest.py
│       ├── unit/
│       │   ├── test_temporal_state_manager.py
│       │   ├── test_hybrid_optimizer.py
│       │   ├── test_linearization.py
│       │   ├── test_constraint_generators.py
│       │   ├── test_expression_engine.py
│       │   ├── test_dependency_graph.py
│       │   └── ...
│       ├── integration/
│       │   ├── test_optimization_pipeline.py
│       │   ├── test_api_scenarios.py
│       │   └── ...
│       └── fixtures/
│           ├── sample_portfolio_10.json
│           ├── sample_portfolio_500.json
│           └── planningspace_template.xlsx
│
├── frontend/
│   ├── package.json
│   ├── tsconfig.json
│   ├── next.config.js
│   ├── tailwind.config.ts
│   ├── src/
│   │   ├── app/                        # Next.js App Router
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx
│   │   │   ├── dashboard/
│   │   │   ├── projects/
│   │   │   ├── scenarios/
│   │   │   ├── optimization/
│   │   │   ├── analytics/
│   │   │   └── settings/
│   │   ├── components/
│   │   │   ├── ui/                     # shadcn/ui primitives
│   │   │   ├── charts/                 # Recharts wrappers
│   │   │   ├── network/                # D3.js / React Flow dependency graph
│   │   │   ├── pareto/                 # Plotly 3D Pareto explorer
│   │   │   └── forms/
│   │   ├── lib/
│   │   │   ├── api/                    # TanStack Query hooks + API client
│   │   │   ├── store/                  # Zustand stores
│   │   │   └── utils/
│   │   └── types/                      # TypeScript type definitions
│   └── tests/
│
├── infrastructure/
│   ├── terraform/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── modules/
│   ├── docker/
│   │   ├── Dockerfile.backend
│   │   ├── Dockerfile.frontend
│   │   └── Dockerfile.worker
│   └── k8s/                            # Kubernetes manifests (if applicable)
│
└── .github/
    └── workflows/
        ├── ci.yml
        ├── deploy-staging.yml
        └── deploy-production.yml
```

---

## Development Workflow

### Backend

```bash
# Setup
cd backend
pip install -e ".[dev]"              # or: uv sync --dev

# Run API server
uvicorn app.main:app --reload --port 8000

# Run Celery worker
celery -A app.tasks worker --loglevel=info

# Database migrations
alembic upgrade head                 # Apply all migrations
alembic revision --autogenerate -m "description"

# Linting and formatting
ruff check .                         # Lint
ruff check . --fix                   # Auto-fix
ruff format .                        # Format

# Type checking
mypy app/

# Testing
pytest                               # All tests
pytest tests/unit/                   # Unit only
pytest tests/integration/            # Integration only
pytest --cov=app --cov-report=term-missing  # With coverage
pytest -x -v                         # Stop on first failure

# Full CI check (run before committing)
ruff check . && ruff format --check . && mypy app/ && pytest --cov=app
```

### Frontend

```bash
cd frontend
npm install
npm run dev                          # Dev server (port 3000)
npm run build                        # Production build
npm run lint                         # ESLint
npm run type-check                   # TypeScript strict
npm run test
```

### Docker

```bash
docker-compose up                    # All services (API, worker, DB, Redis)
docker-compose up -d                 # Detached
docker-compose down                  # Stop all
```

---

## Key Conventions

### Python Backend
1. **Async-first API:** All FastAPI route handlers must be `async def`.
2. **Pydantic at all boundaries:** Request/response schemas, config, data validation. SQLAlchemy models are internal only.
3. **Repository pattern:** Database access through repository classes, not directly in route handlers.
4. **Service layer:** Business logic in `services/`, not in route handlers or models.
5. **Type annotations everywhere:** Full annotations on all functions. mypy strict mode enforced.
6. **Error handling:** Domain-specific exceptions (e.g., `OptimizationInfeasibleError`, `ProjectNotFoundError`); FastAPI exception handlers convert to HTTP responses.
7. **Logging:** Structured JSON output via `structlog` or standard `logging`. No `print()` in production code.
8. **Testing:** >80% coverage target. Every optimization algorithm must have a known-answer test with hand-verified solution.

### Naming Conventions
- **Python:** `snake_case` for variables/functions/modules; `PascalCase` for classes; `UPPER_SNAKE_CASE` for constants
- **TypeScript:** `camelCase` for variables/functions; `PascalCase` for components/types/interfaces
- **API endpoints:** REST with plural nouns: `/api/v1/projects`, `/api/v1/scenarios/{id}/optimize`
- **Database tables:** `snake_case`, plural: `opportunities`, `selection_dependencies`, `optimization_results`
- **Files:** `snake_case` for Python; kebab-case or PascalCase for React components

### Git
- Branch naming: `feature/description`, `fix/description`, `refactor/description`
- Commit messages: imperative mood, concise (e.g., "Add temporal state manager with Big-M linearization")
- PRs require passing CI (lint, type-check, tests) before merge

---

## Domain Terminology

### Financial / Energy Industry
- **CAPEX** — Capital Expenditure (upfront investment required for a project)
- **OPEX** — Operating Expenditure (ongoing costs)
- **NPV** — Net Present Value (sum of discounted future cash flows)
- **IRR** — Internal Rate of Return
- **EUR** — Estimated Ultimate Recovery (total recoverable oil/gas reserves)
- **P10/P50/P90** — Probability percentiles (P50 = median, P10 = 10% chance of exceeding)
- **PSC** — Production Sharing Contract (fiscal regime type)
- **Price Deck** — Commodity price forecast over the planning horizon (oil, gas, NGL, power, carbon credits)
- **Working Interest (WI)** — Fractional ownership of a project (0.0 to 1.0+)
- **Shadow Price** — Value of relaxing a constraint by one unit (MILP dual variable)
- **Stranded Asset** — Asset that becomes uneconomic before end of life (e.g., due to carbon pricing)
- **Reserve Replacement Ratio** — New reserves added / production depleted

### Optimization
- **MILP** — Mixed Integer Linear Programming (continuous + binary/integer variables)
- **SDDP** — Stochastic Dual Dynamic Programming (multi-stage optimization under uncertainty)
- **CVaR** — Conditional Value at Risk (expected loss in worst X% of scenarios)
- **VaR** — Value at Risk (threshold loss at a confidence level)
- **Pareto Frontier** — Set of non-dominated solutions in multi-objective optimization
- **Big-M Reformulation** — Linearization technique using large constant M + auxiliary binary variables
- **MIP Gap** — Distance between best found solution and theoretical optimum (lower = better; target 0.1%)
- **State Variable** — Explicit variable for system state at each (project, year, metric) triplet
- **Temporal Constraint** — Constraint linking state variables across adjacent time periods (e.g., `debt[t] = debt[t-1]*(1+r) + capex[t] - cashflow[t]`)
- **Formula Explosion** — Exponential growth from recursive formula evaluation (the core problem our architecture solves)
- **Lazy Constraint Generation** — Adding detailed constraints only for selected/promising projects
- **Temporal Aggregation** — Reducing time resolution for distant years (annual → biennial → quinquennial; 30 years → 18 time periods)

### Project Interdependency Types
- **Prerequisite** — Project A must complete before Project B can start (with optional time lag in years)
- **Mutual Exclusivity (Mutex)** — At most one project from a set can be selected
- **Synergy** — Combined value exceeds sum of individual values (e.g., shared facilities reduce CAPEX by $50M)
- **Shared Infrastructure** — Projects compete for limited physical capacity (platform slots, pipeline throughput)
- **Resource Constraint** — Projects compete for limited resources (drilling rigs, personnel, budget)
- **Market Constraint** — Combined production from a project set cannot exceed market capacity

### PlanningSpace Compatibility (Data Model Terms)
- **Opportunity** — An investment project/asset (our "Project" entity)
- **Outcome** — A probabilistic scenario for an opportunity (e.g., Base/Optimistic/Pessimistic with weights summing to 1.0)
- **Fixture** — A Master Data assignment record (special attribute row linking opportunities to shared data sets)
- **Master Data Set** — Shared time-series parameters applied to multiple opportunities via attribute matching (e.g., "High Price" deck applies to all opportunities with `price_scenario="High"`)
- **FYF** — First Year Formula (formula for t=0; cannot reference prior time)
- **PT** — Prior Time reference (value at t-1; used in CT formulas)
- **CT** — Current Time formula (formula for t>0; can reference PT and current metrics)
- **Level** — Aggregation level: `O` (Outcome), `P` (Project/Opportunity), `S` (Scenario)
- **Selection Group** — Named group of projects with collective constraints (Exclusive, Inclusive, At Least N, At Most N, Exactly N)
- **Metric Constraint** — Portfolio-level limit on any calculated metric (hard or soft with penalty weight)

---

## Key Architectural Decisions

These decisions are non-negotiable and must be followed throughout development.

### 1. Explicit Temporal State Variables (NOT Recursion)

**The single most important architectural decision.** All time-dependent metrics must use explicit state variables indexed by (project, year, metric), linked by linear temporal constraints. Never use recursive function calls for multi-year calculations.

```python
# CORRECT: Explicit state variable with linear temporal constraint
model.debt = Var(model.projects, model.years, domain=NonNegativeReals)

def debt_evolution(model, p, t):
    if t == 0:
        return model.debt[p, 0] == 0
    return (model.debt[p, t] ==
            model.debt[p, t-1] * (1 + rate) +
            model.capex[p, t] - model.cashflow[p, t])

# WRONG: Recursive formulation (causes formula explosion)
def debt(project, year):
    if year == 0: return 0
    return debt(project, year-1) + new_debt[year] - repayment[year]
```

**Why:** 500 projects x 30 years with recursive formulas = infinite computational explosion. State variables create a finite, solvable 150K-variable MILP. Use the `TimeSeriesStateManager` class for all state variable creation.

### 2. Graph Theory (NetworkX) + MILP Hybrid

Two-phase approach for dependency modeling:
- **Phase 1 — Graph:** Build a NetworkX `DiGraph` representing project interdependencies. Use graph algorithms for cycle detection, topological sort, critical path analysis, centrality, and visualization data generation.
- **Phase 2 — MILP:** Convert graph edges to Pyomo MILP constraints for optimization. Each edge type (prerequisite, mutex, synergy, shared_infra, resource) maps to specific constraint patterns.

### 3. Hybrid Pre-Computation for Independent Projects

In typical portfolios, 70-90% of projects have no interdependencies:
- **Independent projects:** Pre-compute standalone NPV as a scalar (O(1) lookup during optimization). Only need a binary selection variable.
- **Interdependent projects:** Full state variable treatment with temporal constraints.
- **Result:** 60-80% fewer optimization variables; 5-10x faster solve times; identical optimality.

### 4. Big-M Linearization for Max/Min

All non-linear max/min operations must be converted to linear constraints using auxiliary binary variables and Big-M constants. Required because MILP solvers need all constraints to be linear.

```python
# max(a, b) linearization:
# z >= a, z >= b (z is at least as large as both)
# z <= a + M*(1-y), z <= b + M*y (binary y selects which is active)
```

Choose M carefully using domain-specific bounds (e.g., `max_debt = sum(capex_schedule)`). Too large → numerical issues; too small → incorrect results.

### 5. TimescaleDB for Time-Series Results

Optimization results `(scenario_id, project_id, year) → metrics` are stored in TimescaleDB hypertables. Use continuous aggregates for dashboard queries (total CAPEX/revenue/production per scenario per year). Never store time-series in regular PostgreSQL tables.

### 6. Solver Abstraction (Gurobi Primary, OR-Tools Fallback)

All solver interactions go through `solver_interface.py`. Never call Gurobi APIs directly from service or route layers. The interface handles automatic fallback from Gurobi → OR-Tools if Gurobi is unavailable. Always extract and return solver statistics (solve time, MIP gap, iterations, variable/constraint counts).

### 7. Expression Engine (PlanningSpace Compatible)

The expression engine evaluates computed metrics using PlanningSpace-compatible formula syntax:
- `[Metric Name]` references for input metrics and Master Data
- FYF/PT/CT formula pattern: FYF at t=0, CT for t>0 with PT referencing t-1
- Built-in functions: `Total()`, `TotalDisc()`, `IF()`, `MAX()`, `MIN()`, `SUM()`, `GetCumulative()`
- Topological sort of metric dependency graph determines evaluation order
- AST-based compilation with security validation (block `eval`, `exec`, `import`, `__import__`, `open`)
- Compiled formulas cached for reuse
- Filter by attribute/characteristic/opportunity/outcome; aggregate by level (O/P/S)

### 8. Hard vs. Soft Constraints

Two constraint modes for metric constraints:
- **Hard:** Must be satisfied. Infeasible if violated. Standard MILP constraint.
- **Soft:** Can be violated with penalty. Uses slack variables added to constraints and penalty terms in objective function: `penalty = weight * (slack / magnitude)`. Enables trade-offs between constraint satisfaction and objective value.

---

## Constraint System

Four constraint types, all converted to Pyomo MILP constraints:

### Selection Constraints
Per-project: integer/continuous selection, working interest bounds (min/max WI), instance limits (total and per-year), yearly timing windows.

### Selection Dependencies
Between projects: prerequisite (with time offset and timing relation), mutual exclusivity (Must Not), instance ratios (N real/normalized parents : M children).

### Selection Groups
Named groups of projects with collective rules: Exclusive (at most 1), Inclusive (all or nothing), At Least N, At Most N, Exactly N. Group-level instance and yearly constraints.

### Metric Constraints
Portfolio-level limits on any computed metric (e.g., annual CAPEX max $1B, minimum production plateau 397,000 boe/d). Support both hard enforcement and soft enforcement with configurable penalty weight and magnitude.

---

## Development Phases and Priorities

### P0 / MVP (Months 1-7) — BUILD FIRST
Core deterministic optimization — implement this first.
- **Foundation (Months 1-3):** Infrastructure setup, core data models, database schema (all tables from Section 8.4 of PRD), auth (SSO/RBAC), basic FastAPI framework, React UI shell, project import from Excel/CSV
- **MVP (Months 4-7):**
  - Project library (500+ projects) with full attribute system
  - Economic assumptions: price decks, fiscal regimes, Master Data Sets with attribute-based linking
  - Basic interdependency modeling (prerequisites, mutex)
  - Expression engine (PlanningSpace-compatible FYF/PT/CT formulas, dependency analysis, topological evaluation)
  - Deterministic MILP optimization (Pyomo + Gurobi/OR-Tools)
  - `TimeSeriesStateManager` and `HybridPortfolioOptimizer`
  - 4 constraint types: selection, dependency, group, metric (hard + soft)
  - 5 metric constraint categories: CAPEX annual/cumulative, production, emissions, infrastructure
  - Single objective: maximize NPV
  - Scenario builder: create/save/run/compare scenarios
  - Sensitivity analysis: tornado charts, one-way sensitivity
  - Executive dashboard: key metrics cards, CAPEX/production/emissions charts, portfolio composition views
  - Basic Excel export and reporting
- **Success criteria:** 200-project portfolio solved in <3 min; 3 pilot customers onboarded

### P1 / Phase 2 (Months 8-12)
Key differentiators vs. incumbents.
- Advanced interdependencies: shared infrastructure capacity, synergy quantification, resource constraints
- Network visualization (D3.js / React Flow interactive graph with force-directed layout)
- Multi-objective optimization with Pareto frontier (epsilon-constraint / weighted sum; 20-30 Pareto-optimal portfolios)
- Energy transition: mixed hydrocarbon + renewables optimization, carbon pricing scenarios, transition pathway visualization (2030/2040/2050)
- Monte Carlo simulation (1,000 scenarios with Latin Hypercube Sampling, correlated commodity prices)
- PowerPoint auto-generation, detailed Excel models, AI-generated narrative summaries
- Multi-user collaboration (WebSocket real-time updates, role-based views)
- Audit trail and governance (scenario certification, data lineage)
- **Success criteria:** 15 paying customers; win 2 competitive deals vs. Product Y

### P2 / Phase 3 (Months 13-18)
Advanced analytics and technical leadership.
- Stochastic optimization: two-stage stochastic programming, SDDP, scenario tree generation/reduction (1,000 → 20-50 representative), CVaR risk constraints, recourse decisions
- Real options valuation: option to defer/abandon/expand/contract/switch, compound options for multi-stage projects, binomial lattice + Longstaff-Schwartz LSM
- AI/ML: surrogate models for fast approximate optimization, scenario clustering, anomaly detection in project data
- Approval workflows (Analyst → Manager → Executive), Slack/Teams integration
- **Success criteria:** 40 customers; stochastic optimization adopted by 60%

### P3 / Phase 4 (Months 19-24)
Enterprise scale.
- 2,000+ project support, distributed optimization, GPU-accelerated Monte Carlo
- SOC 2 Type II certification
- Custom report builder (drag-and-drop), scheduled/automated reports, API for external BI tools
- Industry expansion: mining, utilities, private equity fund portfolio modules
- **Success criteria:** 75 customers; $50M ARR

---

## Non-Functional Requirements

| Category | Requirement | Target |
|----------|------------|--------|
| **API Response** | p95 latency | <200ms |
| **Dashboard** | Load time | <2 seconds |
| **Optimization** | 500-project deterministic MILP, 30 years, 20 constraints | <5 minutes |
| **Stochastic** | 200-project, 3 stages, 50 scenarios | <30 minutes |
| **Monte Carlo** | 1,000 scenarios | <10 minutes |
| **Concurrent Users** | Without degradation | 50+ |
| **Import** | 500-project Excel | <2 minutes |
| **Scalability** | MVP / Future | 500 / 2,000+ projects |
| **Uptime** | MVP / Production | 99.5% / 99.9% |
| **Test Coverage** | Code coverage | >80% |
| **Security** | Encryption at rest / in transit | AES-256 / TLS 1.3 |
| **Auth** | MFA required, SSO via SAML 2.0 (Okta, Azure AD) | All users |
| **Accessibility** | WCAG compliance | 2.1 AA |
| **Compliance** | SOC 2 Type II | Within 18 months |
| **MIP Gap** | Optimality tolerance | 0.1% (99.9% optimal) |

---

## Important Patterns

### Temporal State Manager Pattern
When adding any new time-dependent metric to the optimization model:
1. Call `TimeSeriesStateManager.create_state_variable()` to create the `(project, year)` indexed Pyomo `Var`.
2. Call `link_temporal_constraint()` with an evolution function linking year `t` to year `t-1`.
3. Provide an initial condition function for `t=0` (defaults to 0).
4. For bounds tightening, compute domain-specific upper bounds (e.g., `max_debt = sum(capex_schedule)`).

### Dependency Constraint Generation Pattern
When adding new interdependency types:
1. Add edge type to the NetworkX `DiGraph` with appropriate metadata kwargs.
2. Implement constraint generation in `constraint_generators.py` following existing patterns for prerequisites, mutex, synergy, shared_infra.
3. For synergy/interaction effects, create linearized interaction binary variable: `interaction <= select[A]`, `interaction <= select[B]`, `interaction >= select[A] + select[B] - 1`.
4. Test with a small (5-10 project) hand-verified portfolio.

### Solver Abstraction Pattern
1. Build the Pyomo `ConcreteModel` with all variables and constraints.
2. Call `solver_interface.solve(model, solver_preference="gurobi")`.
3. Interface handles Gurobi → OR-Tools fallback automatically.
4. Always extract solver stats: `{solve_time, mip_gap, iterations, num_variables, num_constraints, precomputed_projects, optimization_method}`.

### Expression Evaluation Pipeline
1. Register all metrics in `ExpressionRegistry` (Input, Master Data, Computed).
2. Registry auto-extracts `[Metric Name]` dependencies from formulas via regex.
3. `_build_execution_order()` performs topological sort on the dependency graph.
4. `FormulaCompiler` transforms PlanningSpace syntax to Python AST with security validation.
5. `ExecutionEngine.evaluate_all_metrics()` evaluates in topological order: FYF at t=0, CT for t>0.
6. Results cached by `(metric_name, opportunity, outcome, year, level)`.

### API Design Pattern
- All endpoints versioned under `/api/v1/`.
- Long-running operations (optimization, Monte Carlo, report generation) return a task ID immediately; clients poll or use WebSocket for status updates.
- Response format for lists: `{"data": [...], "meta": {"total": N, "page": P}}`
- Error format: `{"error": {"code": "OPTIMIZATION_INFEASIBLE", "message": "...", "details": {...}}}`

---

## Testing Guidelines

1. **Known-answer tests:** Every optimization algorithm must include a small test case (5-10 projects) where the optimal solution is hand-verified. Verify objective value, selected projects, and timing.
2. **Solver equivalence:** Run the same problem on both Gurobi and OR-Tools; verify objective values match within MIP gap tolerance.
3. **Temporal state correctness:** Verify that state variables (debt, production, emissions) at each year match manual forward calculation.
4. **Constraint enforcement:** For each constraint type (selection, dependency, group, metric), verify the solver cannot produce solutions that violate the constraint.
5. **Soft constraint behavior:** Verify slack variables activate appropriately and penalty terms correctly degrade the objective.
6. **Expression engine:** Validate formula evaluation against known PlanningSpace spreadsheet results for: Revenue = Production * Price, Cumulative Production with PT, NPV via TotalDisc, conditional IF formulas.
7. **Import validation:** Test Excel import against sample PlanningSpace template files; verify outcome weights sum to 1.0, time series lengths match horizon.
8. **Performance benchmarks:** Track solve time for 10-project, 100-project, and 500-project portfolios. Regression if >2x increase.

---

## Database Schema

Core tables (see `prd.md` Section 8.4 for full DDL):

| Table | Purpose |
|-------|---------|
| `opportunities` | Investment projects with type, business unit, location |
| `outcomes` | Probabilistic scenarios per opportunity (Base/Optimistic/Pessimistic) with weights |
| `opportunity_metrics` | Input time-series data per opportunity-outcome-metric (JSONB arrays) |
| `opportunity_attributes` | Flexible attributes + PlanningSpace fixture support + custom JSONB |
| `master_data_sets` | Named parameter sets (e.g., "High Price") with category and applicability |
| `master_data_metrics` | Time-series values within Master Data Sets (optional stochastic distributions) |
| `metric_expressions` | Computed metric formulas (FYF/PT/CT/Total/TotalDisc) with level and filters |
| `selection_constraints` | Per-project: integer flag, WI bounds, instance limits, yearly timing windows |
| `selection_dependencies` | Between projects: Must/Must Not, time offset, timing relation, instance ratios |
| `selection_groups` | Named groups: Exclusive/Inclusive/At Least N type, member list |
| `group_members` | M:N relationship between groups and opportunities |
| `metric_constraints` | Portfolio-level limits: hard/soft, penalty weight/magnitude, yearly overrides |
| `optimization_results` | **TimescaleDB hypertable** — (scenario, project, year) → financial + production metrics |

Key indexes:
- `idx_scenario_project_year ON optimization_results(scenario_id, project_id, year)` — fast scenario queries
- `idx_scenario_selected ON optimization_results(scenario_id, is_selected)` — quick filtered views
- Continuous aggregate `portfolio_summary` — pre-computed totals by scenario and year for dashboard

---

## Key Reference Files

| Section | PRD Lines | Content |
|---------|-----------|---------|
| Competitive Analysis | 24-197 | 8 gaps vs. PlanningSpace; feature parity table; migration strategy |
| Tech Stack & Architecture | 287-373 | Full stack listing; system architecture diagram |
| Temporal State Management | 375-857 | **Critical**: state variable formulation, Big-M linearization, graph-based dependencies, hybrid optimizer, performance strategies, complexity analysis |
| Data Management Features | 860-932 | Project library, interdependency network, economic assumptions requirements |
| Optimization Engine | 935-1083 | Deterministic MILP, stochastic (SDDP), multi-objective, real options requirements |
| Scenario & Sensitivity | 1086-1150 | Scenario builder, Monte Carlo, risk metrics requirements |
| Visualization & Reporting | 1153-1258 | Executive dashboard, network viz, Pareto explorer, exports |
| Energy Transition | 1262-1296 | Mixed portfolio, carbon pricing, transition pathways, stranded assets |
| Data Models (Python) | 1407-1620 | Project, Dependency, Scenario, PriceDeck Pydantic models |
| PlanningSpace-Compatible Structures | 1715-2602 | Input data, attributes, Master Data, expressions, selection constraints/dependencies/groups, metric constraints — all with database schemas and MILP formulations |
| Database Schema (SQL) | 2606-2767 | Full DDL for all core tables + TimescaleDB hypertable + indexes |
| Expression Engine Architecture | 2817-3470 | **Critical**: ExpressionRegistry, FormulaCompiler (AST), ExecutionEngine — full implementation with code samples |
| Development Roadmap | 3472-3631 | Phase 0-4 deliverables, team sizes, success criteria |
| Architectural Decisions | 3723-3836 | Rationale for all 6 key decisions with trade-off analysis |
| Glossary | 3863-3910 | All domain terms defined |
