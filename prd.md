# Product Requirements Document (PRD)
## Enterprise Portfolio Optimization Platform

**Version:** 1.0  
**Date:** February 10, 2026  
**Status:** Draft  
**Owner:** Product Strategy Team

---

## Executive Summary

### Product Vision
Build the world's most advanced multi-year portfolio optimization platform that combines mathematical rigor with practical usability, enabling C-suite executives to maximize enterprise value across complex, interdependent asset portfolios spanning traditional energy and low-carbon investments.

### Market Opportunity
- **Primary Market:** Oil & gas companies with $500M+ annual capex budgets
- **Secondary Markets:** Utilities, mining, renewable energy developers, private equity (energy sector)
- **Market Gap:** No existing tool combines (1) true interdependency modeling at scale, (2) embedded stochastic optimization, (3) real options valuation, and (4) energy transition portfolio management


---

## 1. Competitive Analysis: Product X Feature Gaps

### 1.1 Market Leader Analysis

**Product Y Planning Space Portfolio (formerly Product X)** dominates the purpose-built oil & gas portfolio optimization market with comprehensive features and petroleum-specific workflows. Our analysis of their data templates and documentation reveals both their strengths and critical gaps we can exploit.

### 1.2 Product X's Core Strengths

| Feature Category | Product X Capability | Market Impact |
|-----------------|-------------------|---------------|
| **Excel-based workflow** | Familiar templates for petroleum engineers | Industry standard, low adoption barrier |
| **Expression system** | Powerful FYF/PT/CT formula syntax | Handles complex time-dependent metrics |
| **Constraint modeling** | 4 constraint types (selection, dependency, group, metric) | Comprehensive business rule coverage |
| **Probabilistic outcomes** | Multiple weighted outcomes per project | Models geological uncertainty |
| **Master data management** | Global parameters with scenario variants | Efficient price deck/toll management |
| **Flexible attributes** | User-defined project categorization | Customizable to any organizational structure |
| **Integration** | Native PlanningSpace ecosystem | Seamless Product Y product suite |

### 1.3 Critical Gaps & Our Differentiation Strategy

#### **Gap 1: No Dependency Visualization** ⭐ HIGH IMPACT
**Product X Limitation:**
- Dependencies defined in text tables only
- No visual representation of prerequisite chains
- Cannot see network structure or critical paths
- Cycle detection requires manual inspection

**Our Opportunity:**
- Interactive graph visualization (D3.js/React Flow)
- Automatic critical path highlighting
- Real-time cycle detection with warnings
- Visual dependency builder (drag-and-drop)
- Impact analysis: "What becomes infeasible if I remove Project X?"

**Business Impact:** Executives can see portfolio structure at a glance, reducing planning time from weeks to hours.

#### **Gap 2: Stochastic Optimization Requires Separate Tool** ⭐ HIGH IMPACT
**Product X Limitation:**
- Deterministic optimization in Portfolio
- Monte Carlo requires separate PetroVR product
- Separate workflows, data export/import
- Different UI, learning curve
- Additional licensing cost

**Our Opportunity:**
- Native Monte Carlo in core platform
- Stochastic programming with recourse decisions
- Unified workflow (optimize under uncertainty)
- Scenario tree visualization
- CVaR and risk-based optimization

**Business Impact:** 15-25% higher portfolio value by capturing flexibility and avoiding worst-case scenarios.

#### **Gap 3: No Real Options Support** ⭐ HIGH IMPACT
**Product X Limitation:**
- Static NPV only
- Cannot value flexibility (defer, abandon, expand)
- Misses 20-40% of value in exploration portfolios
- No compound option modeling

**Our Opportunity:**
- Embedded real options valuation (binomial lattice, LSM)
- Option to defer, abandon, expand, contract, switch
- Compound options for multi-stage projects
- Integrated into portfolio optimization

**Business Impact:** Capture $50M-$200M in option value for typical major's exploration portfolio.

#### **Gap 4: Limited Energy Transition Support** ⭐ HIGH IMPACT
**Product X Limitation:**
- Hydrocarbon-focused
- No unified optimization of oil/gas + renewables
- Cannot model portfolio transition pathways
- Missing carbon pricing optimization

**Our Opportunity:**
- Mixed portfolio optimization (fossil + renewables)
- Transition pathway visualization (2030, 2040, 2050)
- Net-zero constraint optimization
- Stranded asset risk assessment
- Technology transition scenarios

**Business Impact:** Critical for 2025+ as companies commit to net-zero targets.

#### **Gap 5: Manual Sensitivity Analysis** ⚠️ MEDIUM IMPACT
**Product X Limitation:**
- Must create scenarios manually for sensitivity
- No automated tornado charts
- Time-consuming for multi-dimensional sensitivity
- Difficult to identify key value drivers

**Our Opportunity:**
- One-click tornado chart generation
- Automated scenario sweep (price, CAPEX, reserves)
- Multi-way sensitivity surface plots
- AI-powered key driver identification

**Business Impact:** Reduce sensitivity analysis from 2 days to 10 minutes.

#### **Gap 6: Excel Scalability Limits** ⚠️ MEDIUM IMPACT
**Product X Limitation:**
- Excel template → ~500 project practical limit
- 1M row Excel limit constrains large portfolios
- Performance degrades with 30+ year horizons
- Manual data validation until import

**Our Opportunity:**
- Database-native design (PostgreSQL + TimescaleDB)
- 2,000+ projects supported
- Real-time validation with line-by-line feedback
- No Excel constraints

**Business Impact:** Support enterprise-scale portfolios (e.g., Shell has 1,200+ active projects globally).

#### **Gap 7: No Collaborative Features** ⚠️ MEDIUM IMPACT
**Product X Limitation:**
- Single-user editing
- No real-time collaboration
- Comment threads only
- Manual version merging

**Our Opportunity:**
- Multi-user simultaneous editing
- Real-time updates (WebSocket)
- Approval workflows (Analyst → Manager → Executive)
- Activity feed and notifications

**Business Impact:** Reduce planning cycle time by 30-40% through parallel work.

#### **Gap 8: Weak Network Optimization** ⚠️ MEDIUM IMPACT
**Product X Limitation:**
- Simple prerequisite dependencies only
- No shared infrastructure capacity modeling
- Cannot optimize network flows
- Limited multi-project synergy quantification

**Our Opportunity:**
- Full network optimization (graph-based)
- Shared infrastructure capacity constraints (platform slots, pipeline throughput)
- Synergy value quantification and optimization
- Network flow algorithms

**Business Impact:** Capture $20M-$100M in infrastructure sharing synergies.

### 1.4 Feature Parity + Differentiation Summary

| Category | Product X | Us | Advantage |
|----------|---------|----|-----------| 
| **Data Import** | ✅ Excel templates | ✅ Excel + API + DB | ⚖️ Parity + more options |
| **Expression System** | ✅ FYF/PT/CT formulas | ✅ Compatible + Python | ⚖️ Parity + flexibility |
| **Constraints** | ✅ 4 types comprehensive | ✅ Same + visual builders | ⚖️ Parity + UX |
| **Dependencies** | ✅ Text tables | ✅ Same + graph viz | 🎯 **We win** |
| **Deterministic Optimization** | ✅ MILP, mature | ✅ Same (Gurobi) | ⚖️ Parity |
| **Stochastic Optimization** | ⚠️ Separate PetroVR | ✅ Native integration | 🎯 **We win** |
| **Real Options** | ❌ Not supported | ✅ Embedded | 🎯 **We win** |
| **Energy Transition** | ⚠️ Limited | ✅ Core feature | 🎯 **We win** |
| **Sensitivity Analysis** | ⚠️ Manual | ✅ Automated | 🎯 **We win** |
| **Scalability** | ⚠️ ~500 projects | ✅ 2,000+ projects | 🎯 **We win** |
| **Collaboration** | ⚠️ Single user | ✅ Real-time multi-user | 🎯 **We win** |
| **Master Data** | ✅ Scenarios | ✅ Same + stochastic | 🎯 **We win** |

**Strategic Positioning:** "Everything Product X does, plus modern capabilities they can't deliver"

### 1.5 Migration Strategy for Product X Users

**Seamless Transition Plan:**

1. **Import Wizard:** Upload Product X Excel templates → Automatic conversion
2. **Validation:** Side-by-side comparison (results should match within solver tolerance)
3. **Enhancement Discovery:** Guided tour of new capabilities (graph viz, stochastic, real options)
4. **Parallel Operation:** Run both tools during transition period for validation
5. **Full Migration:** Switch to our platform once confidence established

**Key Message:** "Keep your existing workflows, data, and expertise. Add next-generation capabilities."

---

## 2. Product Overview

### 2.1 Problem Statement

Current portfolio optimization tools suffer from critical limitations:

1. **Interdependency blindness** — treat projects as independent when real portfolios have massive infrastructure sharing and resource competition
2. **Static optimization** — use deterministic assumptions then simulate uncertainty, missing flexibility value worth 15-25% of portfolio NPV
3. **NPV tunnel vision** — ignore real options, asymmetric risk profiles, and strategic value dimensions
4. **Energy transition gap** — cannot optimize unified portfolios spanning hydrocarbons and renewables with fundamentally different characteristics
5. **Poor C-suite UX** — built for petroleum engineers, not strategic decision-makers

### 2.2 Solution Summary

An AI-augmented, cloud-native portfolio optimization platform featuring:

- **Network-aware optimization** — models up to 500 interdependent projects with shared infrastructure, resource constraints, and sequencing dependencies
- **Stochastic optimization with recourse** — optimizes under uncertainty with dynamic decision trees, not post-hoc Monte Carlo
- **Integrated real options valuation** — captures option value of waiting, abandoning, expanding, or switching at the portfolio level
- **Multi-dimensional value framework** — quantifies financial, ESG, strategic, and risk metrics on a common scale
- **Energy transition optimizer** — unified optimization across conventional and low-carbon portfolios
- **Executive decision interface** — purpose-built for C-suite with narrative insights, what-if in seconds, and visual portfolio storytelling

---

## 3. Target Users & Personas

### Primary Personas

**1. Chief Strategy Officer (CSO) / VP Corporate Development**
- **Goals:** Maximize long-term enterprise value, manage portfolio risk, communicate strategy to board
- **Pain Points:** Can't see interdependencies across divisions, struggle to compare apples-to-oranges (upstream vs. renewables)
- **Success Metric:** Confidence in capital allocation recommendations backed by data

**2. Chief Financial Officer (CFO)**
- **Goals:** Optimize capital deployment, meet financial covenants, manage investor expectations
- **Pain Points:** Static NPV doesn't capture real flexibility, can't model conditional funding strategies
- **Success Metric:** Portfolio delivers financial targets with acceptable risk profile

**3. VP Planning & Economics / Portfolio Manager**
- **Goals:** Generate optimal portfolio recommendations, run scenarios quickly, defend recommendations with rigor
- **Pain Points:** Manual scenario analysis takes weeks, can't model complex constraints, tools aren't trusted by executives
- **Success Metric:** Produce defensible portfolio recommendations 10x faster

### Secondary Personas

**4. Director of Sustainability / ESG Lead**
- **Goals:** Integrate emissions constraints, demonstrate climate strategy alignment
- **Pain Points:** ESG metrics treated as afterthought, not integrated into optimization

**5. Asset Manager / Business Unit Lead**
- **Goals:** Get fair capital allocation, understand portfolio competition dynamics
- **Pain Points:** Allocation feels political rather than analytical

---

## 4. Core Value Propositions

### 5.1 For C-Suite Executives
- **10x faster strategic decisions** — what-if scenarios in seconds, not weeks
- **15-30% portfolio value improvement** — capture interdependency synergies and option value missed by incumbents
- **Risk-aware optimization** — explicit uncertainty modeling with confidence intervals
- **Unified energy strategy** — optimize across traditional and transition investments
- **Boardroom-ready outputs** — executive dashboards and narrative explanations

### 3.2 For Portfolio Managers
- **True mathematical optimization** — provably optimal portfolios, not just ranked lists
- **500+ project capacity** — enterprise-scale with real interdependencies
- **Rapid scenario iteration** — test 100+ scenarios in minutes
- **Full audit trail** — every recommendation defensible and traceable

### 3.3 Competitive Differentiation

| Capability | Our Platform | Product Y Planning Space | IFS Copperleaf | Generic PPM |
|------------|--------------|----------------------|----------------|-------------|
| Interdependency modeling (50+ projects) | ✅ Network optimization | ⚠️ Limited | ❌ Asset-focused | ❌ No |
| Stochastic optimization | ✅ Native SDDP/MSP | ❌ Deterministic + MC | ❌ Deterministic | ❌ No |
| Real options integration | ✅ Embedded | ❌ No | ❌ No | ❌ No |
| Energy transition portfolios | ✅ Core feature | ⚠️ Emerging | ❌ Utilities only | ❌ No |
| Multi-objective optimization | ✅ Pareto frontier | ⚠️ Single objective | ✅ Value Framework | ⚠️ Basic |
| C-suite UX | ✅ Purpose-built | ⚠️ Technical | ✅ Strong | ⚠️ Varies |
| Petroleum domain models | ✅ Built-in | ✅ Industry-leading | ❌ No | ❌ No |
| 20+ year horizons | ✅ Yes | ✅ Yes | ✅ Yes | ⚠️ Varies |

---

## 5. Technical Architecture

### 5.1 Technology Stack

**Backend (Python)**
- **Core Framework:** FastAPI (async, high-performance API)
- **Optimization Engine:** 
  - Pyomo (algebraic modeling)
  - Gurobi (MILP solver, requires license)
  - OR-Tools (open-source alternative/fallback)
  - Scipy/CVXPY (convex optimization)
- **Stochastic Optimization:** Custom implementation of Stochastic Dual Dynamic Programming (SDDP)
- **Real Options:** Custom binomial lattice and Longstaff-Schwartz LSM implementation
- **Data Processing:** Pandas, NumPy, Polars
- **Monte Carlo:** NumPy with multiprocessing
- **Machine Learning:** Scikit-learn, XGBoost (for surrogate modeling)
- **Database:** PostgreSQL (time-series data, projects, scenarios)
- **Cache:** Redis (scenario results, optimization cache)
- **Task Queue:** Celery (long-running optimizations)
- **Time Series:** TimescaleDB extension

**Frontend (React)**
- **Framework:** Next.js 14+ (React with SSR/SSG)
- **State Management:** Zustand or Redux Toolkit
- **Data Visualization:**
  - Recharts (charts/graphs)
  - D3.js (network diagrams for interdependencies)
  - Plotly React (3D Pareto frontiers)
  - React Flow (decision tree visualization)
- **UI Components:** shadcn/ui or Ant Design
- **Tables:** TanStack Table (formerly React Table)
- **Forms:** React Hook Form + Zod validation
- **API Client:** TanStack Query (React Query)

**Infrastructure**
- **Cloud Platform:** AWS or Azure (multi-region)
- **Compute:** 
  - API servers: ECS/Fargate or Kubernetes
  - Optimization workers: EC2 spot instances (cost-optimized)
- **Storage:** S3/Blob Storage (scenario archives, exports)
- **CDN:** CloudFront/Azure CDN
- **Monitoring:** DataDog or New Relic
- **CI/CD:** GitHub Actions
- **IaC:** Terraform

**Integration Layer**
- **Data Import:** CSV, Excel (openpyxl), Parquet, JSON
- **API Connectors:** REST APIs for Product Y, PHDWin, ARIES (where available)
- **Export:** Excel (detailed models), PowerPoint (executive summaries), PDF

### 5.2 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     CLIENT LAYER (Browser)                   │
│  Next.js App (React) - Executive Dashboard, Scenario Builder│
└────────────────────┬────────────────────────────────────────┘
                     │ HTTPS/WebSocket
┌────────────────────┴────────────────────────────────────────┐
│                   API GATEWAY (FastAPI)                      │
│  Authentication, Rate Limiting, Request Routing              │
└─────┬──────────────────────────────────────────────┬────────┘
      │                                               │
      ├──────────────────────┬────────────────────────┤
      │                      │                        │
┌─────▼──────┐      ┌───────▼────────┐      ┌────────▼────────┐
│ Data       │      │ Optimization    │      │ Analytics       │
│ Service    │      │ Service         │      │ Service         │
│            │      │                 │      │                 │
│ • Import   │      │ • MILP Solver   │      │ • Monte Carlo   │
│ • Validate │      │ • SDDP Engine   │      │ • Sensitivity   │
│ • Transform│      │ • Real Options  │      │ • Risk Metrics  │
│ • Graph    │      │ • Multi-Obj     │      │ • Reporting     │
│   Analysis │      │ • Temporal      │      │                 │
└─────┬──────┘      │   State Mgmt    │      └────────┬────────┘
      │             └────────┬────────┘               │
      │                      │                        │
      │             ┌────────▼────────┐               │
      │             │ Celery Workers  │               │
      │             │ (Async Tasks)   │               │
      │             └────────┬────────┘               │
      │                      │                        │
┌─────▼──────────────────────▼────────────────────────▼────────┐
│              DATA LAYER                                       │
│  PostgreSQL/TimescaleDB    Redis Cache    S3/Blob Storage    │
└───────────────────────────────────────────────────────────────┘
```

### 5.3 Temporal State Management Architecture

**Challenge:** Multi-year portfolio optimization with interdependencies creates a computational explosion problem. When calculating Enterprise Value at year 30 for 500 projects where metrics depend on previous years' values, naive recursive formulations create formulas that expand exponentially (30-level recursion × 500 projects = computational nightmare).

**Solution:** State Variable Architecture with Graph-Augmented MILP

#### 4.3.1 Core Design Principles

**1. Explicit State Variables (Not Recursion)**
Replace recursive formula expansion with explicit variables for each (project, year, metric) combination:

```python
# ❌ WRONG: Recursive formulation (explodes)
def debt(project, year):
    if year == 0:
        return 0
    return debt(project, year-1) + new_debt[year] - repayment[year]

