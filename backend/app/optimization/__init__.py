"""Portfolio optimization engine.

Core modules:
- temporal_state_manager: Explicit state variables for time-dependent metrics
- milp_builder: Pyomo ConcreteModel construction
- solver_interface: Pluggable solver abstraction (HiGHS, Gurobi, etc.)
- constraint_generators: Selection, dependency, group, metric constraints
- linearization: Big-M reformulations for non-linear operations
- hybrid_optimizer: Orchestrates the full optimization pipeline
"""
