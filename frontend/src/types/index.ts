/**
 * TypeScript type definitions for Portfolio OptiSim.
 *
 * Mirrors the Pydantic schemas from the backend API.
 */

// ---------------------------------------------------------------------------
// Projects / Opportunities
// ---------------------------------------------------------------------------

export interface Opportunity {
  id: string;
  name: string;
  type: string | null;
  business_unit: string | null;
  country: string | null;
  created_at: string;
  updated_at: string;
}

export interface Outcome {
  id: string;
  opportunity_id: string;
  name: string;
  weight: number;
}

export interface OpportunityWithOutcomes extends Opportunity {
  outcomes: Outcome[];
}

// ---------------------------------------------------------------------------
// Scenarios
// ---------------------------------------------------------------------------

export type ScenarioStatus =
  | "DRAFT"
  | "QUEUED"
  | "RUNNING"
  | "COMPLETED"
  | "FAILED"
  | "CANCELLED";

export interface Scenario {
  id: string;
  name: string;
  description: string | null;
  objective_function: string;
  planning_horizon_years: number;
  discount_rate: number;
  status: ScenarioStatus;
  optimization_method: string | null;
  optimization_settings: Record<string, unknown> | null;
  created_at: string;
  updated_at: string;
}

// ---------------------------------------------------------------------------
// Optimization
// ---------------------------------------------------------------------------

export interface OptimizationStatus {
  scenario_id: string;
  task_id: string | null;
  status: string;
  message: string | null;
  progress: number | null;
  solve_time_seconds: number | null;
  mip_gap: number | null;
  objective_value: number | null;
}

export interface SolverInfo {
  display_name: string;
  is_commercial: boolean;
  available: boolean;
}

// ---------------------------------------------------------------------------
// Dependencies
// ---------------------------------------------------------------------------

export interface SelectionDependency {
  id: string;
  parent_opportunity_id: string;
  child_opportunity_id: string;
  dependency_type: string;
  time_offset_years: number | null;
  timing_relation: string | null;
  synergy_value: number | null;
  capacity_limit: number | null;
  created_at: string;
}

export interface SelectionGroup {
  id: string;
  name: string;
  group_type: string;
  constraint_value: number | null;
  created_at: string;
  updated_at: string;
}

// ---------------------------------------------------------------------------
// Analytics
// ---------------------------------------------------------------------------

export interface MonteCarloResult {
  num_simulations: number;
  mean_npv: number;
  std_npv: number;
  p10: number;
  p50: number;
  p90: number;
  prob_positive: number;
}

export interface SensitivityFactor {
  parameter_name: string;
  base_value: number;
  low_value: number;
  high_value: number;
  low_result: number;
  high_result: number;
  impact: number;
}

// ---------------------------------------------------------------------------
// API Response Wrappers
// ---------------------------------------------------------------------------

export interface PaginationMeta {
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}

export interface PaginatedResponse<T> {
  data: T[];
  meta: PaginationMeta;
}

export interface ApiError {
  error: {
    code: string;
    message: string;
    details: Record<string, unknown> | null;
  };
}