# ✅ CORRECT: State variable formulation (linear)
model.debt = Var(model.projects, model.years, domain=NonNegativeReals)

def debt_evolution(model, p, t):
    if t == 0:
        return model.debt[p, 0] == 0
    return (model.debt[p, t] == 
            model.debt[p, t-1] * (1 + interest_rate) +
            model.capex[p, t] - model.cashflow[p, t])
```

**Why this works:**
- Creates 500 projects × 30 years = 15,000 debt variables
- Each linked by simple linear constraint
- Solver handles sparse matrices efficiently
- No recursive calculation

**2. Linearization of Non-Linear Constraints**
Convert max/min and product operations to linear constraints using auxiliary variables:

```python
# For: operating_cost = max(base_cost, min_threshold)

model.operating_cost = Var(model.projects, model.years, domain=NonNegativeReals)
model.use_threshold = Var(model.projects, model.years, domain=Binary)

# Big-M reformulation
M = 1e9

def operating_cost_constraints(model, p, t):
    # operating_cost >= both options
    yield model.operating_cost[p, t] >= model.base_cost[p, t]
    yield model.operating_cost[p, t] >= model.min_threshold[p]
    
    # operating_cost <= base_cost OR min_threshold (enforced via binary)
    yield (model.operating_cost[p, t] <= 
           model.base_cost[p, t] + M * (1 - model.use_threshold[p, t]))
    yield (model.operating_cost[p, t] <= 
           model.min_threshold[p] + M * model.use_threshold[p, t])
```

**3. Graph Theory for Interdependency Modeling**
Use NetworkX to model dependencies, then convert to MILP constraints:

```python
# Step 1: Build dependency graph
import networkx as nx

G = nx.DiGraph()
G.add_edge('Project_A', 'Project_B', type='prerequisite', lag=1)
G.add_edge('Project_C', 'Project_D', type='synergy', capex_reduction=50e6)

# Step 2: Convert to MILP constraints
for (source, target) in G.edges():
    edge_data = G[source][target]
    
    if edge_data['type'] == 'prerequisite':
        # If target selected, source must be selected first
        model.add_constraint(
            model.select[source] >= model.select[target]
        )
    
    elif edge_data['type'] == 'synergy':
        # Linearize: synergy_active = select[source] AND select[target]
        model.add_constraint(
            model.synergy_active[source, target] <= model.select[source]
        )
        model.add_constraint(
            model.synergy_active[source, target] <= model.select[target]
        )
        model.add_constraint(
            model.synergy_active[source, target] >= 
            model.select[source] + model.select[target] - 1
        )
        
        # Apply synergy impact
        for t in model.years:
            model.add_constraint(
                model.capex_reduction[target, t] == 
                edge_data['capex_reduction'] * model.synergy_active[source, target]
            )
```

#### 4.3.2 Implementation Architecture

```python
# /backend/optimization/temporal_state_manager.py

from pyomo.environ import *
import networkx as nx

class TimeSeriesStateManager:
    """
    Manages temporal state variables efficiently for multi-year portfolio optimization.
    Prevents exponential formula expansion by using explicit state variables.
    """
    
    def __init__(self, num_projects, num_years):
        self.num_projects = num_projects
        self.num_years = num_years
        self.state_vars = {}
        self.dependency_graph = nx.DiGraph()
    
    def create_state_variable(self, model, var_name, domain=Reals, 
                            bounds=None, initialize=None):
        """
        Create state variable for all (project, year) combinations.
        
        Args:
            var_name: Name of the variable (e.g., 'debt', 'production')
            domain: Pyomo domain (Reals, NonNegativeReals, Binary, etc.)
            bounds: Optional (lower, upper) bounds tuple
            initialize: Optional initial values
        
        Returns:
            Pyomo Var object
        """
        var = Var(
            range(self.num_projects), 
            range(self.num_years), 
            domain=domain,
            bounds=bounds,
            initialize=initialize
        )
        setattr(model, var_name, var)
        self.state_vars[var_name] = var
        return var
    
    def link_temporal_constraint(self, model, var_name, evolution_fn, 
                                initial_condition_fn=None):
        """
        Add constraints linking year t to year t-1.
        
        Args:
            var_name: Name of state variable
            evolution_fn: Function(model, p, t) returning constraint expression
            initial_condition_fn: Optional function for t=0, defaults to 0
        """
        var = self.state_vars[var_name]
        
        def temporal_rule(model, p, t):
            if t == 0:
                if initial_condition_fn:
                    return initial_condition_fn(model, p)
                else:
                    return var[p, 0] == 0  # Default: zero initial condition
            else:
                return evolution_fn(model, p, t)
        
        constraint_name = f"{var_name}_evolution"
        constraint = Constraint(
            range(self.num_projects), 
            range(self.num_years), 
            rule=temporal_rule
        )
        setattr(model, constraint_name, constraint)
        return constraint
    
    def add_dependency(self, source_project, target_project, 
                      dependency_type, **kwargs):
        """
        Add interdependency between projects to graph.
        
        Args:
            source_project: Source project ID
            target_project: Target project ID
            dependency_type: 'prerequisite', 'mutex', 'synergy', 'shared_infra'
            **kwargs: Additional parameters (e.g., capex_reduction=50e6)
        """
        self.dependency_graph.add_edge(
            source_project, 
            target_project,
            type=dependency_type,
            **kwargs
        )
    
    def generate_dependency_constraints(self, model):
        """
        Convert dependency graph to MILP constraints.
        """
        for (source, target) in self.dependency_graph.edges():
            edge_data = self.dependency_graph[source][target]
            dep_type = edge_data['type']
            
            if dep_type == 'prerequisite':
                # If target selected, source must be selected
                constraint_name = f"prereq_{source}_{target}"
                constraint = Constraint(
                    expr=(model.select[source] >= model.select[target])
                )
                setattr(model, constraint_name, constraint)
            
            elif dep_type == 'mutex':
                # At most one can be selected
                constraint_name = f"mutex_{source}_{target}"
                constraint = Constraint(
                    expr=(model.select[source] + model.select[target] <= 1)
                )
                setattr(model, constraint_name, constraint)
            
            elif dep_type == 'synergy':
                # Create linearized interaction variable
                interaction_name = f"synergy_{source}_{target}"
                interaction_var = Var(domain=Binary)
                setattr(model, interaction_name, interaction_var)
                
                # Linearization constraints
                setattr(model, f"{interaction_name}_c1",
                       Constraint(expr=(interaction_var <= model.select[source])))
                setattr(model, f"{interaction_name}_c2",
                       Constraint(expr=(interaction_var <= model.select[target])))
                setattr(model, f"{interaction_name}_c3",
                       Constraint(expr=(interaction_var >= 
                                      model.select[source] + model.select[target] - 1)))
                
                # Apply synergy impact (stored in kwargs)
                # This would be handled by specific constraint functions
                self._apply_synergy_impact(model, source, target, 
                                          interaction_var, edge_data)
    
    def _apply_synergy_impact(self, model, source, target, 
                            interaction_var, edge_data):
        """Apply synergy impact to relevant state variables"""
        if 'capex_reduction' in edge_data:
            reduction = edge_data['capex_reduction']
            # Modify target project's CAPEX based on interaction
            for t in range(self.num_years):
                constraint_name = f"synergy_impact_{source}_{target}_{t}"
                # This assumes model.capex_adjustment exists
                if hasattr(model, 'capex_adjustment'):
                    constraint = Constraint(
                        expr=(model.capex_adjustment[target, t] == 
                              reduction * interaction_var)
                    )
                    setattr(model, constraint_name, constraint)


# /backend/optimization/hybrid_optimizer.py

class HybridPortfolioOptimizer:
    """
    Hybrid optimizer that pre-computes independent projects and uses
    state variables only for interdependent projects.
    
    Performance: Reduces variables by 60-80% for typical portfolios.
    """
    
    def __init__(self, projects, dependency_graph):
        self.projects = projects
        self.dependency_graph = dependency_graph
        
        # Separate independent and interdependent projects
        nodes_with_edges = set(dependency_graph.nodes())
        self.independent_projects = [
            p for p in projects if p.id not in nodes_with_edges
        ]
        self.interdependent_projects = [
            p for p in projects if p.id in nodes_with_edges
        ]
        
        print(f"Independent projects: {len(self.independent_projects)}")
        print(f"Interdependent projects: {len(self.interdependent_projects)}")
    
    def precompute_independent_projects(self, price_deck, discount_rate):
        """
        Pre-calculate NPV for projects with no dependencies.
        Massive performance gain: O(1) lookup vs. O(years) computation per project.
        """
        standalone_npvs = {}
        
        for project in self.independent_projects:
            cashflows = []
            for year in range(30):
                revenue = project.revenue_forecast[year] * price_deck[year]
                opex = project.opex_profile[year]
                capex = project.capex_schedule[year]
                cf = revenue - opex - capex
                cashflows.append(cf)
            
            npv = sum(cf / (1 + discount_rate)**t 
                     for t, cf in enumerate(cashflows))
            standalone_npvs[project.id] = npv
        
        return standalone_npvs
    
    def build_optimization_model(self, standalone_npvs, num_years=30):
        """
        Build MILP model with hybrid approach.
        """
        model = ConcreteModel()
        
        # Sets
        model.indep_projects = Set(initialize=[p.id for p in self.independent_projects])
        model.dep_projects = Set(initialize=[p.id for p in self.interdependent_projects])
        model.years = RangeSet(0, num_years - 1)
        
        # Decision variables - simple binary for independent projects
        model.select_indep = Var(model.indep_projects, domain=Binary)
        model.select_dep = Var(model.dep_projects, domain=Binary)
        
        # State variables - ONLY for interdependent projects
        state_manager = TimeSeriesStateManager(
            len(self.interdependent_projects), 
            num_years
        )
        
        # Create state variables
        model.revenue = state_manager.create_state_variable(
            model, 'revenue', domain=NonNegativeReals
        )
        model.opex = state_manager.create_state_variable(
            model, 'opex', domain=NonNegativeReals
        )
        model.capex = state_manager.create_state_variable(
            model, 'capex', domain=NonNegativeReals
        )
        model.debt = state_manager.create_state_variable(
            model, 'debt', domain=NonNegativeReals
        )
        
        # Add temporal evolution constraints
        def debt_evolution(model, p, t):
            interest_rate = 0.05
            return (model.debt[p, t] == 
                   model.debt[p, t-1] * (1 + interest_rate) +
                   model.capex[p, t] - 
                   (model.revenue[p, t] - model.opex[p, t]))
        
        state_manager.link_temporal_constraint(model, 'debt', debt_evolution)
        
        # Generate dependency constraints
        state_manager.generate_dependency_constraints(model)
        
        # Objective: Maximize total portfolio NPV
        def portfolio_npv(model):
            # Independent projects: use pre-computed NPV (O(1) lookup)
            indep_value = sum(
                standalone_npvs[p] * model.select_indep[p]
                for p in model.indep_projects
            )
            
            # Interdependent projects: compute from state variables
            discount_rate = 0.10
            dep_value = sum(
                sum(
                    (model.revenue[p_idx, t] - model.opex[p_idx, t] - model.capex[p_idx, t]) 
                    / (1 + discount_rate)**t
                    for t in model.years
                ) * model.select_dep[p_id]
                for p_idx, p_id in enumerate(model.dep_projects)
            )
            
            return indep_value + dep_value
        
        model.objective = Objective(rule=portfolio_npv, sense=maximize)
        
        return model, state_manager


# Example usage
if __name__ == "__main__":
    # Initialize state manager
    manager = TimeSeriesStateManager(num_projects=500, num_years=30)
    
    model = ConcreteModel()
    model.projects = RangeSet(0, 499)
    model.years = RangeSet(0, 29)
    model.select = Var(model.projects, domain=Binary)
    
    # Create state variables
    manager.create_state_variable(model, 'debt', domain=NonNegativeReals)
    manager.create_state_variable(model, 'production', domain=NonNegativeReals)
    manager.create_state_variable(model, 'emissions', domain=NonNegativeReals)
    
    # Add dependencies
    manager.add_dependency(10, 25, 'prerequisite')
    manager.add_dependency(15, 20, 'synergy', capex_reduction=50e6)
    manager.add_dependency(30, 35, 'mutex')
    
    # Generate all constraints
    manager.generate_dependency_constraints(model)
    
    # Add temporal evolution
    def debt_evolution(model, p, t):
        return (model.debt[p, t] == 
               model.debt[p, t-1] * 1.05 + 
               model.capex[p, t] - model.cashflow[p, t])
    
    manager.link_temporal_constraint(model, 'debt', debt_evolution)
```

#### 4.3.3 Performance Optimization Strategies

**Strategy 1: Temporal Aggregation**
Reduce resolution for distant years:

```python
# High resolution for near-term (years 0-10): annual
# Medium resolution (years 11-20): 2-year periods  
# Low resolution (years 21-30): 5-year periods

model.years_annual = RangeSet(0, 10)
model.years_biennial = RangeSet(11, 20, 2)  # 11, 13, 15, 17, 19
model.years_quinquennial = RangeSet(21, 30, 5)  # 21, 26

# Reduction: 30 years → 18 time periods (40% fewer variables)
```

**Strategy 2: Lazy Constraint Generation**
Generate detailed constraints only for selected projects:

```python
def optimize_with_lazy_constraints(model, projects):
    # Phase 1: Solve with simplified constraints
    solver = SolverFactory('gurobi')
    solver.solve(model)
    
    # Phase 2: Identify selected projects
    selected = [p for p in projects if model.select[p].value > 0.5]
    
    # Phase 3: Add detailed temporal constraints only for selected projects
    for p in selected:
        for t in range(30):
            add_detailed_constraints(model, p, t)
    
    # Phase 4: Re-solve with full constraints
    solver.solve(model)
```

**Strategy 3: Variable Bounds Tightening**
Use domain knowledge to tighten variable bounds:

```python
# Instead of: debt >= 0 (weak bound)
# Use: debt <= max_possible_debt (tight bound)

def compute_max_debt(project):
    """Maximum debt = cumulative CAPEX if no revenue"""
    return sum(project.capex_schedule)

model.debt = Var(
    model.projects, 
    model.years,
    domain=NonNegativeReals,
    bounds=lambda model, p, t: (0, compute_max_debt(projects[p]))
)

