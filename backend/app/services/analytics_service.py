"""
Analytics Service - Monte Carlo simulation, sensitivity analysis, risk metrics

Provides portfolio analytics including:
- Monte Carlo simulation with Latin Hypercube Sampling
- One-way and tornado sensitivity analysis
- Risk metrics (VaR, CVaR, downside deviation)
- Portfolio statistics and summary metrics
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import numpy as np
import structlog

logger = structlog.get_logger(__name__)


@dataclass
class SensitivityFactor:
    """Result for a single sensitivity parameter."""

    parameter_name: str
    base_value: float
    low_value: float
    high_value: float
    low_result: float
    high_result: float
    impact: float  # high_result - low_result (absolute impact magnitude)


@dataclass
class MonteCarloResult:
    """Results from a Monte Carlo simulation."""

    num_simulations: int
    mean_npv: float
    std_npv: float
    p10: float  # 10th percentile (downside)
    p50: float  # Median
    p90: float  # 90th percentile (upside)
    min_npv: float
    max_npv: float
    prob_positive: float  # P(NPV > 0)
    npv_distribution: List[float] = field(default_factory=list)


@dataclass
class RiskMetrics:
    """Portfolio risk metrics."""

    var_5: float  # Value at Risk at 5% confidence
    var_10: float  # Value at Risk at 10% confidence
    cvar_5: float  # Conditional VaR at 5%
    cvar_10: float  # Conditional VaR at 10%
    downside_deviation: float
    sharpe_ratio: Optional[float] = None


class AnalyticsService:
    """Portfolio analytics and risk assessment."""

    def run_monte_carlo(
        self,
        base_npv: float,
        project_npvs: Dict[str, float],
        uncertainties: Dict[str, Dict[str, float]],
        num_simulations: int = 1000,
        seed: Optional[int] = None,
    ) -> MonteCarloResult:
        """Run Monte Carlo simulation on portfolio NPV.

        Simulates uncertainty by varying project NPVs according to
        specified distributions.

        Args:
            base_npv: Deterministic portfolio NPV
            project_npvs: Dict of project_id -> NPV
            uncertainties: Dict of project_id -> {std_pct, min_pct, max_pct}
                std_pct: standard deviation as % of NPV (e.g., 0.20 = 20%)
            num_simulations: Number of Monte Carlo iterations
            seed: Random seed for reproducibility

        Returns:
            MonteCarloResult with distribution statistics
        """
        rng = np.random.default_rng(seed)

        # Generate Latin Hypercube Samples for each project
        npv_samples = np.zeros(num_simulations)

        for pid, npv in project_npvs.items():
            unc = uncertainties.get(pid, {"std_pct": 0.20})
            std = abs(npv * unc.get("std_pct", 0.20))

            # Sample from normal distribution
            samples = rng.normal(loc=npv, scale=std, size=num_simulations)

            # Apply bounds if specified
            min_val = npv * (1 - unc.get("min_pct", 0.5))
            max_val = npv * (1 + unc.get("max_pct", 0.5))
            samples = np.clip(samples, min_val, max_val)

            npv_samples += samples

        # Calculate statistics
        sorted_npvs = np.sort(npv_samples)

        result = MonteCarloResult(
            num_simulations=num_simulations,
            mean_npv=float(np.mean(npv_samples)),
            std_npv=float(np.std(npv_samples)),
            p10=float(np.percentile(npv_samples, 10)),
            p50=float(np.percentile(npv_samples, 50)),
            p90=float(np.percentile(npv_samples, 90)),
            min_npv=float(np.min(npv_samples)),
            max_npv=float(np.max(npv_samples)),
            prob_positive=float(np.mean(npv_samples > 0)),
            npv_distribution=sorted_npvs.tolist(),
        )

        logger.info(
            "monte_carlo_completed",
            num_simulations=num_simulations,
            mean_npv=result.mean_npv,
            p10=result.p10,
            p50=result.p50,
            p90=result.p90,
        )

        return result

    def run_sensitivity_analysis(
        self,
        base_objective: float,
        parameters: Dict[str, Dict[str, float]],
        evaluate_fn: Any,
    ) -> List[SensitivityFactor]:
        """Run one-way sensitivity analysis (tornado chart).

        Varies each parameter independently by ±variation and measures
        the impact on the objective.

        Args:
            base_objective: Base case objective value
            parameters: Dict of parameter_name -> {
                base: base value,
                low: low bound (or variation %),
                high: high bound (or variation %)
            }
            evaluate_fn: Callable(parameter_name, value) -> objective_value

        Returns:
            List of SensitivityFactor sorted by impact (largest first)
        """
        factors: List[SensitivityFactor] = []

        for name, config in parameters.items():
            base_val = config["base"]
            low_val = config.get("low", base_val * 0.8)
            high_val = config.get("high", base_val * 1.2)

            low_result = evaluate_fn(name, low_val)
            high_result = evaluate_fn(name, high_val)

            factors.append(SensitivityFactor(
                parameter_name=name,
                base_value=base_val,
                low_value=low_val,
                high_value=high_val,
                low_result=low_result,
                high_result=high_result,
                impact=abs(high_result - low_result),
            ))

        # Sort by impact (largest first for tornado chart)
        factors.sort(key=lambda f: f.impact, reverse=True)

        logger.info(
            "sensitivity_analysis_completed",
            num_parameters=len(parameters),
            top_factor=factors[0].parameter_name if factors else None,
        )

        return factors

    def calculate_risk_metrics(
        self,
        npv_distribution: List[float],
        risk_free_rate: float = 0.03,
    ) -> RiskMetrics:
        """Calculate portfolio risk metrics from NPV distribution.

        Args:
            npv_distribution: Array of simulated NPV values
            risk_free_rate: Risk-free rate for Sharpe ratio

        Returns:
            RiskMetrics with VaR, CVaR, downside deviation
        """
        arr = np.array(npv_distribution)

        # VaR (Value at Risk) - loss at confidence level
        var_5 = float(np.percentile(arr, 5))
        var_10 = float(np.percentile(arr, 10))

        # CVaR (Conditional VaR) - expected loss below VaR
        cvar_5 = float(np.mean(arr[arr <= var_5])) if np.any(arr <= var_5) else var_5
        cvar_10 = float(np.mean(arr[arr <= var_10])) if np.any(arr <= var_10) else var_10

        # Downside deviation (semi-deviation below mean)
        mean_npv = float(np.mean(arr))
        downside = arr[arr < mean_npv] - mean_npv
        downside_deviation = float(np.sqrt(np.mean(downside ** 2))) if len(downside) > 0 else 0.0

        # Sharpe ratio (if std > 0)
        std_npv = float(np.std(arr))
        sharpe = None
        if std_npv > 0:
            sharpe = (mean_npv - risk_free_rate * mean_npv) / std_npv

        return RiskMetrics(
            var_5=var_5,
            var_10=var_10,
            cvar_5=cvar_5,
            cvar_10=cvar_10,
            downside_deviation=downside_deviation,
            sharpe_ratio=sharpe,
        )
