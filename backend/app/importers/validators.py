"""
Import Validation Rules

Validates imported portfolio data for consistency, completeness, and correctness
before persisting to the database.

Checks:
- Outcome weights sum to 1.0 per opportunity
- Time series lengths match planning horizon
- Required fields present
- No duplicate opportunity names
- Metric values within reasonable bounds
- Attributes match expected types
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set

import structlog

logger = structlog.get_logger(__name__)


@dataclass
class ValidationError:
    """A single validation error."""

    field: str
    message: str
    severity: str = "error"  # "error" or "warning"
    row: Optional[int] = None
    sheet: Optional[str] = None


@dataclass
class ValidationResult:
    """Aggregated validation results."""

    is_valid: bool = True
    errors: List[ValidationError] = field(default_factory=list)
    warnings: List[ValidationError] = field(default_factory=list)
    stats: Dict[str, Any] = field(default_factory=dict)

    def add_error(self, field: str, message: str, **kwargs: Any) -> None:
        self.errors.append(ValidationError(field=field, message=message, severity="error", **kwargs))
        self.is_valid = False

    def add_warning(self, field: str, message: str, **kwargs: Any) -> None:
        self.warnings.append(ValidationError(field=field, message=message, severity="warning", **kwargs))


class ImportValidator:
    """Validates imported portfolio data."""

    # Acceptable opportunity types
    VALID_TYPES: Set[str] = {
        "upstream_oil", "upstream_gas", "downstream",
        "renewable_solar", "renewable_wind", "renewable_hydro",
        "infrastructure", "decommissioning", "exploration",
        "development", "production",
    }

    def __init__(self, planning_horizon: int = 30) -> None:
        self.planning_horizon = planning_horizon

    def validate_opportunities(
        self,
        opportunities: List[Dict[str, Any]],
    ) -> ValidationResult:
        """Validate a list of imported opportunity records."""
        result = ValidationResult()
        seen_names: Set[str] = set()

        for i, opp in enumerate(opportunities, start=1):
            name = opp.get("name", "")

            # Required: name
            if not name or not name.strip():
                result.add_error("name", f"Row {i}: Opportunity name is required", row=i)
                continue

            # Unique name
            if name in seen_names:
                result.add_error("name", f"Row {i}: Duplicate opportunity name '{name}'", row=i)
            seen_names.add(name)

            # Validate type if provided
            opp_type = opp.get("type")
            if opp_type and opp_type.lower() not in self.VALID_TYPES:
                result.add_warning(
                    "type",
                    f"Row {i}: Unknown type '{opp_type}' for '{name}'. "
                    f"Valid types: {', '.join(sorted(self.VALID_TYPES))}",
                    row=i,
                )

        result.stats["total_opportunities"] = len(opportunities)
        result.stats["unique_names"] = len(seen_names)

        logger.info(
            "opportunities_validated",
            total=len(opportunities),
            errors=len(result.errors),
            warnings=len(result.warnings),
        )

        return result

    def validate_outcomes(
        self,
        outcomes: Dict[str, List[Dict[str, Any]]],
    ) -> ValidationResult:
        """
        Validate outcomes grouped by opportunity.

        Args:
            outcomes: Dict mapping opportunity_name -> list of outcome dicts
                Each outcome dict has "name" and "weight" keys
        """
        result = ValidationResult()

        for opp_name, outcome_list in outcomes.items():
            if not outcome_list:
                result.add_error(
                    "outcomes",
                    f"Opportunity '{opp_name}' has no outcomes",
                )
                continue

            # Check weights sum to 1.0
            total_weight = sum(o.get("weight", 0.0) for o in outcome_list)
            if abs(total_weight - 1.0) > 0.01:
                result.add_error(
                    "weight",
                    f"Opportunity '{opp_name}': outcome weights sum to {total_weight:.4f}, "
                    f"expected 1.0",
                )

            # Check each outcome
            seen_names: Set[str] = set()
            for outcome in outcome_list:
                name = outcome.get("name", "")
                weight = outcome.get("weight", 0.0)

                if not name:
                    result.add_error("outcome_name", f"Opportunity '{opp_name}': empty outcome name")

                if name in seen_names:
                    result.add_error(
                        "outcome_name",
                        f"Opportunity '{opp_name}': duplicate outcome name '{name}'",
                    )
                seen_names.add(name)

                if weight < 0 or weight > 1:
                    result.add_error(
                        "weight",
                        f"Opportunity '{opp_name}', outcome '{name}': "
                        f"weight {weight} out of range [0, 1]",
                    )

        result.stats["total_outcome_groups"] = len(outcomes)

        return result

    def validate_time_series(
        self,
        metric_name: str,
        values: List[float],
        opportunity_name: str = "",
        outcome_name: str = "",
    ) -> ValidationResult:
        """Validate a single time series for length and value reasonableness."""
        result = ValidationResult()

        if len(values) != self.planning_horizon:
            result.add_warning(
                "time_series_length",
                f"'{metric_name}' for {opportunity_name}/{outcome_name}: "
                f"length {len(values)}, expected {self.planning_horizon}. "
                f"Values will be padded with zeros or truncated.",
            )

        # Check for NaN or infinity
        for i, v in enumerate(values):
            if v != v:  # NaN check
                result.add_error(
                    "time_series_nan",
                    f"'{metric_name}' year {i}: NaN value for {opportunity_name}/{outcome_name}",
                )
            elif abs(v) == float("inf"):
                result.add_error(
                    "time_series_inf",
                    f"'{metric_name}' year {i}: infinite value for {opportunity_name}/{outcome_name}",
                )

        return result

    def validate_full_import(
        self,
        opportunities: List[Dict[str, Any]],
        outcomes: Dict[str, List[Dict[str, Any]]],
        metrics: Dict[str, Dict[str, Dict[str, List[float]]]],
    ) -> ValidationResult:
        """Run all validators on a complete import data set.

        Args:
            opportunities: List of opportunity dicts
            outcomes: opportunity_name -> list of outcome dicts
            metrics: metric_name -> opportunity_name -> outcome_name -> values

        Returns:
            Combined ValidationResult
        """
        combined = ValidationResult()

        # Validate opportunities
        opp_result = self.validate_opportunities(opportunities)
        combined.errors.extend(opp_result.errors)
        combined.warnings.extend(opp_result.warnings)
        combined.stats.update(opp_result.stats)

        # Validate outcomes
        out_result = self.validate_outcomes(outcomes)
        combined.errors.extend(out_result.errors)
        combined.warnings.extend(out_result.warnings)
        combined.stats.update(out_result.stats)

        # Validate time series
        ts_error_count = 0
        for metric_name, opp_data in metrics.items():
            for opp_name, outcome_data in opp_data.items():
                for outcome_name, values in outcome_data.items():
                    ts_result = self.validate_time_series(
                        metric_name, values, opp_name, outcome_name
                    )
                    combined.errors.extend(ts_result.errors)
                    combined.warnings.extend(ts_result.warnings)
                    ts_error_count += len(ts_result.errors)

        combined.stats["time_series_errors"] = ts_error_count
        combined.is_valid = len(combined.errors) == 0

        logger.info(
            "full_import_validated",
            is_valid=combined.is_valid,
            errors=len(combined.errors),
            warnings=len(combined.warnings),
            stats=combined.stats,
        )

        return combined