# Result: 20-40% faster solve times with tight bounds
```

#### 4.3.4 Computational Complexity Analysis

| Approach | Variables (500 projects, 30 years) | Constraints | Solve Time | Optimality |
|----------|-------------------------------------|-------------|------------|------------|
| **Naive Recursion** | Infinite (formula explosion) | N/A | ∞ | N/A |
| **Full State Variables** | 150,000 (500×30×10 vars) | 150,000 | 5-15 min | Optimal |
| **Hybrid (80% independent)** | 30,000 (100×30×10 vars) | 30,000 | 1-3 min | Optimal |
| **Temporal Aggregation** | 90,000 (500×18×10 vars) | 90,000 | 2-8 min | Near-optimal |
| **Lazy Constraints** | 15,000 (50 selected×30×10) | 15,000 | 30-90 sec | Optimal |

**Memory footprint:**
- Full state: ~1.2 GB RAM (sparse matrices)
- Hybrid: ~240 MB RAM
- Suitable for standard cloud instances (4-8 GB RAM)

---

## 6. Core Features & Requirements

### 5.1 Data Management

#### 5.1.1 Project Library
**Priority:** P0 (MVP)

**Description:** Central repository for all investment opportunities (projects, assets, initiatives) with comprehensive attributes.

**Functional Requirements:**
- **FR-DM-001:** Support minimum 500 projects per portfolio
- **FR-DM-002:** Project attributes include:
  - Basic: ID, name, type (upstream/midstream/downstream/renewable/decommissioning), business unit, location
  - Economic: CAPEX schedule (multi-year), OPEX profile, revenue forecast, production profile
  - Timing: earliest start date, latest start date, duration, milestones
  - Technical: reserves (P10/P50/P90), EUR, peak production, decline parameters
  - Risk: geological PoS, commercial PoS, execution risk scores
  - ESG: emissions intensity, emissions absolute, safety risk, water usage, biodiversity impact
  - Strategic: strategic alignment score, technology readiness level, competitive moat
- **FR-DM-003:** Version control for project data with full audit trail
- **FR-DM-004:** Bulk import from Excel templates, CSV, API connections
- **FR-DM-005:** Data validation rules (e.g., NPV calculations, date logic, constraint violations)
- **FR-DM-006:** Project templates for common types (exploration well, development project, acquisition, etc.)

**Acceptance Criteria:**
- User can import 500 projects via Excel in <2 minutes
- System validates 100% of financial calculation errors on upload
- Full audit trail shows who changed what and when

#### 5.1.2 Interdependency Network Modeling
**Priority:** P0 (MVP) — **KEY DIFFERENTIATOR**

**Description:** Model complex relationships between projects including shared infrastructure, resource competition, and sequencing requirements.

**Functional Requirements:**
- **FR-DM-007:** Define dependency types:
  - **Prerequisites:** Project A must complete before B can start
  - **Mutual exclusivity:** Only one project from set {A, B, C} can be selected
  - **Shared infrastructure:** Projects share processing capacity, pipeline capacity, platform slots
  - **Synergies:** Project B is more valuable if A is selected (e.g., shared facilities reduce CAPEX)
  - **Resource constraints:** Projects compete for limited drilling rigs, personnel, budget
  - **Market constraints:** Combined production from set {X, Y, Z} cannot exceed market capacity
- **FR-DM-008:** Visual network editor with drag-and-drop dependency creation
- **FR-DM-009:** Automatic cycle detection (prevent circular dependencies)
- **FR-DM-010:** Quantify synergy value (e.g., "Project B saves $50M CAPEX if A is executed first")
- **FR-DM-011:** Infrastructure capacity modeling (e.g., "Platform X has 8 well slots, Projects {A,B,C,D,E} each need 2 slots")
- **FR-DM-012:** Import interdependencies from adjacency matrix or edge list

**Technical Requirements:**
- **TR-DM-001:** Graph database or adjacency list representation for O(1) dependency lookups
- **TR-DM-002:** Dependency validation completes in <5 seconds for 500-project portfolios

**Acceptance Criteria:**
- User can model a 200-project portfolio with 500 interdependencies
- Visual network diagram renders in <3 seconds
- Optimizer correctly enforces all dependency types

#### 5.1.3 Economic Assumptions Library
**Priority:** P0 (MVP)

**Description:** Centralized economic assumptions (price decks, costs, fiscal terms) with scenario management.

**Functional Requirements:**
- **FR-DM-013:** Multi-commodity price decks (oil, gas, NGL, power, carbon credits)
- **FR-DM-014:** Price deck components:
  - Deterministic: single price path
  - Stochastic: price distribution (mean-reverting, GBM, historical simulation)
  - Scenario sets: "Base/Low/High" with probabilities
- **FR-DM-015:** Inflation/escalation curves by category (labor, materials, services)
- **FR-DM-016:** Exchange rate assumptions and correlations
- **FR-DM-017:** Fiscal regime library (royalties, taxes, cost recovery, PSCs) — minimum 20 major regimes
- **FR-DM-018:** Discount rate policies (corporate WACC, project-specific risk adjustments)

---

### 5.2 Optimization Engine

#### 5.2.1 Deterministic Portfolio Optimization
**Priority:** P0 (MVP)

**Description:** Core MILP-based optimization to select projects and timing that maximize objective function subject to constraints.

**Functional Requirements:**
- **FR-OPT-001:** Decision variables:
  - Binary: select project (yes/no)
  - Integer: project start year (or continuous with CAPEX discretization)
- **FR-OPT-002:** Objective functions (user-selectable):
  - Maximize NPV (standard)
  - Maximize NPV per unit CAPEX (capital efficiency)
  - Maximize production (volume-driven)
  - Minimize emissions intensity
  - Custom weighted composite
- **FR-OPT-003:** Constraint types:
  - Annual CAPEX budget (soft or hard)
  - Cumulative CAPEX budget (multi-year)
  - Annual production targets (min/max)
  - Annual revenue targets (min/max)
  - Debt/equity ratios (maximum leverage)
  - Reserve replacement ratio (minimum)
  - Emissions caps (absolute CO2e per year)
  - Resource availability (rigs, personnel)
  - Infrastructure capacity (platform slots, pipeline throughput)
- **FR-OPT-004:** Enforce all interdependency types from FR-DM-007
- **FR-OPT-005:** Support 20+ year planning horizons with annual time steps
- **FR-OPT-006:** Return results:
  - Optimal project selection and timing
  - Objective function value
  - Shadow prices (constraint slack values)
  - Solver statistics (solve time, gap, iterations)

**Technical Requirements:**
- **TR-OPT-001:** Use Gurobi or CPLEX as primary solver
- **TR-OPT-002:** Optimization completes in <5 minutes for 500-project portfolio with 30 years, 20 constraints
- **TR-OPT-003:** MIP gap tolerance: 0.1% (99.9% optimal)
- **TR-OPT-004:** Formulation efficiency: minimize binary variables where possible
- **TR-OPT-005:** Use TimeSeriesStateManager for all temporal variables (prevents formula explosion)
- **TR-OPT-006:** Implement hybrid optimization: pre-compute independent projects, state variables for interdependent projects only
- **TR-OPT-007:** Use sparse matrix representation (Pyomo default) for memory efficiency
- **TR-OPT-008:** Linearize all max/min operations using Big-M reformulation with auxiliary binary variables
- **TR-OPT-009:** Graph-based dependency modeling with NetworkX, converted to MILP constraints

**Acceptance Criteria:**
- Successfully solve 500-project, 20-constraint, 30-year portfolio in <5 min
- Results match hand-calculated optimal solution for 10-project test case
- Shadow prices correctly identify binding constraints
- State variable approach handles recursive dependencies without formula explosion
- Hybrid approach reduces solve time by 60-80% for portfolios with >80% independent projects

#### 5.2.2 Stochastic Optimization with Recourse
**Priority:** P1 (Phase 2) — **KEY DIFFERENTIATOR**

**Description:** Optimize under uncertainty with multi-stage decision trees where later decisions adapt to revealed information.

**Functional Requirements:**
- **FR-OPT-007:** Stochastic parameters:
  - Commodity prices (correlated random walks)
  - Reserves (P10/P50/P90 distributions)
  - CAPEX overruns (lognormal distributions)
  - Geological success (binary)
- **FR-OPT-008:** Two-stage stochastic programming:
  - **Stage 1 (here-and-now):** Select initial projects
  - **Stage 2 (wait-and-see):** Adapt portfolio after uncertainty resolves (e.g., drill exploration well, then decide development)
- **FR-OPT-009:** Scenario tree generation:
  - Monte Carlo sampling (1000+ scenarios)
  - Scenario reduction to 20-50 representative scenarios
  - Maintain statistical properties (mean, variance, correlations)
- **FR-OPT-010:** Optimize expected value across scenarios with risk measures:
  - Expected NPV
  - CVaR (Conditional Value at Risk) at 10% and 5%
  - Probability of achieving minimum return threshold
- **FR-OPT-011:** Recourse decisions modeled:
  - Accelerate/delay project timing based on price realizations
  - Expand/contract production based on market conditions
  - Abandon projects below economic threshold

**Technical Requirements:**
- **TR-OPT-005:** Implement Stochastic Dual Dynamic Programming (SDDP) or Multi-Stage Stochastic Programming (MSP)
- **TR-OPT-006:** Parallel scenario evaluation (distribute across 8+ cores)
- **TR-OPT-007:** Scenario tree size: 20-50 scenarios for tractability
- **TR-OPT-008:** Solve time: <30 minutes for 200-project portfolio, 3 stages, 50 scenarios

**Acceptance Criteria:**
- Stochastic solution demonstrates >5% expected value improvement vs. deterministic with same parameters
- CVaR constraints successfully limit downside risk
- System correctly models recourse decisions (e.g., abandons project when price drops)

#### 5.2.3 Multi-Objective Optimization
**Priority:** P1 (Phase 2)

**Description:** Optimize for multiple conflicting objectives simultaneously and present Pareto-efficient frontier.

**Functional Requirements:**
- **FR-OPT-012:** Simultaneously optimize 2-4 objectives:
  - Financial (NPV, IRR, payback)
  - Production (total volume, peak production)
  - Risk (portfolio volatility, downside risk)
  - ESG (emissions reduction, safety improvement)
  - Strategic (reserve replacement, portfolio diversification)
- **FR-OPT-013:** Generate Pareto frontier showing trade-offs
- **FR-OPT-014:** User can:
  - Select point on Pareto frontier to view corresponding portfolio
  - Set minimum acceptable levels for each objective
  - Explore trade-off curves (e.g., "What NPV do I sacrifice for 20% lower emissions?")
- **FR-OPT-015:** Weighted sum method with user-adjustable weights
- **FR-OPT-016:** Lexicographic optimization (prioritize objectives in order)

**Technical Requirements:**
- **TR-OPT-009:** Generate 20-30 Pareto-optimal portfolios
- **TR-OPT-010:** Use epsilon-constraint method or weighted sum
- **TR-OPT-011:** Interactive Pareto frontier renders in <2 seconds

**Acceptance Criteria:**
- Pareto frontier contains no dominated solutions (all points are efficient)
- User can generate custom portfolio by specifying weights in <30 seconds
- Trade-off curves clearly show marginal rates of substitution

#### 5.2.4 Real Options Valuation
**Priority:** P2 (Phase 3) — **KEY DIFFERENTIATOR**

**Description:** Value and optimize portfolios considering option value of flexibility (defer, abandon, expand, contract, switch).

**Functional Requirements:**
- **FR-OPT-017:** Model real options types:
  - **Option to defer:** Value of waiting for better information before investing
  - **Option to abandon:** Value of exiting project if economics deteriorate
  - **Option to expand:** Value of increasing capacity if demand materializes
  - **Option to contract:** Value of reducing scale if conditions worsen
  - **Option to switch:** Value of converting facility use (e.g., oil to gas)
- **FR-OPT-018:** Compound options for multi-stage projects (exploration → appraisal → development)
- **FR-OPT-019:** Volatility estimation from historical price data
- **FR-OPT-020:** Integrate option values into portfolio NPV calculation
- **FR-OPT-021:** Identify projects where option value > 20% of static NPV

**Technical Requirements:**
- **TR-OPT-012:** Binomial lattice method for American-style options
- **TR-OPT-013:** Longstaff-Schwartz LSM for complex payoff structures
- **TR-OPT-014:** Calibrate volatility from 5+ years historical data
- **TR-OPT-015:** Option valuation completes in <10 seconds per project

**Acceptance Criteria:**
- Real options module values standard exploration play within 5% of academic benchmark
- Portfolio optimization correctly delays projects with high deferral option value
- System identifies minimum 10% of projects where option value exceeds 20% of NPV

---

### 5.3 Scenario Management & Analysis

#### 5.3.1 Scenario Builder
**Priority:** P0 (MVP)

**Description:** Create and manage multiple scenarios with different assumptions, constraints, and objectives.

**Functional Requirements:**
- **FR-SCN-001:** Scenario components:
  - Price deck selection
  - Constraint set (budget limits, production targets)
  - Project availability (include/exclude specific projects)
  - Objective function choice
  - Optimization settings (solve time limit, gap tolerance)
- **FR-SCN-002:** Scenario templates:
  - Base case
  - Low/Mid/High price
  - Budget-constrained
  - Growth-focused
  - Energy transition accelerated
  - Maintenance-only
- **FR-SCN-003:** Scenario comparison table showing:
  - Portfolio NPV, IRR, production
  - Projects selected (with delta highlighting)
  - Constraint utilization
  - Risk metrics
- **FR-SCN-004:** Batch scenario execution (queue 50+ scenarios overnight)
- **FR-SCN-005:** Scenario versioning and archival

**Acceptance Criteria:**
- User can create 10 scenarios in <15 minutes
- Batch run 50 scenarios completes overnight (<8 hours)
- Comparison view clearly highlights key differences

#### 5.3.2 Sensitivity & Risk Analysis
**Priority:** P0 (MVP)

**Description:** Quantify portfolio sensitivity to uncertain parameters and assess risk.

**Functional Requirements:**
- **FR-SCN-006:** One-way sensitivity analysis:
  - Tornado charts showing impact of ±20% change in key variables
  - Variables: oil price, gas price, CAPEX, OPEX, reserves, discount rate
- **FR-SCN-007:** Monte Carlo simulation:
  - Run 1,000-10,000 scenarios with correlated uncertain parameters
  - Output: NPV distribution, P10/P50/P90 portfolio values
  - Identify projects in >80% of optimal portfolios (robust selections)
- **FR-SCN-008:** Risk metrics:
  - Portfolio NPV standard deviation
  - Sharpe ratio (return per unit risk)
  - Value at Risk (VaR) at 95% and 99% confidence
  - Conditional Value at Risk (CVaR)
  - Probability of NPV < 0
- **FR-SCN-009:** Identify key risk drivers (which uncertain parameters contribute most to variance)

**Technical Requirements:**
- **TR-SCN-001:** Monte Carlo simulation uses Latin Hypercube Sampling for efficiency
- **TR-SCN-002:** Correlation matrix for commodity prices (oil-gas correlation, regional spreads)
- **TR-SCN-003:** 1,000-scenario Monte Carlo completes in <10 minutes

**Acceptance Criteria:**
- Tornado chart correctly ranks sensitivity of top 10 parameters
- Monte Carlo NPV distribution matches analytical calculation for simple test case
- System identifies projects appearing in >90% of optimal portfolios

---

### 5.4 Visualization & Reporting

#### 5.4.1 Executive Dashboard
**Priority:** P0 (MVP)

**Description:** High-level portfolio overview for C-suite decision-makers.

**Functional Requirements:**
- **FR-VIZ-001:** Key metrics cards:
  - Portfolio NPV, IRR, Payback Period
  - Total CAPEX required
  - Production (peak, plateau, tail)
  - Emissions profile
  - Number of projects selected
- **FR-VIZ-002:** CAPEX spending profile (bar chart by year)
- **FR-VIZ-003:** Production profile (area chart by year, stacked by project type)
- **FR-VIZ-004:** Geographic map of selected projects
- **FR-VIZ-005:** Portfolio composition (pie charts):
  - By asset type (upstream/midstream/renewables)
  - By business unit
  - By risk category
  - By project stage (explore/appraise/develop)
- **FR-VIZ-006:** Risk dashboard:
  - NPV distribution histogram
  - Risk-return scatter plot
  - Constraint utilization gauges
- **FR-VIZ-007:** Executive summary in natural language:
  - "The optimal portfolio invests $2.4B over 5 years in 23 projects, generating $8.7B NPV at 10% discount rate. The portfolio prioritizes low-risk development projects (18 of 23) while maintaining reserve replacement above 120%."

**Acceptance Criteria:**
- Dashboard loads in <2 seconds
- All charts interactive (click to drill down)
- Auto-generated summary accurately describes portfolio characteristics

#### 5.4.2 Portfolio Network Visualization
**Priority:** P1 (Phase 2) — **KEY DIFFERENTIATOR**

**Description:** Interactive network diagram showing projects and interdependencies.

**Functional Requirements:**
- **FR-VIZ-008:** Network graph with:
  - Nodes = projects (sized by NPV, colored by status: selected/rejected/uncertain)
  - Edges = dependencies (arrows, colored by type)
- **FR-VIZ-009:** Interactive features:
  - Drag nodes to rearrange
  - Click node to see project details
  - Highlight dependencies of selected project
  - Filter by project type, business unit
- **FR-VIZ-010:** Cluster detection (group related projects)
- **FR-VIZ-011:** Criticality highlighting (show projects that enable many others)
- **FR-VIZ-012:** "What-if" mode: manually select/reject projects and see cascading impacts

**Technical Requirements:**
- **TR-VIZ-001:** Use force-directed graph layout (D3.js force simulation)
- **TR-VIZ-002:** Render 500-node network in <5 seconds
- **TR-VIZ-003:** Support zoom, pan, search

**Acceptance Criteria:**
- Network clearly shows critical path dependencies
- User can identify infrastructure bottlenecks visually
- Manual project toggle updates dependent projects in <1 second

#### 5.4.3 Pareto Frontier Explorer
**Priority:** P1 (Phase 2)

**Description:** Interactive 2D/3D visualization of multi-objective trade-offs.

**Functional Requirements:**
- **FR-VIZ-013:** 2D scatter plot for 2 objectives (e.g., NPV vs. Emissions)
- **FR-VIZ-014:** 3D surface for 3 objectives (e.g., NPV vs. Emissions vs. Production)
- **FR-VIZ-015:** Click point on frontier to:
  - View corresponding portfolio composition
  - See project list
  - Display CAPEX profile
- **FR-VIZ-016:** Trade-off curves showing marginal rates of substitution
- **FR-VIZ-017:** Weight sliders to generate custom portfolio within Pareto set

**Acceptance Criteria:**
- Pareto frontier with 30 points renders in <3 seconds
- User can explore 10+ portfolio variants in <2 minutes
- Trade-off curves clearly show diminishing returns

#### 5.4.4 Reporting & Exports
**Priority:** P0 (MVP)

**Description:** Generate reports and export data for external use.

**Functional Requirements:**
- **FR-VIZ-018:** Report templates:
  - Executive summary (PowerPoint, 5-10 slides)
  - Detailed portfolio analysis (Excel workbook with multiple sheets)
  - Board presentation (PowerPoint, 20-30 slides)
  - Audit trail (PDF, all assumptions and decisions)
- **FR-VIZ-019:** Custom report builder (drag-and-drop sections)
- **FR-VIZ-020:** Export formats:
  - Excel (full project-level detail)
  - CSV (results table)
  - JSON (API consumption)
  - PowerPoint (charts as editable objects)
  - PDF (static reports)
- **FR-VIZ-021:** Scheduled reports (email weekly portfolio status)

**Acceptance Criteria:**
- Excel export contains all input data and results for full reproducibility
- PowerPoint export maintains corporate branding templates
- Reports generate in <30 seconds for 200-project portfolio

---

### 5.5 Energy Transition Portfolio Management
**Priority:** P1 (Phase 2) — **KEY DIFFERENTIATOR**

**Description:** Unified optimization across traditional hydrocarbon and low-carbon investments.

**Functional Requirements:**
- **FR-ET-001:** Asset type taxonomy:
  - Traditional: upstream oil, upstream gas, midstream, downstream
  - Transition: CCUS, hydrogen (blue/green), biofuels, RNG
  - Renewable: solar, wind, battery storage, geothermal
  - Decommissioning: P&A, facility removal, site restoration
- **FR-ET-002:** Dual objective optimization:
  - Primary: Maximize NPV
  - Secondary: Minimize scope 1+2 emissions or achieve net-zero by target year
- **FR-ET-003:** Carbon pricing scenarios:
  - Explicit carbon tax/price
  - Shadow carbon price for internal decision-making
  - Compliance cost for emissions above cap
- **FR-ET-004:** Transition pathway analysis:
  - Visualize portfolio evolution over 20 years
  - Show hydrocarbon decline and renewable growth
  - Demonstrate path to net-zero by 2040/2050
- **FR-ET-005:** Stranded asset risk assessment:
  - Identify projects that become uneconomic under carbon pricing
  - Highlight assets with regulatory phase-out risk
- **FR-ET-006:** Portfolio resilience metrics:
  - Diversification score (across energy types)
  - Transition readiness index
  - Exposure to carbon price risk

**Acceptance Criteria:**
- System optimizes mixed portfolio of 60% oil/gas, 40% renewables
- Carbon constraint successfully forces portfolio toward low-carbon options
- Transition pathway visualization clearly shows energy mix evolution

---

### 5.6 Collaboration & Workflow

#### 5.6.1 Multi-User Collaboration
**Priority:** P1 (Phase 2)

**Functional Requirements:**
- **FR-COLLAB-001:** Role-based access control:
  - Admin: full access, user management
  - Portfolio Manager: create scenarios, run optimizations, view all results
  - Analyst: edit project data, run pre-defined scenarios
  - Executive: view-only dashboards and reports
  - Business Unit Lead: view/edit own unit's projects only
- **FR-COLLAB-002:** Real-time collaboration:
  - See who else is viewing a scenario
  - Lock scenarios during editing
  - Change notifications (Slack/email when optimization completes)
- **FR-COLLAB-003:** Comment threads on projects and scenarios
- **FR-COLLAB-004:** Approval workflows:
  - Analyst creates scenario → Manager reviews → Executive approves
  - Track approval status

**Acceptance Criteria:**
- 10 users can work simultaneously without conflicts
- Changes sync across users in <5 seconds
- Approval workflow reduces decision cycle time by 50%

#### 5.6.2 Audit Trail & Governance
**Priority:** P1 (Phase 2)

**Functional Requirements:**
- **FR-GOV-001:** Complete audit log:
  - Who changed what, when (project data, assumptions, scenarios)
  - Optimization run history with all inputs
  - Decision rationale capture (why was this portfolio selected?)
- **FR-GOV-002:** Scenario certification:
  - Mark scenarios as "Board Approved" or "Working Draft"
  - Prevent modification of certified scenarios
- **FR-GOV-003:** Data lineage tracking:
  - Trace any output back to source assumptions
  - Version control for all inputs
- **FR-GOV-004:** Compliance exports for regulatory reporting (SEC, local regulations)

**Acceptance Criteria:**
- Audit log reconstructs any scenario from 12 months ago
- Data lineage traces NPV back to source price deck and project data
- Certified scenarios are immutable

---

## 7. Non-Functional Requirements

### 6.1 Performance

- **NFR-PERF-001:** API response time <200ms for 95th percentile
- **NFR-PERF-002:** Dashboard load time <2 seconds
- **NFR-PERF-003:** 500-project deterministic optimization completes in <5 minutes
- **NFR-PERF-004:** Monte Carlo simulation (1,000 scenarios) completes in <10 minutes
- **NFR-PERF-005:** Support 50 concurrent users without performance degradation
- **NFR-PERF-006:** Large Excel import (500 projects) processes in <2 minutes

### 6.2 Scalability

- **NFR-SCALE-001:** Support portfolios up to 500 projects (MVP), 2,000 projects (future)
- **NFR-SCALE-002:** Planning horizon: 20+ years with annual time steps
- **NFR-SCALE-003:** Horizontal scaling of optimization workers (add capacity on-demand)
- **NFR-SCALE-004:** Database supports 10TB+ of scenario results over 5 years

### 6.3 Reliability & Availability

- **NFR-REL-001:** System uptime: 99.5% (MVP), 99.9% (production)
- **NFR-REL-002:** Zero data loss (automated backups every 6 hours)
- **NFR-REL-003:** Recovery Time Objective (RTO): <4 hours
- **NFR-REL-004:** Recovery Point Objective (RPO): <6 hours
- **NFR-REL-005:** Graceful degradation (API remains available if optimization workers fail)

### 6.4 Security

- **NFR-SEC-001:** SOC 2 Type II compliance (target within 18 months)
- **NFR-SEC-002:** Data encryption at rest (AES-256) and in transit (TLS 1.3)
- **NFR-SEC-003:** Multi-factor authentication (MFA) required for all users
- **NFR-SEC-004:** Single Sign-On (SSO) via SAML 2.0 (Okta, Azure AD)
- **NFR-SEC-005:** Role-based access control (RBAC) with minimum privilege principle
- **NFR-SEC-006:** Data residency options (US, EU, Australia) for compliance
- **NFR-SEC-007:** Penetration testing annually
- **NFR-SEC-008:** Vulnerability scanning in CI/CD pipeline

### 6.5 Usability

- **NFR-UX-001:** Executive dashboard requires zero training (self-explanatory)
- **NFR-UX-002:** Portfolio manager can create and run scenario in <10 minutes after 1-hour training
- **NFR-UX-003:** System Help includes:
  - Interactive tutorials
  - Video walkthroughs
  - Searchable knowledge base
  - Tooltips on all technical terms
- **NFR-UX-004:** Mobile-responsive dashboard (view-only on tablet/phone)
- **NFR-UX-005:** Accessibility: WCAG 2.1 AA compliance

### 6.6 Maintainability

- **NFR-MAINT-001:** Code test coverage >80%
- **NFR-MAINT-002:** API documentation auto-generated (OpenAPI/Swagger)
- **NFR-MAINT-003:** Modular architecture (replace solver engine without rewriting application)
- **NFR-MAINT-004:** Configuration-driven (no code changes for new constraint types)
- **NFR-MAINT-005:** Comprehensive logging and monitoring (errors, performance, usage)

---

## 8. Data Models (High-Level)

### 8.1 Core Entities

**Project**
```python
{
  "id": "uuid",
  "name": "string",
  "type": "enum[upstream_oil, upstream_gas, midstream, renewable_solar, ...]",
  "business_unit": "string",
  "location": {"lat": float, "lon": float, "country": "string"},
  "economics": {
    "capex_schedule": [{"year": int, "amount": float}, ...],
    "opex_profile": [{"year": int, "amount": float}, ...],
    "revenue_forecast": [{"year": int, "amount": float}, ...],
    "production_profile": [{"year": int, "volume": float, "commodity": "string"}, ...]
  },
  "timing": {
    "earliest_start": "date",
    "latest_start": "date", 
    "duration_years": int
  },
  "risk": {
    "geological_pos": float,  # 0-1
    "commercial_pos": float,
    "capex_uncertainty": {"p10": float, "p50": float, "p90": float}
  },
  "reserves": {
    "p10": float,
    "p50": float,
    "p90": float,
    "eur": float
  },
  "esg": {
    "emissions_intensity": float,  # tons CO2e per unit
    "emissions_absolute": float,   # total tons CO2e
    "safety_risk_score": float
  },
  "strategic": {
    "strategic_alignment": float,  # 1-5 scale
    "competitive_moat": "enum[none, weak, strong]"
  }
}
```

**Dependency**
```python
{
  "id": "uuid",
  "type": "enum[prerequisite, mutex, shared_infra, synergy, resource_constraint]",
  "source_project_id": "uuid",
  "target_project_id": "uuid",
  "parameters": {
    # For prerequisite: timing lag
    "lag_months": int,
    
    # For shared_infra: capacity constraint
    "infrastructure_id": "uuid",
    "capacity_required": float,
    
    # For synergy: value impact
    "capex_reduction": float,
    "opex_reduction": float
  }
}
```

**Temporal State Variables (Optimization Runtime)**
```python
# These are created dynamically during optimization, not stored in database
# Managed by TimeSeriesStateManager class

{
  "project_id": "uuid",
  "year": int,
  "state_variables": {
    # Financial states
    "revenue": float,           # Revenue in year t
    "opex": float,             # Operating expenses in year t
    "capex": float,            # Capital expenses in year t
    "cashflow": float,         # Net cashflow in year t
    "debt": float,             # Cumulative debt at end of year t
    "npv_contribution": float, # Discounted value from year t
    
    # Production states
    "production": float,        # Production volume in year t
    "cumulative_production": float,  # Total production through year t
    "decline_rate": float,      # Production decline in year t
    
    # ESG states
    "emissions": float,         # Emissions in year t
    "cumulative_emissions": float,  # Total emissions through year t
    
    # Infrastructure states
    "capacity_used": float,     # Infrastructure capacity consumed
    "resource_consumption": {   # Resources used in year t
      "rigs": int,
      "personnel": int,
      "materials": float
    },
    
    # Derived/calculated states
    "debt_service_coverage": float,  # Cashflow / debt payment
    "roi_cumulative": float,    # Return on investment through year t
    "breakeven_status": "enum[not_reached, reached]"
  },
  
  # Constraints linking to previous year
  "temporal_constraints": {
    "debt_evolution": "debt[t] = debt[t-1]*(1+r) + capex[t] - cashflow[t]",
    "production_decline": "production[t] = production[t-1]*(1-decline_rate)",
    "capacity_constraint": "sum(capacity_used[p,t] for p in projects) <= total_capacity"
  }
}
```

**State Variable Index Structure (Database Storage)**
```python
# Store optimization results with temporal dimension
{
  "scenario_id": "uuid",
  "project_id": "uuid", 
  "year": int,  # 0-30
  
  # Financial metrics by year
  "revenue_by_year": float,
  "opex_by_year": float,
  "capex_by_year": float,
  "cashflow_by_year": float,
  "debt_by_year": float,
  
  # Production metrics by year
  "production_by_year": float,
  "cumulative_production_by_year": float,
  
  # Calculated once, stored for fast retrieval
  "npv": float,  # Total NPV (not by year)
  "irr": float,  # Internal rate of return
  
  # Metadata
  "is_selected": bool,
  "start_year": int,
  "created_at": "timestamp"
}

# Database index for fast time-series queries
CREATE INDEX idx_scenario_project_year ON optimization_results(scenario_id, project_id, year);
CREATE INDEX idx_scenario_selected ON optimization_results(scenario_id, is_selected);
```

**Scenario**
```python
{
  "id": "uuid",
  "name": "string",
  "description": "string",
  "created_by": "user_id",
  "created_at": "timestamp",
  "status": "enum[draft, running, completed, failed]",
  "inputs": {
    "price_deck_id": "uuid",
    "constraints": [
      {
        "type": "enum[capex_annual, capex_cumulative, production_min, emissions_max, ...]",
        "parameters": {...}
      }
    ],
    "objective": {
      "type": "enum[maximize_npv, maximize_npv_per_capex, multi_objective]",
      "weights": {"npv": 0.7, "emissions": 0.3}  # for multi-objective
    },
    "project_availability": ["project_id_1", "project_id_2", ...],
    "optimization_settings": {
      "solver": "gurobi",
      "time_limit_seconds": 300,
      "mip_gap": 0.001,
      "use_hybrid_optimization": true,  # Pre-compute independent projects
      "temporal_aggregation": "annual",  # or "biennial", "quinquennial"
      "lazy_constraints": false
    }
  },
  "results": {
    "optimal_portfolio": {
      "selected_projects": [
        {"project_id": "uuid", "start_year": int}
      ],
      "objective_value": float,
      "metrics": {
        "npv": float,
        "total_capex": float,
        "peak_production": float,
        "emissions_total": float
      }
    },
    "solver_stats": {
      "solve_time_seconds": float,
      "mip_gap_final": float,
      "iterations": int,
      "num_variables": int,
      "num_constraints": int,
      "num_state_variables": int,  # Temporal state variables created
      "precomputed_projects": int,  # Projects handled via pre-computation
      "optimization_method": "enum[full_milp, hybrid, lazy_constraints]"
    },
    "temporal_results": {
      # Time-series data stored separately for efficiency
      "reference": "optimization_results table",
      "num_time_periods": 30,
      "year_resolution": "annual"
    }
  }
}
```

**PriceDeck**
```python
{
  "id": "uuid",
  "name": "string",
  "type": "enum[deterministic, stochastic]",
  "commodities": [
    {
      "commodity": "enum[oil_wti, gas_henry_hub, power_ercot, ...]",
      "unit": "string",
      "prices": [
        {"year": int, "price": float}  # deterministic
      ],
      "distribution": {  # stochastic
        "type": "enum[gbm, mean_reverting, historical_simulation]",
        "parameters": {...}
      }
    }
  ]
}
```

### 8.2 Database Schema Optimizations for Temporal Data

**TimescaleDB Hypertables for Time-Series Storage**
```sql
-- Create hypertable for time-series optimization results
CREATE TABLE optimization_results (
  scenario_id UUID NOT NULL,
  project_id UUID NOT NULL,
  year INT NOT NULL,
  
  -- Financial metrics
  revenue DECIMAL(15,2),
  opex DECIMAL(15,2),
  capex DECIMAL(15,2),
  cashflow DECIMAL(15,2),
  debt DECIMAL(15,2),
  
  -- Production metrics
  production DECIMAL(15,2),
  cumulative_production DECIMAL(15,2),
  
  -- Selection info
  is_selected BOOLEAN,
  start_year INT,
  
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Convert to TimescaleDB hypertable (optimized for time-series)
SELECT create_hypertable('optimization_results', 'created_at');

-- Create composite index for fast scenario queries
CREATE INDEX idx_scenario_project_year 
ON optimization_results(scenario_id, project_id, year);

-- Continuous aggregates for fast dashboard queries
CREATE MATERIALIZED VIEW portfolio_summary
WITH (timescaledb.continuous) AS
SELECT 
  scenario_id,
  year,
  SUM(capex) as total_capex,
  SUM(revenue) as total_revenue,
  SUM(production) as total_production,
  COUNT(*) FILTER (WHERE is_selected) as num_selected_projects
FROM optimization_results
GROUP BY scenario_id, year;

-- Refresh policy (update every hour)
SELECT add_continuous_aggregate_policy('portfolio_summary',
  start_offset => INTERVAL '1 day',
  end_offset => INTERVAL '1 hour',
  schedule_interval => INTERVAL '1 hour');
```

**Partitioning Strategy**
```sql
-- Partition optimization_results by scenario_id for query performance
CREATE TABLE optimization_results (
  scenario_id UUID NOT NULL,
  -- ... other columns
) PARTITION BY HASH (scenario_id);

-- Create 16 partitions (adjust based on expected concurrent scenarios)
CREATE TABLE optimization_results_p0 PARTITION OF optimization_results 
  FOR VALUES WITH (MODULUS 16, REMAINDER 0);
CREATE TABLE optimization_results_p1 PARTITION OF optimization_results 
  FOR VALUES WITH (MODULUS 16, REMAINDER 1);
-- ... repeat for p2-p15
```

### 8.3 Product X-Compatible Data Structures

To enable seamless migration from Product X and competitive feature parity, our platform supports all Product X data structures with extensions for our enhanced capabilities.

#### 7.3.1 Input Data Structure

**Excel Sheet: "p4 input data"**

Purpose: Time-series metrics for each opportunity-outcome combination

**Column Structure:**
```
Opportunity Name | Outcome | Weight | Metric Name | Unit | Yr1 | Yr2 | Yr3 | ... | Yr30
```

**Database Schema (Normalized):**
```python
class OpportunityMetricTimeSeries(BaseModel):
    """
    Stores input metrics in normalized long format
    (Product X uses wide format in Excel)
    """
    opportunity_id: UUID
    opportunity_name: str  # "Alpha Base", "Bravo Development"
    outcome_id: UUID
    outcome_name: str  # "Base", "Optimistic", "Pessimistic"
    outcome_weight: float  # Probability: 0.0 to 1.0 (must sum to 1.0 per opportunity)
    metric_id: UUID
    metric_name: str  # "Capex", "Opex", "Production Rate - Oil"
    unit: str  # "$M", "bbl/d", "mcf/d"
    time_series_data: List[TimeSeriesValue]  # [{year: 0, value: 10000}, {year: 1, value: 10000}, ...]
    
    # Metadata
    data_source: str = "excel_import"  # Or "api", "manual_entry"
    imported_at: datetime
    last_modified: datetime

class TimeSeriesValue(BaseModel):
    year: int  # 0-indexed from portfolio start
    value: float
    
    # Optional for sparse data
    interpolation_method: Optional[str] = "linear"  # "linear", "forward_fill", "zero"
```

**Sample Data:**
```
Opportunity: Alpha Base
Outcome: Base (weight=1.0)
Metrics:
  - Capex: [10000, 10000, 10000, ...] $M over 30 years
  - Opex: [102656, 97575, 92789, ...] $M (declining)
  - Production Rate - Gas: [168750, 158923, 149668, ...] mcf/d (declining)
  - Production Rate - Oil: [9375, 8829, 8315, ...] bbl/d (declining)
```

**Import Transformation:**
```python
def import_Product X_input_data(excel_sheet):
    """
    Convert Product X wide format to our normalized long format
    
    Product X: One row per (opportunity, outcome, metric)
    Us: One record per (opportunity, outcome, metric) with time_series array
    """
    records = []
    
    for row in excel_sheet.iter_rows(min_row=2, values_only=True):
        opp_name, outcome_name, weight, metric_name, unit = row[0:5]
        year_values = row[5:]  # Remaining columns are years
        
        # Create time series array
        time_series = [
            {"year": year_idx, "value": value}
            for year_idx, value in enumerate(year_values)
            if value is not None  # Sparse storage
        ]
        
        record = {
            "opportunity_name": opp_name,
            "outcome_name": outcome_name,
            "outcome_weight": weight,
            "metric_name": metric_name,
            "unit": unit,
            "time_series_data": time_series
        }
        records.append(record)
    
    # Validation
    validate_outcome_weights(records)  # Must sum to 1.0
    validate_time_series_length(records)  # Must match planning horizon
    
    return records
```

**Enhancements Over Product X:**
- Support sparse time series (only enter non-zero values)
- Real-time validation during Excel upload
- Automatic unit conversion (bbl/d → Mbbl/d, mcf/d → MMcf/d)
- Version control (track changes over time)
- Support 2000+ projects (no Excel row limit)

---

#### 7.3.2 Attributes Structure

**Excel Sheet: "p4 attributes"**

Purpose: Categorize and tag opportunities for filtering, grouping, and master data assignment

**Column Structure:**
```
Opportunity Name | Fixture? | Area | Onshore/Offshore | Reserve Cat | Project | Business Unit | Price Scenario | [Custom Attributes...]
```

**Database Schema:**
```python
class OpportunityAttributes(BaseModel):
    """
    Flexible attribute system supporting Product X's model + custom extensions
    """
    opportunity_id: UUID
    opportunity_name: str
    
    # Special Product X flags
    is_fixture: bool = False  # If True, this is a Master Data assignment record
    
    # Standard petroleum attributes
    area: Optional[str]  # "North", "South", "East", "West" (geographic)
    onshore_offshore: Optional[str]  # "Onshore", "Offshore"
    reserve_category: Optional[str]  # "PDP", "PUD", "PROB", "POSS"
    project: Optional[str]  # Project name (often same as opportunity)
    business_unit: Optional[str]  # "Alpha", "Bravo", "Charlie"
    
    # Master Data linkage
    price_scenario: Optional[str]  # Links to Master Data Set (e.g., "High", "Base", "Low")
    toll_scenario: Optional[str]  # Links to regional toll Master Data
    
    # Custom attributes (key-value store)
    custom_attributes: Dict[str, Any] = {}
    
    # Hierarchical attributes
    hierarchy: Optional[Dict[str, str]] = {}  # {"region": "North America", "country": "USA", "state": "Texas"}
    
    # Metadata
    created_at: datetime
    last_modified: datetime

class MasterDataAssignment(BaseModel):
    """
    Special fixture records that define Master Data Set linkages
    
    Example: Opportunity "High Price" with is_fixture=True, price_scenario="High"
    means any opportunity with price_scenario="High" uses this Master Data Set
    """
    fixture_name: str  # "High Price", "North Tolls"
    is_fixture: bool = True
    master_data_set_id: UUID
    applicable_attribute: str  # "price_scenario", "toll_scenario"
    applicable_value: str  # "High", "North"
```

**Sample Data:**
```
Regular opportunities:
  Alpha Base: area=North, onshore_offshore=Onshore, reserve_category=PDP, business_unit=Alpha
  Bravo Development: area=South, onshore_offshore=Onshore, reserve_category=PUD, business_unit=Bravo
  
Fixture records (Master Data assignments):
  High Price: is_fixture=True, price_scenario=High
  North Tolls: is_fixture=True, area=North
  Base Price: is_fixture=True, price_scenario=Base
```

**Enhancements Over Product X:**
- Unlimited custom attributes (not limited by Excel columns)
- Attribute type validation (categorical, numeric, boolean, date)
- Hierarchical attributes with inheritance (Region → Country → State)
- Attribute-based access control (Business Unit leads see only their projects)
- Saved attribute combinations as "views" or "filters"
- Visual attribute builder (no Excel column management)

---

#### 7.3.3 Master Data Structure

**Excel Sheet: "p4 master data"**

Purpose: Global time-series parameters that apply to multiple opportunities

**Column Structure:**
```
Master Data Set | Metric Name | Unit | 2025-01-01 | 2026-01-01 | 2027-01-01 | ... | 2044-01-01
```

**Database Schema:**
```python
class MasterDataSet(BaseModel):
    """
    Group of related master data metrics (e.g., "High Price" scenario)
    """
    id: UUID
    name: str  # "High Price", "Base Price", "Low Price", "North Tolls"
    description: Optional[str]
    category: str  # "price_scenario", "toll_scenario", "tax_scenario"
    
    # Metrics in this set
    metrics: List[MasterDataMetric]
    
    # Applicability
    applicable_to_attribute: str  # Which attribute links to this set
    applicable_to_value: str  # Value of that attribute
    
    # Metadata
    created_at: datetime
    last_modified: datetime
    is_active: bool = True

class MasterDataMetric(BaseModel):
    """
    Single metric within a Master Data Set
    """
    id: UUID
    master_data_set_id: UUID
    metric_name: str  # "MD - Price - Oil", "MD - Price - Gas", "MD - Oil Toll"
    unit: str  # "$/bbl", "$/mcf"
    
    # Time series values
    time_series_data: List[TimeSeriesValue]
    
    # For stochastic Master Data
    is_stochastic: bool = False
    distribution_type: Optional[str] = None  # "gbm", "mean_reverting", "historical_simulation"
    distribution_params: Optional[Dict[str, float]] = None

class MasterDataApplication:
    """
    Logic for applying Master Data to opportunities based on attributes
    """
    
    @staticmethod
    def get_applicable_master_data(opportunity: OpportunityAttributes) -> List[MasterDataSet]:
        """
        Find all Master Data Sets applicable to this opportunity
        
        Example:
        - Opportunity has price_scenario="High" → Returns "High Price" Master Data Set
        - Opportunity has area="North" → Returns "North Tolls" Master Data Set
        """
        applicable_sets = []
        
        # Check price scenario
        if opportunity.price_scenario:
            price_set = MasterDataSet.query.filter_by(
                category="price_scenario",
                applicable_to_value=opportunity.price_scenario
            ).first()
            if price_set:
                applicable_sets.append(price_set)
        
        # Check area for tolls
        if opportunity.area:
            toll_set = MasterDataSet.query.filter_by(
                category="toll_scenario",
                applicable_to_value=opportunity.area
            ).first()
            if toll_set:
                applicable_sets.append(toll_set)
        
        return applicable_sets
```

**Sample Data:**
```
Master Data Set: "High Price"
  - MD - Price - Oil: [85, 90, 90, 90, ...] $/bbl
  - MD - Price - Gas: [4, 4, 4, 4, ...] $/mcf
  Applicable to: price_scenario="High"

Master Data Set: "North Tolls"
  - MD - Oil Toll: [5, 5, 5, 5, ...] $/bbl
  - MD - Gas Fee: [0.4, 0.4, 0.4, ...] $/mcf
  - MD - Tax - Production: [0.1, 0.1, 0.1, ...] (10% rate)
  Applicable to: area="North"
```

**Enhancements Over Product X:**
- **Master Data Library:** Pre-built common scenarios (WTI forward curve, Henry Hub, standard fiscal regimes)
- **Scenario builder wizard:** Generate High/Mid/Low from single base case automatically
- **Stochastic Master Data:** Generate correlated price paths via GBM or mean reversion
- **Live data feeds:** Auto-update from Bloomberg API, EIA API, CME futures
- **Version control:** Track Master Data changes over time
- **Validation dashboard:** Show coverage gaps (e.g., "Master Data only covers 25 years but portfolio needs 30")
- **Correlation management:** Define correlations between commodities (oil-gas correlation = 0.7)

---

#### 7.3.4 Expression/Formula Structure

**Excel Sheet: "p4 expressions"**

Purpose: Define computed metrics using formulas that reference input metrics and Master Data

**Column Structure:**
```
Metric Type | Metric Name | Unit | FYF | PT | CT | Attribute | Characteristic | Opportunity | Outcome | Time | Level | Fixture? | Indicator? | Hide? | Scale by | Total | TotalDisc | TotalInf | Disc | CumDisc
```

**Database Schema:**
```python
class MetricExpression(BaseModel):
    """
    Defines a computed metric using Product X-style formulas
    """
    id: UUID
    metric_type: str  # "Input Metrics", "Computed Metrics", "Master Data"
    metric_name: str  # "Revenue - Oil", "BTAX Cash Flow", "NPV10"
    unit: str  # "$M", "boe/d", etc.
    
    # Formula components (Product X FYF/PT/CT pattern)
    formula_fyf: Optional[str] = None  # First Year Formula (t=0, cannot reference other formulas)
    formula_pt: Optional[str] = None  # Prior Time reference (t-1)
    formula_ct: Optional[str] = None  # Current Time formula (can reference PT and current metrics)
    
    # Aggregation formulas
    formula_total: Optional[str] = None  # Undiscounted sum: Total([metric])
    formula_total_disc: Optional[str] = None  # NPV: TotalDisc([metric])
    formula_total_inf: Optional[str] = None  # Inflated total: TotalInf([metric])
    formula_disc: Optional[str] = None  # Single period discount: Disc([metric], t)
    formula_cum_disc: Optional[str] = None  # Cumulative discounted: CumDisc([metric])
    
    # Filtering (apply formula only to subset of data)
    attribute_filter: Optional[str] = None  # Filter by attribute name
    characteristic_filter: Optional[str] = None  # Filter by attribute value
    opportunity_filter: Optional[str] = None  # Apply to specific opportunity only
    outcome_filter: Optional[str] = None  # Apply to specific outcome only
    time_filter: Optional[str] = None  # Apply to specific time periods
    
    # Aggregation level
    level: str = "S"  # "O" (Outcome), "P" (Project/Opportunity), "S" (Scenario)
    
    # Display flags
    is_fixture: bool = False  # Master Data (does not time shift)
    is_indicator: bool = False  # Single value (not time-series)
    is_hidden: bool = False  # Hide from default views
    scale_by: Optional[str] = None  # Scale by working interest or instances
    
    # Metadata
    created_at: datetime
    last_modified: datetime
    dependencies: List[str] = []  # Other metrics this depends on (auto-generated from formula)

class CompiledExpression(BaseModel):
    """
    Compiled version of expression for fast execution
    """
    expression_id: UUID
    compiled_bytecode: bytes  # Compiled AST for Python execution
    dependency_graph: Dict[str, List[str]]  # Metric dependencies
    execution_order: List[str]  # Topologically sorted execution sequence
```

**Sample Expressions:**
```python
# Revenue from oil
{
    "metric_name": "Revenue - Oil",
    "unit": "$M",
    "formula_ct": "[Production Rate - Oil] * [MD - Price - Oil] * 365.25 / 1000000",
    "level": "O",  # Calculate per outcome
}

# BTAX Cash Flow
{
    "metric_name": "BTAX Cash Flow", 
    "unit": "$M",
    "formula_ct": "[Revenue - Oil] + [Revenue - Gas] - [Opex] - [Capex]",
    "level": "P",  # Aggregate to project level (sum across outcomes)
}

# NPV10
{
    "metric_name": "NPV10",
    "unit": "$M",
    "formula_total_disc": "TotalDisc([BTAX Cash Flow], 0.10)",
    "level": "S",  # Aggregate to scenario level
    "is_indicator": True,  # Single value, not time-series
}

# Cumulative Production
{
    "metric_name": "Cumulative Production",
    "unit": "MMbbl",
    "formula_fyf": "[Production Rate - Oil] / 365.25 / 1000",  # First year
    "formula_ct": "PT + [Production Rate - Oil] / 365.25 / 1000",  # Add to prior cumulative
    "level": "O",
}

# Conditional Formula
{
    "metric_name": "Opex Variable",
    "unit": "$M",
    "formula_ct": "IF([Production Rate - Oil] > 5000, [Opex High Rate], [Opex Low Rate])",
    "level": "O",
}

# Filtered Formula (only for offshore projects)
{
    "metric_name": "Offshore Decommissioning Cost",
    "unit": "$M",
    "formula_ct": "[CAPEX] * 0.15",  # 15% of CAPEX
    "attribute_filter": "Onshore / Offshore",
    "characteristic_filter": "Offshore",
    "level": "P",
}
```

**Built-in Functions:**
- `Total([metric])`: Sum metric across all time periods
- `TotalDisc([metric], rate)`: NPV with given discount rate
- `TotalInf([metric])`: Inflate and sum
- `Disc([metric], t)`: Discount single period value
- `CumDisc([metric])`: Cumulative discounted to current period
- `GetCumulative([metric], start, end)`: Sum metric over period range
- `IF(condition, true_value, false_value)`: Conditional
- `MAX(a, b)`: Maximum of two values
- `MIN(a, b)`: Minimum
- `SUM(metrics)`: Sum multiple metrics

**Enhancements Over Product X:**
- **Dual syntax:** Support both Product X `[Metric]` syntax AND Python `df['Metric']`
- **Formula autocomplete:** Suggest available metrics while typing
- **Dependency visualization:** Graph showing which metrics depend on which
- **Formula debugging:** Step through calculation showing intermediate values
- **Unit validation:** Automatic checking (cannot add $/bbl to boe/d)
- **Performance:** Vectorized via NumPy (100x faster than Excel)
- **Custom functions:** Users can register Python functions
- **Excel formula import:** Paste Excel formulas, auto-convert syntax

---

#### 7.3.5 Selection Constraints Structure

**Excel Sheet: "p4 selection constraints"**

Purpose: Control how and when projects can be selected

**Column Structure:**
```
Opportunity Name | Integer? | Active? | Total WI Min/Max | Total Instances Min/Max | Y1 Min/Max | Y2 Min/Max | ... | Y20 Min/Max
```

**Database Schema:**
```python
class SelectionConstraint(BaseModel):
    """
    Constraints on project selection and timing
    """
    id: UUID
    opportunity_id: UUID
    opportunity_name: str
    
    # Constraint type flags
    is_integer: bool = True  # Must select whole units (vs. fractional)
    is_active: bool = True  # Constraint enforced?
    
    # Working Interest (WI) constraints
    total_wi_min: float = 0.0  # Minimum fractional ownership (0.0 to 1.0+)
    total_wi_max: float = 1.0  # Maximum fractional ownership
    
    # Instance constraints (for repeatable projects)
    total_instances_min: int = 0  # Minimum number of times to select
    total_instances_max: int = 1  # Maximum number of times to select
    
    # Yearly timing constraints
    yearly_constraints: List[YearlyConstraint] = []  # Min/Max per year
    
    # Metadata
    created_at: datetime
    last_modified: datetime

class YearlyConstraint(BaseModel):
    """
    Min/Max selection constraint for specific year
    """
    year: int  # 0-indexed from portfolio start
    min_selections: int = 0  # Minimum starts in this year
    max_selections: int = 0  # Maximum starts in this year

# MILP Formulation
class SelectionConstraintGenerator:
    """
    Convert selection constraints to Pyomo constraints
    """
    
    def generate_constraints(self, model, constraint: SelectionConstraint):
        """
        Generate Pyomo constraints from selection constraint definition
        """
        project = constraint.opportunity_id
        
        # Total instances constraint
        if constraint.is_integer:
            model.instances[project].domain = NonNegativeIntegers
        
        model.add_constraint(
            constraint.total_instances_min <= 
            sum(model.start_year[project, t] for t in model.years) <= 
            constraint.total_instances_max
        )
        
        # Yearly timing constraints
        for yearly in constraint.yearly_constraints:
            year = yearly.year
            model.add_constraint(
                yearly.min_selections <= model.start_year[project, year] <= yearly.max_selections
            )
        
        # Working interest constraints
        model.add_constraint(
            constraint.total_wi_min <= model.working_interest[project] <= constraint.total_wi_max
        )
```

**Sample Constraints:**
```python
# Base production (must select, year 1 only)
{
    "opportunity_name": "Alpha Base",
    "is_integer": True,
    "total_instances_min": 1,
    "total_instances_max": 1,
    "yearly_constraints": [
        {"year": 0, "min_selections": 1, "max_selections": 1},  # Must start year 1
        {"year": 1, "min_selections": 0, "max_selections": 0},  # Cannot start year 2+
        ...
    ]
}

# Development project (optional, years 2-6, up to 5 instances per year)
{
    "opportunity_name": "Alpha Development",
    "is_integer": True,
    "total_instances_min": 0,
    "total_instances_max": 20,
    "yearly_constraints": [
        {"year": 0, "min_selections": 0, "max_selections": 0},  # Cannot start year 1
        {"year": 1, "min_selections": 0, "max_selections": 5},  # Years 2-6: up to 5/year
        {"year": 2, "min_selections": 0, "max_selections": 5},
        ...
    ]
}
```

---

#### 7.3.6 Selection Dependencies Structure

**Excel Sheet: "p4 selection dependencies"**

Purpose: Define prerequisite relationships between projects

**Column Structure:**
```
Active? | Independent Opportunity | Must/Must Not | Time Period Offset | Before/After/During | Dependent Opportunity | Need # N/R Independent | Each # N/R Dependent
```

**Database Schema:**
```python
class SelectionDependency(BaseModel):
    """
    Prerequisite or mutex dependency between projects
    """
    id: UUID
    is_active: bool = True
    
    # Projects involved
    independent_opportunity_id: UUID  # Parent/prerequisite project
    independent_opportunity_name: str
    dependent_opportunity_id: UUID  # Child/dependent project
    dependent_opportunity_name: str
    
    # Dependency type
    must_or_must_not: str  # "Must" (prerequisite) or "Must Not" (mutex)
    
    # Timing relationship
    time_offset: int = 0  # Years between parent and child (-1 = child starts 1 year AFTER parent)
    timing_relation: str = "Before"  # "Before", "After", "During"
    
    # Instance relationship
    need_instances: str = "1 R"  # How many parent instances needed (N=Normalized, R=Real)
    each_instances: str = "1 R"  # For each N parents, need M children
    
    # Metadata
    created_at: datetime
    last_modified: datetime

# MILP Formulation
class DependencyConstraintGenerator:
    """
    Convert dependencies to Pyomo constraints
    """
    
    def generate_prerequisite(self, model, dep: SelectionDependency):
        """
        Generate prerequisite constraints
        
        "If child selected in year t, parent must be selected in year (t + offset)"
        """
        parent = dep.independent_opportunity_id
        child = dep.dependent_opportunity_id
        offset = dep.time_offset
        
        for t in model.years:
            parent_year = t + offset
            if 0 <= parent_year < len(model.years):
                # If child starts at t, parent must have started by (t + offset)
                model.add_constraint(
                    model.start_year[child, t] <= 
                    sum(model.start_year[parent, tau] for tau in range(0, parent_year + 1))
                )
    
    def generate_mutex(self, model, dep: SelectionDependency):
        """
        Generate mutual exclusivity constraint
        
        "At most one of {parent, child} can be selected"
        """
        parent = dep.independent_opportunity_id
        child = dep.dependent_opportunity_id
        
        model.add_constraint(
            model.select[parent] + model.select[child] <= 1
        )
```

**Sample Dependencies:**
```python
# Exploration must precede appraisal (1 year lag)
{
    "independent_opportunity_name": "Charlie Exploration",
    "dependent_opportunity_name": "Charlie Appraisal",
    "must_or_must_not": "Must",
    "time_offset": -1,  # Appraisal starts 1 year AFTER exploration
    "timing_relation": "Before",
    "need_instances": "1 R",  # Need 1 real exploration
    "each_instances": "1 R",  # For each 1 exploration
}

# Appraisal must precede development (2 year lag for Dev 2)
{
    "independent_opportunity_name": "Charlie Appraisal",
    "dependent_opportunity_name": "Charlie Dev 2",
    "must_or_must_not": "Must",
    "time_offset": -2,  # Dev 2 starts 2 years after appraisal
    "timing_relation": "Before",
}

# Mutual exclusivity
{
    "independent_opportunity_name": "Delta Exploration",
    "dependent_opportunity_name": "Charlie Exploration",
    "must_or_must_not": "Must Not",
    # Only one exploration program
}
```

---

#### 7.3.7 Selection Groups Structure

**Excel Sheets: "p4 selection groups" + "p4 selection group constraints"**

Purpose: Group projects with collective constraints (exclusive or inclusive)

**Database Schema:**
```python
class SelectionGroup(BaseModel):
    """
    Group of projects with collective selection rules
    """
    id: UUID
    name: str  # "Echo", "Development Options"
    group_type: str  # "Exclusive", "Inclusive", "At Least N", "At Most N", "Exactly N"
    is_active: bool = True
    
    # Members
    members: List[GroupMember] = []
    
    # Group-level constraints (same structure as SelectionConstraint)
    total_instances_min: Optional[int] = None
    total_instances_max: Optional[int] = None
    yearly_constraints: List[YearlyConstraint] = []
    
    # Metadata
    created_at: datetime
    last_modified: datetime

class GroupMember(BaseModel):
    """
    Project membership in a selection group
    """
    opportunity_id: UUID
    opportunity_name: str
    is_disabled: bool = False  # Temporarily exclude from group

# MILP Formulation
class GroupConstraintGenerator:
    """
    Convert selection groups to Pyomo constraints
    """
    
    def generate_exclusive_group(self, model, group: SelectionGroup):
        """
        Exclusive group: At most 1 member selected
        """
        members = [m.opportunity_id for m in group.members if not m.is_disabled]
        model.add_constraint(
            sum(model.select[proj] for proj in members) <= 1
        )
    
    def generate_inclusive_group(self, model, group: SelectionGroup):
        """
        Inclusive group: All or nothing
        """
        members = [m.opportunity_id for m in group.members if not m.is_disabled]
        
        # Create group selection variable
        group_var = Var(domain=Binary)
        model.add_component(f"group_{group.id}", group_var)
        
        # If group selected, all members selected
        for member in members:
            model.add_constraint(model.select[member] >= group_var)
        
        # If any member selected, group selected
        model.add_constraint(
            group_var * len(members) >= sum(model.select[m] for m in members)
        )
    
    def generate_at_least_n(self, model, group: SelectionGroup, n: int):
        """
        At least N members must be selected
        """
        members = [m.opportunity_id for m in group.members if not m.is_disabled]
        model.add_constraint(
            sum(model.select[proj] for proj in members) >= n
        )
```

---

#### 7.3.8 Metric Constraints Structure

**Excel Sheet: "p4 metric limits" or "Metric Limits"**

Purpose: Portfolio-level constraints on any calculated metric

**Column Structure:**
```
Metric Name | Unit | Enforce? | Type | Soft? | Penalty Weight | Magnitude | Default | Y1 | Y2 | ... | Y20
```

**Database Schema:**
```python
class MetricConstraint(BaseModel):
    """
    Constraint on portfolio-level metric value
    """
    id: UUID
    metric_name: str  # Any metric from expressions (e.g., "C205 - Capital")
    unit: str  # "$MM", "boe/d"
    
    # Constraint enforcement
    is_enforced: bool = True
    constraint_type: str  # "Min", "Max", "Range", "Equal"
    
    # Hard vs. Soft constraint
    is_soft: bool = False  # If True, can be violated with penalty
    penalty_weight: Optional[float] = None  # Weight in objective function
    penalty_magnitude: Optional[float] = None  # Normalization factor
    
    # Limit values
    default_limit: Optional[float] = None  # Applied to all years unless overridden
    yearly_limits: Dict[int, float] = {}  # {year: limit} overrides
    
    # Metadata
    created_at: datetime
    last_modified: datetime

# MILP Formulation
class MetricConstraintGenerator:
    """
    Convert metric constraints to Pyomo constraints
    """
    
    def generate_hard_constraint(self, model, constraint: MetricConstraint):
        """
        Generate hard constraint (must be satisfied)
        """
        metric_name = constraint.metric_name
        
        for year in model.years:
            limit = constraint.yearly_limits.get(year, constraint.default_limit)
            
            if limit is None:
                continue  # No constraint for this year
            
            # Evaluate metric for this year
            metric_value = model.evaluate_metric(metric_name, year)
            
            if constraint.constraint_type == "Max":
                model.add_constraint(metric_value <= limit)
            elif constraint.constraint_type == "Min":
                model.add_constraint(metric_value >= limit)
    
    def generate_soft_constraint(self, model, constraint: MetricConstraint):
        """
        Generate soft constraint with penalty for violation
        """
        # Add slack variable
        slack_var = Var(model.years, domain=NonNegativeReals)
        model.add_component(f"slack_{constraint.id}", slack_var)
        
        for year in model.years:
            limit = constraint.yearly_limits.get(year, constraint.default_limit)
            if limit is None:
                continue
            
            metric_value = model.evaluate_metric(constraint.metric_name, year)
            
            if constraint.constraint_type == "Min":
                # metric + slack >= limit (slack allows violation)
                model.add_constraint(metric_value + slack_var[year] >= limit)
            elif constraint.constraint_type == "Max":
                # metric - slack <= limit
                model.add_constraint(metric_value - slack_var[year] <= limit)
            
            # Add penalty to objective
            # penalty = weight * (slack / magnitude)^2
            penalty = constraint.penalty_weight * (slack_var[year] / constraint.penalty_magnitude) ** 2
            model.objective_penalties.append(penalty)
```

**Sample Metric Constraints:**
```python
# Hard CAPEX limit
{
    "metric_name": "C205 - Capital",
    "unit": "$MM",
    "is_enforced": True,
    "constraint_type": "Max",
    "is_soft": False,
    "default_limit": 1000,  # $1000MM per year max
}

# Soft cash flow target
{
    "metric_name": "C210 - Cash Flow - BTAX",
    "unit": "$MM",
    "is_enforced": True,
    "constraint_type": "Min",
    "is_soft": True,
    "penalty_weight": 50,
    "penalty_magnitude": 100,
    "yearly_limits": {
        1: 958.32,
        2: 986.27,
        3: 1015.62,
        # Can violate with $50 penalty per $100MM shortfall
    }
}

# Minimum production plateau
{
    "metric_name": "B201 - Production - Daily Rate",
    "unit": "boe/d",
    "is_enforced": True,
    "constraint_type": "Min",
    "is_soft": False,
    "yearly_limits": {
        1: 397000,
        2: 397000,
        ...
        6: 397000,  # Maintain 397,000 boe/d for years 2-7
    }
}
```

---

### 8.4 Database Schema Summary

**Core Tables:**
```sql
-- Projects and Opportunities
CREATE TABLE opportunities (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50),  -- upstream_oil, upstream_gas, etc.
    business_unit VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_modified TIMESTAMPTZ DEFAULT NOW()
);

-- Outcomes (probabilistic scenarios per opportunity)
CREATE TABLE outcomes (
    id UUID PRIMARY KEY,
    opportunity_id UUID REFERENCES opportunities(id),
    name VARCHAR(100),  -- Base, Optimistic, Pessimistic
    probability DECIMAL(5,4),  -- 0.0000 to 1.0000
    CONSTRAINT valid_probability CHECK (probability >= 0 AND probability <= 1)
);

-- Input Metrics (time-series data)
CREATE TABLE opportunity_metrics (
    id UUID PRIMARY KEY,
    opportunity_id UUID REFERENCES opportunities(id),
    outcome_id UUID REFERENCES outcomes(id),
    metric_name VARCHAR(255),
    unit VARCHAR(50),
    time_series_data JSONB,  -- [{year: 0, value: 10000}, ...]
    imported_at TIMESTAMPTZ DEFAULT NOW()
);

-- Attributes
CREATE TABLE opportunity_attributes (
    opportunity_id UUID PRIMARY KEY REFERENCES opportunities(id),
    is_fixture BOOLEAN DEFAULT FALSE,
    area VARCHAR(100),
    onshore_offshore VARCHAR(20),
    reserve_category VARCHAR(20),
    business_unit VARCHAR(100),
    price_scenario VARCHAR(100),
    custom_attributes JSONB,  -- Flexible key-value
    hierarchy JSONB
);

-- Master Data Sets
CREATE TABLE master_data_sets (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100),  -- price_scenario, toll_scenario
    applicable_to_attribute VARCHAR(100),
    applicable_to_value VARCHAR(100)
);

CREATE TABLE master_data_metrics (
    id UUID PRIMARY KEY,
    master_data_set_id UUID REFERENCES master_data_sets(id),
    metric_name VARCHAR(255),
    unit VARCHAR(50),
    time_series_data JSONB,
    is_stochastic BOOLEAN DEFAULT FALSE,
    distribution_params JSONB
);

-- Expressions
CREATE TABLE metric_expressions (
    id UUID PRIMARY KEY,
    metric_type VARCHAR(50),
    metric_name VARCHAR(255) UNIQUE,
    unit VARCHAR(50),
    formula_fyf TEXT,
    formula_pt TEXT,
    formula_ct TEXT,
    formula_total TEXT,
    formula_total_disc TEXT,
    level CHAR(1) DEFAULT 'S',  -- O, P, or S
    is_fixture BOOLEAN DEFAULT FALSE,
    is_indicator BOOLEAN DEFAULT FALSE,
    dependencies JSONB  -- [metric_name1, metric_name2, ...]
);

-- Selection Constraints
CREATE TABLE selection_constraints (
    id UUID PRIMARY KEY,
    opportunity_id UUID REFERENCES opportunities(id),
    is_integer BOOLEAN DEFAULT TRUE,
    is_active BOOLEAN DEFAULT TRUE,
    total_wi_min DECIMAL(10,4) DEFAULT 0,
    total_wi_max DECIMAL(10,4) DEFAULT 1,
    total_instances_min INTEGER DEFAULT 0,
    total_instances_max INTEGER DEFAULT 1,
    yearly_constraints JSONB  -- [{year: 0, min: 1, max: 1}, ...]
);

-- Selection Dependencies
CREATE TABLE selection_dependencies (
    id UUID PRIMARY KEY,
    is_active BOOLEAN DEFAULT TRUE,
    independent_opportunity_id UUID REFERENCES opportunities(id),
    dependent_opportunity_id UUID REFERENCES opportunities(id),
    must_or_must_not VARCHAR(20),  -- Must, Must Not
    time_offset INTEGER DEFAULT 0,
    timing_relation VARCHAR(20),  -- Before, After, During
    need_instances VARCHAR(10),
    each_instances VARCHAR(10)
);

-- Selection Groups
CREATE TABLE selection_groups (
    id UUID PRIMARY KEY,
    name VARCHAR(255),
    group_type VARCHAR(50),  -- Exclusive, Inclusive, etc.
    is_active BOOLEAN DEFAULT TRUE,
    total_instances_min INTEGER,
    total_instances_max INTEGER,
    yearly_constraints JSONB
);

CREATE TABLE group_members (
    group_id UUID REFERENCES selection_groups(id),
    opportunity_id UUID REFERENCES opportunities(id),
    is_disabled BOOLEAN DEFAULT FALSE,
    PRIMARY KEY (group_id, opportunity_id)
);

-- Metric Constraints
CREATE TABLE metric_constraints (
    id UUID PRIMARY KEY,
    metric_name VARCHAR(255),
    unit VARCHAR(50),
    is_enforced BOOLEAN DEFAULT TRUE,
    constraint_type VARCHAR(20),  -- Min, Max, Range, Equal
    is_soft BOOLEAN DEFAULT FALSE,
    penalty_weight DECIMAL(10,2),
    penalty_magnitude DECIMAL(15,2),
    default_limit DECIMAL(15,2),
    yearly_limits JSONB  -- {0: 1000, 1: 1000, ...}
);

-- Optimization Results (TimescaleDB hypertable)
CREATE TABLE optimization_results (
    scenario_id UUID NOT NULL,
    opportunity_id UUID NOT NULL,
    year INTEGER NOT NULL,
    is_selected BOOLEAN,
    start_year INTEGER,
    working_interest DECIMAL(10,4),
    instances INTEGER,
    revenue DECIMAL(15,2),
    opex DECIMAL(15,2),
    capex DECIMAL(15,2),
    production DECIMAL(15,2),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (scenario_id, opportunity_id, year)
);

-- Convert to TimescaleDB hypertable
SELECT create_hypertable('optimization_results', 'created_at');
```

---

## 9. Success Metrics & KPIs

### 9.1 Product Metrics

**Adoption & Engagement**
- Monthly Active Users (MAU)
- Daily Active Users (DAU) / MAU ratio
- Scenarios created per user per month
- Optimization runs per user per month
- Time spent in application per session

**Product Usage**
- % of customers using stochastic optimization
- % of customers using interdependency modeling
- % of customers using energy transition features
- Average portfolio size (# projects)
- Average scenario comparison sets (# scenarios)

**Performance**
- Median optimization solve time
- 95th percentile API response time
- Dashboard load time (p50, p95)
- System uptime %

### 9.2 Business Metrics

**Revenue**
- Annual Recurring Revenue (ARR)
- Customer count by tier (Small <$500M capex, Mid $500M-$2B, Large >$2B)
- Net Revenue Retention (NRR)
- Customer Acquisition Cost (CAC)
- Lifetime Value (LTV) / CAC ratio

**Customer Success**
- Net Promoter Score (NPS) target: >50
- Customer satisfaction (CSAT) target: >4.5/5
- Churn rate target: <5% annually
- % customers achieving >10% portfolio value improvement (target: 80%)
- Time to value: days from onboarding to first optimization

**Market Position**
- Market share in oil & gas portfolio optimization (target: 30% by year 3)
- Win rate vs. Product Y Planning Space in competitive deals (target: 40% year 2, 60% year 3)
- # of published case studies demonstrating value creation

---

## 10. Expression Engine Architecture

The Expression Engine is a critical component that evaluates Product X-compatible formulas to compute derived metrics. It must support both Product X's FYF/PT/CT syntax and optionally Python syntax for power users.

### 10.1 Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                   EXPRESSION REGISTRY                        │
│  Store all metric expressions from database                  │
│  - Input metrics (no formula)                               │
│  - Master Data (no formula, fixture)                        │
│  - Computed metrics (has formula)                           │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              DEPENDENCY ANALYZER                             │
│  Build dependency graph of metric references                 │
│  - Extract [Metric Name] references from formulas           │
│  - Detect circular dependencies                             │
│  - Generate topological sort (execution order)              │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│               FORMULA COMPILER                               │
│  Parse and compile formulas to executable code              │
│  - Support Product X syntax: [Metric], PT, FYF               │
│  - Convert to Python AST                                    │
│  - Add safety checks (no eval, exec, import)                │
│  - Optimize for vectorized execution                        │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              EXECUTION ENGINE                                │
│  Execute formulas in topological order                       │
│  - FYF execution (t=0, no PT reference)                     │
│  - CT execution (t>0, can reference PT)                     │
│  - Aggregation formulas (Total, TotalDisc, etc.)           │
│  - Filter by attributes/opportunities/outcomes              │
│  - Aggregate by level (O/P/S)                               │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              RESULT CACHE                                    │
│  Store computed metric values for reuse                      │
│  - Key: (metric_name, opportunity, outcome, year, level)    │
│  - Invalidate on data changes                               │
└─────────────────────────────────────────────────────────────┘
```

### 10.2 Core Components

#### A. Expression Registry

```python
# /backend/expression_engine/registry.py

from typing import Dict, List, Optional, Set
from dataclasses import dataclass
import networkx as nx

@dataclass
class MetricDefinition:
    """Single metric definition"""
    metric_name: str
    metric_type: str  # "Input", "Master Data", "Computed"
    unit: str
    
    # Formulas (Product X pattern)
    formula_fyf: Optional[str] = None  # First year
    formula_pt: Optional[str] = None   # Prior time reference
    formula_ct: Optional[str] = None   # Current time
    formula_total: Optional[str] = None  # Aggregation
    formula_total_disc: Optional[str] = None
    
    # Filtering
    level: str = "S"  # O, P, or S
    attribute_filter: Optional[str] = None
    characteristic_filter: Optional[str] = None
    
    # Flags
    is_fixture: bool = False  # Master Data
    is_indicator: bool = False  # Single value (not time series)
    
    # Dependencies (auto-generated)
    depends_on: Set[str] = None
    
    def __post_init__(self):
        if self.depends_on is None:
            self.depends_on = set()

class ExpressionRegistry:
    """
    Central registry of all metric expressions
    """
    
    def __init__(self):
        self.metrics: Dict[str, MetricDefinition] = {}
        self.dependency_graph: nx.DiGraph = nx.DiGraph()
        self.execution_order: List[str] = []
    
    def register_metric(self, metric: MetricDefinition):
        """Add metric to registry"""
        self.metrics[metric.metric_name] = metric
        
        # Extract dependencies from formulas
        self._extract_dependencies(metric)
        
        # Rebuild execution order
        self._build_execution_order()
    
    def _extract_dependencies(self, metric: MetricDefinition):
        """
        Extract metric references from formulas
        
        Patterns to match:
        - [Metric Name] - direct metric reference
        - PT - reference to prior time period of same metric
        - Built-in functions: Total([Metric]), TotalDisc([Metric]), etc.
        """
        import re
        
        # Pattern: [Metric Name]
        metric_ref_pattern = r'\[([^\]]+)\]'
        
        # Check all formula fields
        formulas = [
            metric.formula_fyf,
            metric.formula_ct,
            metric.formula_total,
            metric.formula_total_disc
        ]
        
        for formula in formulas:
            if formula:
                # Extract metric references
                matches = re.findall(metric_ref_pattern, str(formula))
                metric.depends_on.update(matches)
                
                # Add edges to dependency graph
                for referenced_metric in matches:
                    self.dependency_graph.add_edge(metric.metric_name, referenced_metric)
    
    def _build_execution_order(self):
        """
        Generate topological sort of metrics for execution
        
        Metrics with no dependencies execute first,
        then metrics that depend on them, etc.
        """
        try:
            # Reverse graph (dependencies point from child to parent)
            # We want execution order from parent to child
            reversed_graph = self.dependency_graph.reverse()
            
            # Topological sort
            self.execution_order = list(nx.topological_sort(reversed_graph))
            
        except nx.NetworkXError as e:
            # Cycle detected
            cycles = list(nx.simple_cycles(self.dependency_graph))
            raise ValueError(f"Circular dependencies detected: {cycles}")
    
    def get_metric(self, metric_name: str) -> MetricDefinition:
        """Retrieve metric definition"""
        if metric_name not in self.metrics:
            raise KeyError(f"Metric '{metric_name}' not found in registry")
        return self.metrics[metric_name]
    
    def get_execution_order(self) -> List[str]:
        """Get ordered list of metrics for execution"""
        return self.execution_order
    
    def validate_dependencies(self) -> List[str]:
        """
        Check that all referenced metrics exist
        
        Returns: List of error messages
        """
        errors = []
        
        for metric in self.metrics.values():
            for dep in metric.depends_on:
                if dep not in self.metrics:
                    errors.append(f"Metric '{metric.metric_name}' references undefined metric '{dep}'")
        
        return errors
```

#### B. Formula Compiler

```python
# /backend/expression_engine/compiler.py

import ast
import re
from typing import Dict, Any, Callable

class FormulaCompiler:
    """
    Compile Product X formulas to executable Python code
    """
    
    # Built-in functions
    BUILTIN_FUNCTIONS = {
        'Total', 'TotalDisc', 'TotalInf', 'Disc', 'CumDisc',
        'GetCumulative', 'IF', 'MAX', 'MIN', 'SUM', 'ABS',
        'SQRT', 'POW', 'EXP', 'LN', 'LOG'
    }
    
    # Reserved keywords to block
    FORBIDDEN_NAMES = {
        'eval', 'exec', 'compile', 'import', '__import__',
        'open', 'file', 'input', 'raw_input'
    }
    
    def __init__(self):
        self.compiled_cache: Dict[str, Callable] = {}
    
    def compile_formula(self, formula: str, formula_type: str = 'CT') -> Callable:
        """
        Compile formula to executable function
        
        Args:
            formula: Formula string in Product X syntax
            formula_type: 'FYF', 'CT', 'Total', etc.
        
        Returns:
            Compiled function that takes (metrics, master_data, t, project, outcome, level)
        """
        # Check cache
        cache_key = f"{formula_type}:{formula}"
        if cache_key in self.compiled_cache:
            return self.compiled_cache[cache_key]
        
        # Transform Product X syntax to Python
        python_code = self._transform_to_python(formula, formula_type)
        
        # Parse to AST
        try:
            tree = ast.parse(python_code, mode='eval')
        except SyntaxError as e:
            raise ValueError(f"Invalid formula syntax: {formula}\nError: {str(e)}")
        
        # Validate AST (security check)
        self._validate_ast(tree)
        
        # Compile to code object
        code = compile(tree, '<formula>', 'eval')
        
        # Create function wrapper
        def formula_function(metrics, master_data, t, project=None, outcome=None, level='S'):
            # Build evaluation context
            context = {
                'metrics': metrics,
                'master_data': master_data,
                't': t,
                'project': project,
                'outcome': outcome,
                'PT': metrics.get('_prior', {}),  # Prior time values
                
                # Built-in functions
                'Total': self._builtin_total,
                'TotalDisc': self._builtin_total_disc,
                'IF': lambda cond, true_val, false_val: true_val if cond else false_val,
                'MAX': max,
                'MIN': min,
                'SUM': sum,
                'ABS': abs,
            }
            
            # Execute
            try:
                return eval(code, {"__builtins__": {}}, context)
            except Exception as e:
                raise RuntimeError(f"Error evaluating formula '{formula}': {str(e)}")
        
        # Cache and return
        self.compiled_cache[cache_key] = formula_function
        return formula_function
    
    def _transform_to_python(self, formula: str, formula_type: str) -> str:
        """
        Transform Product X syntax to Python
        
        Transformations:
        - [Metric Name] → metrics['Metric Name'][t]
        - [MD - Price] → master_data['MD - Price'][t]
        - PT → metrics['current_metric'][t-1]
        """
        python_code = formula
        
        # Transform metric references [Metric Name]
        def replace_metric_ref(match):
            metric_name = match.group(1)
            
            # Check if Master Data
            if metric_name.startswith('MD -') or metric_name.startswith('OMD'):
                return f"master_data['{metric_name}'][t]"
            else:
                return f"metrics['{metric_name}'][t]"
        
        python_code = re.sub(r'\[([^\]]+)\]', replace_metric_ref, python_code)
        
        # Transform PT (Prior Time)
        # PT alone means current metric's prior value
        # This needs context of current metric name
        python_code = python_code.replace('PT', "metrics['_current'][t-1] if t > 0 else 0")
        
        return python_code
    
    def _validate_ast(self, tree: ast.AST):
        """
        Validate AST for security
        
        Block dangerous operations:
        - eval, exec, compile
        - import statements
        - attribute access on unsafe objects
        """
        for node in ast.walk(tree):
            # Block function calls to forbidden names
            if isinstance(node, ast.Name):
                if node.id in self.FORBIDDEN_NAMES:
                    raise ValueError(f"Forbidden function/variable: {node.id}")
            
            # Block imports
            if isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
                raise ValueError("Import statements not allowed in formulas")
    
    # Built-in function implementations
    def _builtin_total(self, metric_values):
        """Undiscounted sum"""
        return sum(metric_values)
    
    def _builtin_total_disc(self, metric_values, discount_rate=0.10):
        """NPV calculation"""
        return sum(value / (1 + discount_rate)**t for t, value in enumerate(metric_values))
```

#### C. Execution Engine

```python
# /backend/expression_engine/executor.py

from typing import Dict, List, Any
import numpy as np
from collections import defaultdict

class ExecutionEngine:
    """
    Execute compiled formulas in correct order
    """
    
    def __init__(self, registry: ExpressionRegistry, compiler: FormulaCompiler):
        self.registry = registry
        self.compiler = compiler
        self.result_cache: Dict[tuple, Any] = {}
    
    def evaluate_all_metrics(
        self,
        opportunities: List[Dict],
        master_data: Dict[str, np.ndarray],
        planning_horizon: int
    ) -> Dict[str, np.ndarray]:
        """
        Evaluate all computed metrics for all opportunities and time periods
        
        Args:
            opportunities: List of opportunity dicts with input metrics
            master_data: Dict of {metric_name: time_series_array}
            planning_horizon: Number of years
        
        Returns:
            Dict of {metric_name: computed_values} for all metrics
        """
        results = {}
        
        # Initialize with input metrics
        for opp in opportunities:
            for metric_name, time_series in opp.get('metrics', {}).items():
                if metric_name not in results:
                    results[metric_name] = {}
                
                # Store by opportunity and outcome
                key = (opp['name'], opp.get('outcome', 'Base'))
                results[metric_name][key] = time_series
        
        # Execute computed metrics in dependency order
        execution_order = self.registry.get_execution_order()
        
        for metric_name in execution_order:
            metric = self.registry.get_metric(metric_name)
            
            # Skip input metrics (already loaded)
            if metric.metric_type == "Input":
                continue
            
            # Skip Master Data (already loaded)
            if metric.is_fixture:
                continue
            
            # Compute metric
            results[metric_name] = self._evaluate_metric(
                metric,
                results,
                master_data,
                opportunities,
                planning_horizon
            )
        
        return results
    
    def _evaluate_metric(
        self,
        metric: MetricDefinition,
        current_results: Dict,
        master_data: Dict,
        opportunities: List[Dict],
        planning_horizon: int
    ) -> Dict:
        """
        Evaluate single computed metric
        
        Returns: Dict of {(opportunity, outcome): time_series}
        """
        metric_results = {}
        
        # Filter opportunities based on metric filters
        filtered_opps = self._apply_filters(opportunities, metric)
        
        for opp in filtered_opps:
            opp_name = opp['name']
            outcome = opp.get('outcome', 'Base')
            
            # Compute time series for this opportunity-outcome
            time_series = np.zeros(planning_horizon)
            
            for t in range(planning_horizon):
                # Determine which formula to use
                if t == 0 and metric.formula_fyf:
                    # First year formula
                    formula = metric.formula_fyf
                    formula_type = 'FYF'
                elif metric.formula_ct:
                    # Current time formula
                    formula = metric.formula_ct
                    formula_type = 'CT'
                else:
                    # No formula for this period
                    continue
                
                # Compile formula
                formula_func = self.compiler.compile_formula(formula, formula_type)
                
                # Build context with prior time values if needed
                metrics_context = self._build_metrics_context(
                    current_results,
                    opp_name,
                    outcome,
                    t
                )
                
                # Evaluate
                try:
                    value = formula_func(
                        metrics_context,
                        master_data,
                        t,
                        project=opp_name,
                        outcome=outcome,
                        level=metric.level
                    )
                    time_series[t] = value
                except Exception as e:
                    # Log error and use 0
                    print(f"Error evaluating {metric.metric_name} for {opp_name} at t={t}: {str(e)}")
                    time_series[t] = 0
            
            # Store result
            key = (opp_name, outcome)
            metric_results[key] = time_series
        
        return metric_results
    
    def _apply_filters(self, opportunities: List[Dict], metric: MetricDefinition) -> List[Dict]:
        """
        Filter opportunities based on metric's attribute/characteristic filters
        """
        filtered = opportunities
        
        if metric.attribute_filter and metric.characteristic_filter:
            filtered = [
                opp for opp in filtered
                if opp.get('attributes', {}).get(metric.attribute_filter) == metric.characteristic_filter
            ]
        
        if metric.opportunity_filter:
            filtered = [opp for opp in filtered if opp['name'] == metric.opportunity_filter]
        
        if metric.outcome_filter:
            filtered = [opp for opp in filtered if opp.get('outcome') == metric.outcome_filter]
        
        return filtered
    
    def _build_metrics_context(
        self,
        results: Dict,
        opportunity: str,
        outcome: str,
        time_period: int
    ) -> Dict:
        """
        Build dictionary of metric values accessible to formula
        
        Includes current time and prior time values
        """
        context = {}
        
        key = (opportunity, outcome)
        
        for metric_name, metric_data in results.items():
            if key in metric_data:
                time_series = metric_data[key]
                
                # Current time value
                context[metric_name] = {
                    't': time_series[time_period] if time_period < len(time_series) else 0
                }
                
                # Add prior time to special _prior dict
                if time_period > 0:
                    if '_prior' not in context:
                        context['_prior'] = {}
                    context['_prior'][metric_name] = time_series[time_period - 1]
        
        return context
```

### 10.3 Usage Example

```python
# Example: Evaluate all metrics for portfolio

from expression_engine.registry import ExpressionRegistry, MetricDefinition
from expression_engine.compiler import FormulaCompiler
from expression_engine.executor import ExecutionEngine

# 1. Build registry
registry = ExpressionRegistry()

# Register input metrics (from database)
registry.register_metric(MetricDefinition(
    metric_name="Production Rate - Oil",
    metric_type="Input",
    unit="bbl/d"
))

registry.register_metric(MetricDefinition(
    metric_name="Opex",
    metric_type="Input",
    unit="$M"
))

# Register Master Data
registry.register_metric(MetricDefinition(
    metric_name="MD - Price - Oil",
    metric_type="Master Data",
    unit="$/bbl",
    is_fixture=True
))

# Register computed metrics
registry.register_metric(MetricDefinition(
    metric_name="Revenue - Oil",
    metric_type="Computed",
    unit="$M",
    formula_ct="[Production Rate - Oil] * [MD - Price - Oil] * 365.25 / 1000000",
    level="O"  # Calculate per outcome
))

registry.register_metric(MetricDefinition(
    metric_name="BTAX Cash Flow",
    metric_type="Computed",
    unit="$M",
    formula_ct="[Revenue - Oil] - [Opex]",
    level="P"  # Aggregate to project level
))

registry.register_metric(MetricDefinition(
    metric_name="Cumulative Production",
    metric_type="Computed",
    unit="MMbbl",
    formula_fyf="[Production Rate - Oil] / 365.25 / 1000",  # First year
    formula_ct="PT + [Production Rate - Oil] / 365.25 / 1000",  # Subsequent years (add to prior)
    level="O"
))

# 2. Validate
errors = registry.validate_dependencies()
if errors:
    print("Validation errors:", errors)
    exit(1)

# 3. Create compiler and executor
compiler = FormulaCompiler()
executor = ExecutionEngine(registry, compiler)

# 4. Prepare data
opportunities = [
    {
        "name": "Alpha Base",
        "outcome": "Base",
        "metrics": {
            "Production Rate - Oil": np.array([9375, 8829, 8315, ...]),  # bbl/d
            "Opex": np.array([102656, 97575, 92789, ...])  # $M
        }
    }
]

master_data = {
    "MD - Price - Oil": np.array([75, 75, 75, ...])  # $/bbl
}

planning_horizon = 30

# 5. Execute
results = executor.evaluate_all_metrics(
    opportunities,
    master_data,
    planning_horizon
)

# 6. Access results
revenue_oil = results["Revenue - Oil"][("Alpha Base", "Base")]
print(f"Year 1 oil revenue: ${revenue_oil[0]:.2f}M")

btax_cf = results["BTAX Cash Flow"][("Alpha Base", "Base")]
print(f"NPV (manual): ${np.sum(btax_cf / (1.1 ** np.arange(30))):.2f}M")
```

### 10.4 Performance Optimizations

1. **Vectorization**: Where possible, compute entire time series at once using NumPy
2. **Caching**: Cache compiled formulas and intermediate results
3. **Parallel execution**: Compute independent metrics in parallel
4. **Lazy evaluation**: Only compute metrics needed for optimization objective
5. **Incremental updates**: Recompute only affected metrics when data changes

---

## 11. Development Roadmap

### Phase 0: Foundation (Months 1-3)
**Objective:** Technical foundation and MVP architecture

**Deliverables:**
- Infrastructure setup (AWS/Azure, CI/CD, monitoring)
- Core data models and database schema
- Authentication & authorization (SSO, RBAC)
- Basic API framework (FastAPI)
- Basic React UI shell with routing
- Project import from Excel/CSV

**Team:** 2 backend, 1 frontend, 1 DevOps

---

### Phase 1: MVP - Deterministic Optimization (Months 4-7)
**Objective:** Launch minimum viable product with core optimization

**Deliverables:**
- **Data Management:**
  - Project library (500+ projects)
  - Economic assumptions (price decks, fiscal regimes)
  - Basic interdependency modeling (prerequisites, mutex)
  
- **Optimization:**
  - Deterministic MILP optimization
  - 5 constraint types (CAPEX annual, cumulative, production, emissions, infrastructure)
  - Single objective (maximize NPV)
  - 20-year horizon support
  
- **Visualization:**
  - Executive dashboard
  - CAPEX and production profile charts
  - Portfolio composition views
  - Basic Excel export
  
- **Scenarios:**
  - Create/save/run scenarios
  - Scenario comparison table

**Success Criteria:**
- Solve 200-project portfolio in <3 minutes
- 3 pilot customers onboarded
- Demonstrate 10%+ improvement vs. manual planning for 2 customers

**Team:** 3 backend, 2 frontend, 1 data scientist, 1 DevOps, 1 PM

---

### Phase 2: Differentiation Features (Months 8-12)
**Objective:** Add key differentiators vs. incumbents

**Deliverables:**
- **Advanced Interdependencies:**
  - Shared infrastructure capacity modeling
  - Synergy quantification
  - Resource constraints
  - Network visualization
  
- **Multi-Objective Optimization:**
  - Pareto frontier generation
  - NPV vs. Emissions trade-offs
  - Interactive Pareto explorer
  
- **Energy Transition:**
  - Mixed portfolio optimization (hydrocarbons + renewables)
  - Carbon pricing scenarios
  - Transition pathway visualization
  
- **Sensitivity Analysis:**
  - Tornado charts
  - One-way sensitivities
  - Basic Monte Carlo (1,000 scenarios)
  
- **Reporting:**
  - PowerPoint auto-generation
  - Detailed Excel models
  - Executive summary narratives (AI-generated)

**Success Criteria:**
- 15 paying customers
- 2 case studies showing >15% value improvement
- NPS >40
- Win 2 competitive deals vs. Product Y

**Team:** 4 backend, 2 frontend, 2 data scientists, 1 DevOps, 1 PM, 1 customer success

---

### Phase 3: Advanced Analytics (Months 13-18)
**Objective:** Establish technical leadership with advanced capabilities

**Deliverables:**
- **Stochastic Optimization:**
  - Two-stage stochastic programming
  - Scenario tree generation and reduction
  - CVaR risk constraints
  - Recourse decision modeling
  
- **Real Options:**
  - Option to defer valuation
  - Option to abandon
  - Compound options for multi-stage projects
  - Embedded option value in portfolio NPV
  
- **AI/ML Enhancements:**
  - Surrogate models for fast approximate optimization
  - Scenario clustering
  - Anomaly detection in project data
  
- **Collaboration:**
  - Multi-user real-time collaboration
  - Approval workflows
  - Comment threads
  - Slack/Teams integration

**Success Criteria:**
- 40 customers
- Stochastic optimization adopted by 60% of customers
- Real options demonstrates >20% value improvement for marginal field portfolios
- Win 5 competitive deals vs. Product Y

**Team:** 5 backend, 3 frontend, 3 data scientists, 1 DevOps, 1 PM, 2 customer success

---

### Phase 4: Enterprise Scale (Months 19-24)
**Objective:** Enterprise readiness and scale

**Deliverables:**
- **Performance Optimization:**
  - Distributed optimization (parallel scenario solving)
  - GPU acceleration for Monte Carlo
  - 2,000-project portfolio support
  
- **Enterprise Features:**
  - SSO with all major providers
  - SOC 2 Type II certification
  - Custom data retention policies
  - White-label option
  
- **Advanced Reporting:**
  - Custom report builder (drag-and-drop)
  - Scheduled/automated reports
  - API for external BI tools
  
- **Industry Expansion:**
  - Mining portfolio optimization module
  - Utilities capital planning module
  - Private equity fund portfolio module

**Success Criteria:**
- 75 customers
- $50M ARR
- Category leader positioning (top 3 in Gartner/Forrester if evaluated)
- 3 customers with >1,000 project portfolios

**Team:** 6 backend, 4 frontend, 3 data scientists, 2 DevOps, 2 PM, 4 customer success

---

## 12. Dependencies & Integration Requirements

### 10.1 Third-Party Integrations

**Optimization Solvers (Critical)**
- Gurobi: Commercial license required (~$30K/year academic, ~$100K/year commercial)
- Alternative: Google OR-Tools (free, open-source, but slower for large MILP)

**Data Sources (High Priority)**
- Product Y Planning Space: API integration for project import (if available)
- PHDWin: CSV export format support
- Excel: openpyxl library for complex workbook parsing
- Market data providers: Bloomberg, Refinitiv (price deck feeds)

**Infrastructure (Critical)**
- Cloud provider: AWS or Azure
- Authentication: Okta, Auth0, or Azure AD
- Monitoring: DataDog, New Relic, or CloudWatch
- Email: SendGrid or AWS SES

**Collaboration (Medium Priority)**
- Slack API (notifications)
- Microsoft Teams webhooks
- Google Workspace (SSO, Drive integration)

### 10.2 Open Source Dependencies (Python)

**Core:**
- FastAPI, Uvicorn (API)
- SQLAlchemy (ORM)
- Alembic (database migrations)
- Pydantic (validation)
- Celery, Redis (task queue)

**Optimization:**
- Pyomo (modeling)
- Gurobi Python API or OR-Tools
- Scipy (convex optimization)
- NumPy, Pandas (data)

**ML/Analytics:**
- Scikit-learn
- XGBoost
- Matplotlib, Seaborn (visualization)

**Testing:**
- Pytest
- Coverage.py
- Locust (load testing)

---

## 13. Risk Assessment & Mitigation

### 11.1 Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| **Gurobi license cost too high** | Medium | High | Implement OR-Tools fallback; negotiate academic pricing initially; build licensing cost into pricing model |
| **Optimization doesn't scale to 500 projects** | Low | Critical | Implemented TimeSeriesStateManager architecture prevents formula explosion; hybrid optimization reduces variables by 60-80%; lazy constraints for large portfolios; proven scalable to 2000+ projects in academic literature |
| **Temporal state variable formula explosion** | Low | Critical | SOLVED via explicit state variable formulation in Section 4.3; creates 150K variables vs. infinite recursive calls; sparse matrix handling; hybrid pre-computation approach |
| **Stochastic optimization too slow** | High | Medium | Start with 2-stage only; implement scenario reduction; use parallel computing; consider approximate methods; temporal aggregation for distant years |
| **Real options math too complex for users** | High | Medium | Provide simple toggle (include/exclude options); auto-calibrate volatility; explain in plain language |
| **Data quality issues break optimization** | High | Medium | Robust validation on import; graceful degradation; clear error messages; data quality dashboard |
| **Max/min non-linear constraints** | Low | Medium | SOLVED via Big-M linearization with auxiliary binary variables (Section 4.3.1); industry-standard approach |
| **Interdependency modeling at scale** | Medium | High | Graph-based dependency modeling with NetworkX; automatic conversion to MILP constraints; visual validation tools; handles 500+ projects with complex networks |

### 11.2 Market Risks

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| **Product Y bundles aggressively** | Medium | High | Focus on differentiation (interdependencies, stochastic, real options); target customers frustrated with Product Y |
| **Market too small (only large O&G)** | Low | Critical | Expand to utilities, mining, private equity early; modular pricing for smaller customers |
| **Customers don't trust "black box" optimization** | High | High | Full transparency mode showing all constraints; shadow price explanations; validation against manual scenarios |
| **Energy transition makes O&G tools obsolete** | Low | Medium | Build energy transition features as core (not bolt-on); position as "future-proof" |
| **Long sales cycles (12-18 months)** | High | Medium | Freemium tier for small portfolios; quick wins (30-day pilots); land-and-expand strategy |

### 11.3 Execution Risks

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| **Can't hire optimization experts** | Medium | High | Partner with university research groups; build simple cases first; document extensively |
| **Scope creep delays MVP** | High | Medium | Strict MVP definition; ruthless prioritization; decline custom features in phase 1 |
| **Petroleum domain knowledge gap** | Medium | High | Hire 1-2 petroleum engineers; partner with industry consultants; early customer co-development |
| **Underestimate infrastructure costs** | Medium | Medium | Start with managed services; monitor costs weekly; build cost model into product roadmap |

---

## 14. Key Architectural Decisions

### 11.1 Temporal State Variables vs. Recursive Formulations

**Decision:** Use explicit state variables for all time-dependent metrics instead of recursive function calls.

**Rationale:**
- **Problem:** Calculating enterprise value at year 30 for 500 projects with metrics depending on previous years creates formula explosion (30-level recursion × 500 projects = computational impossibility)
- **Solution:** Create explicit variables for each (project, year, metric) combination with linear constraints linking adjacent years
- **Result:** Transforms infinite recursive problem into manageable 150,000-variable MILP (still large but solvable in minutes)

**Trade-offs:**
- ✅ Pros: Provably optimal, handles any interdependency pattern, solver-native approach, scalable
- ❌ Cons: More variables than heuristic approaches, requires significant RAM (1-2 GB)
- **Verdict:** Essential for correctness; performance is acceptable with optimizations

### 11.2 Graph Theory + MILP Hybrid Architecture

**Decision:** Use graph theory for modeling and visualization, MILP for optimization.

**Rationale:**
- **Graph Theory strengths:** Natural representation of dependencies, excellent for visualization, fast cycle detection
- **Graph Theory limitations:** Cannot optimize under complex constraints (budgets, multiple objectives, timing)
- **MILP strengths:** Provably optimal solutions, handles any linear constraint, well-established solvers
- **Integration:** NetworkX builds dependency graph → converts to MILP constraints → Gurobi optimizes → D3.js visualizes

**Trade-offs:**
- ✅ Pros: Best of both worlds, executive-friendly visualization, mathematically rigorous optimization
- ❌ Cons: Two-component architecture, additional complexity vs. pure graph or pure MILP
- **Verdict:** Necessary to achieve both usability and correctness

### 11.3 Hybrid Pre-Computation for Independent Projects

**Decision:** Pre-compute NPV for independent projects, use state variables only for interdependent projects.

**Rationale:**
- **Observation:** 70-90% of projects in typical portfolios have no interdependencies
- **Optimization:** Pre-calculate standalone NPV for independent projects (O(1) lookup), full state variables only for interdependent subset
- **Impact:** Reduces optimization variables by 60-80% for typical portfolios

**Example Performance:**
- **Full state variables:** 500 projects × 30 years × 10 metrics = 150,000 variables → 5-15 min solve time
- **Hybrid approach:** 100 interdependent projects × 30 years × 10 metrics = 30,000 variables → 1-3 min solve time
- **Improvement:** 5-10× faster with identical optimality

**Trade-offs:**
- ✅ Pros: Massive performance gain, no loss of optimality, simpler constraints for most projects
- ❌ Cons: Additional preprocessing step, need to correctly identify independent projects
- **Verdict:** Critical for production performance; reduces time-to-insight for users

### 11.4 Linearization of Max/Min via Big-M

**Decision:** Convert all max/min operations to linear constraints using auxiliary binary variables and large constants (Big-M method).

**Rationale:**
- **Problem:** Many real-world constraints involve max/min (e.g., `operating_cost = max(base_cost, threshold)`)
- **MILP requirement:** All constraints must be linear
- **Big-M method:** Industry-standard linearization technique used by all major portfolio optimizers
- **Correctness:** Provably equivalent to original non-linear formulation when M is sufficiently large

**Implementation:**
```python
# Original: cost = max(base_cost, threshold)
# Linearized:
cost >= base_cost          # Always
cost >= threshold          # Always  
cost <= base_cost + M*(1-binary)   # Forces cost = base_cost when binary=1
cost <= threshold + M*binary        # Forces cost = threshold when binary=0
```

**Trade-offs:**
- ✅ Pros: Maintains MILP solvability, exact (not approximate), well-understood by solvers
- ❌ Cons: Adds binary variables (increases problem size), requires careful M selection
- **Verdict:** Standard practice; no viable alternative for exact optimization

### 11.5 TimescaleDB for Time-Series Results Storage

**Decision:** Use PostgreSQL with TimescaleDB extension instead of standard relational storage.

**Rationale:**
- **Data pattern:** Optimization results are inherently time-series (project × year × metrics)
- **Query pattern:** Users frequently query "all metrics for year 15-20" or "project X over all years"
- **TimescaleDB advantages:** 
  - Automatic partitioning by time
  - 10-100× faster time-range queries
  - Native continuous aggregates (real-time dashboard metrics)
  - Compression reduces storage by 90% for historical scenarios

**Trade-offs:**
- ✅ Pros: Massive query performance for dashboards, efficient storage, PostgreSQL compatibility
- ❌ Cons: Additional dependency, slight operational complexity
- **Verdict:** Essential for responsive UI with 30-year time horizons; proven at scale

### 11.6 Gurobi as Primary Solver (with OR-Tools Fallback)

**Decision:** Use commercial Gurobi solver as default, with Google OR-Tools as open-source alternative.

**Rationale:**
- **Performance:** Gurobi is 3-10× faster than open-source solvers for large MILP problems
- **Features:** Better handling of quadratic constraints (needed for phase 3 real options)
- **Support:** Commercial support critical for enterprise customers
- **Cost:** ~$100K/year commercial license, but enables product to work at 500-project scale

**OR-Tools fallback:**
- Free and open-source
- Adequate performance for <200 project portfolios
- Enables freemium tier and academic use
- Fallback if customer won't pay Gurobi licensing

**Trade-offs:**
- ✅ Pros: Best performance, enterprise credibility, proven at scale
- ❌ Cons: Significant licensing cost, vendor dependency
- **Verdict:** Gurobi for production, OR-Tools for freemium; cost absorbed in pricing

---

## 15. Open Questions & Decisions Needed

### 15.1 Product Decisions
- [ ] **Pricing model:** Per-user SaaS vs. per-portfolio-size vs. value-based (% of CAPEX optimized)?
- [ ] **Freemium tier:** Offer free version for <50 projects to drive adoption?
- [ ] **Solver licensing:** Pass Gurobi costs to customers or absorb in product pricing?
- [ ] **On-premise option:** Required for certain oil majors or cloud-only initially?

### 15.2 Technical Decisions
- [ ] **Cloud provider:** AWS (more services) vs. Azure (better O&G industry presence)?
- [ ] **Frontend framework:** Next.js (React) vs. SvelteKit vs. Vue.js + Nuxt?
- [ ] **Database:** PostgreSQL + TimescaleDB vs. specialized time-series DB?
- [ ] **Real-time features:** WebSockets for live collaboration or poll-based?

### 15.3 Go-to-Market Decisions
- [ ] **Initial target segment:** Majors (long sales, big deals) vs. independents (faster sales, smaller deals)?
- [ ] **Geographic focus:** Start US/Canada or international (Middle East, North Sea)?
- [ ] **Partnership strategy:** Resell through consultancies (McKinsey, BCG) or direct sales only?
- [ ] **Open core vs. closed source:** Open source core optimizer, monetize UI/enterprise features?

---

## 16. Appendices

### A. Glossary

**Financial & Business Terms:**
- **CAPEX:** Capital Expenditure, upfront investment required
- **OPEX:** Operating Expenditure, ongoing costs
- **NPV:** Net Present Value, discounted value of future cash flows
- **IRR:** Internal Rate of Return
- **EUR:** Estimated Ultimate Recovery (oil/gas reserves)
- **PSC:** Production Sharing Contract
- **P10/P50/P90:** Probability levels (P50 = 50% chance of exceeding)

**Optimization Terms:**
- **MILP:** Mixed Integer Linear Programming - optimization with both continuous and discrete (integer/binary) variables
- **SDDP:** Stochastic Dual Dynamic Programming - method for multi-stage optimization under uncertainty
- **CVaR:** Conditional Value at Risk, average loss in worst X% of scenarios
- **Pareto frontier:** Set of non-dominated solutions in multi-objective optimization
- **Big-M Reformulation:** Technique to linearize max/min constraints using large constants and binary variables
- **MIP Gap:** Difference between best solution found and theoretical optimal (lower is better)
- **Shadow Price:** Value of relaxing a constraint by one unit (dual variable)

**Temporal Optimization Terms:**
- **State Variable:** Explicit variable representing system state at a specific time period (e.g., debt[project, year])
- **Temporal Constraint:** Constraint linking state variables across adjacent time periods (e.g., debt[t] = debt[t-1] + borrowing[t])
- **Formula Explosion:** Problem where recursive calculations create exponentially growing formulas
- **Sparse Matrix:** Matrix where most elements are zero, allowing efficient storage and computation
- **Lazy Constraint Generation:** Technique where constraints are added only when needed, reducing problem size
- **Temporal Aggregation:** Reducing time resolution for distant periods (e.g., annual → quinquennial)
- **Hybrid Optimization:** Combining pre-computation for independent components with full optimization for interdependent ones

**Graph Theory Terms:**
- **Graph (Network):** Mathematical structure of nodes (projects) and edges (relationships)
- **Directed Graph (DiGraph):** Graph where edges have direction (A → B is different from B → A)
- **Node/Vertex:** Individual element in graph (represents a project)
- **Edge:** Connection between nodes (represents dependency or relationship)
- **Adjacency Matrix:** Matrix representation of graph where entry (i,j) = 1 if edge exists from node i to node j
- **Centrality:** Measure of importance/influence of a node in the network
- **Cycle Detection:** Finding circular dependencies (A → B → C → A)
- **Minimum Spanning Tree (MST):** Subset of edges connecting all nodes with minimum total weight
- **Network Topology:** Structure and layout of connections in a graph

**Project Portfolio Management Terms:**
- **Interdependency:** Relationship where one project affects another (shared resources, prerequisites, synergies)
- **Prerequisite Dependency:** Project B cannot start until Project A completes
- **Mutual Exclusivity:** Only one project from a set can be selected (mutex constraint)
- **Synergy:** Positive interaction where combined value exceeds sum of individual values
- **Resource Constraint:** Limitation on available resources (budget, personnel, equipment)
- **Shared Infrastructure:** Physical assets used by multiple projects (platforms, pipelines, facilities)

### B. References

**Competitive Intelligence:**
- Willigers, B., Weis, R., & Majou, F. (2013). "Creating Portfolio Insights by a Practical Multimethod Optimization Approach." SPE Economics & Management, SPE-146583-PA.
- Copperleaf Technologies. "Value Framework Methodology." https://www.copperleaf.com
- Product Y Software. "Planning Space Portfolio Documentation." https://www.Product Ysoftware.com
- Gurobi Optimization. "Mixed Integer Programming." https://www.gurobi.com
- Planisware. "Portfolio Optimization with Swarm Intelligence." https://planisware.com

**Temporal State Optimization & MILP Formulations:**
- Arratia-Martinez, N. M., et al. (2021). "Project Portfolio Selection and Scheduling with Resource Allocation, Synergies, and Project Divisibility." Mathematical Problems in Engineering. DOI: 10.1155/2021/4163287
- Pérez, F., & Gómez, T. (2016). "Linear solution schemes for Mean-SemiVariance Project portfolio selection problems: An application in the oil and gas industry." Omega, 68, 39-48.
- Ghasemzadeh, F., & Archer, N. (1999). "Project portfolio selection through decision support." Decision Support Systems, 29(1), 73-88.

**Graph Theory for Portfolio Interdependencies:**
- Cajas, D. (2023). "A Graph Theory Approach to Portfolio Optimization." SSRN Working Paper.
- Liu, Y., et al. (2017). "Information Technology Project Portfolio Implementation Process Optimization Based on Complex Network Theory and Entropy." Entropy, 19(6), 287.

**Computational Performance:**
- Bertsimas, D., & Cory-Wright, R. (2022). "On the scalability of optimal decision trees: an integer programming approach." INFORMS Journal on Optimization.
- Nemhauser, G. L., & Wolsey, L. A. (1988). "Integer and Combinatorial Optimization." Wiley-Interscience.

**Industry Applications:**
- Orman, M. M., & Duggan, T. E. (1999). "Applying modern portfolio theory to upstream investment decision making." Journal of Petroleum Technology, 51(3), 50-53.
- Sira, E. (2013). "Portfolio optimization in the oil and gas industry: A scatter search approach." Petroleum Science and Engineering.

### C. Contact & Contributors

**Product Owner:** [Name]  
**Technical Lead:** [Name]  
**Engineering Manager:** [Name]  
**Design Lead:** [Name]  

**Reviewers:**
- [ ] VP Engineering
- [ ] CTO
- [ ] Head of Product
- [ ] Customer Advisory Board (3 pilot customers)

---

**Document Status:** DRAFT - Awaiting stakeholder review  
**Next Review Date:** [Date]  
**Approval Required From:** CTO, VP Product, VP Engineering

---

*End of PRD*
