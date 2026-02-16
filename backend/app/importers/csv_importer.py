"""
CSV File Importer

Imports portfolio data from CSV files. Supports multiple CSV files
for different data types (opportunities, outcomes, metrics).

Simpler format than Excel but requires one CSV per data type.
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any, Dict, List, Optional

import structlog

from app.importers.validators import ImportValidator, ValidationResult

logger = structlog.get_logger(__name__)


class CSVImportResult:
    """Container for parsed CSV data."""

    def __init__(self) -> None:
        self.opportunities: List[Dict[str, Any]] = []
        self.outcomes: Dict[str, List[Dict[str, Any]]] = {}
        self.metrics: Dict[str, Dict[str, Dict[str, List[float]]]] = {}
        self.validation: Optional[ValidationResult] = None


class CSVImporter:
    """Import portfolio data from CSV files.

    Usage::

        importer = CSVImporter(planning_horizon=30)
        result = importer.import_opportunities("opportunities.csv")
        result = importer.import_outcomes("outcomes.csv")
        result = importer.import_metrics("metrics.csv")
    """

    def __init__(self, planning_horizon: int = 30) -> None:
        self.planning_horizon = planning_horizon
        self.validator = ImportValidator(planning_horizon)

    def import_opportunities(self, file_path: str | Path) -> List[Dict[str, Any]]:
        """Import opportunities from a CSV file.

        Expected columns: name, type, business_unit, country, [optional fields]
        """
        file_path = Path(file_path)
        opportunities: List[Dict[str, Any]] = []

        with open(file_path, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)

            for row in reader:
                opp: Dict[str, Any] = {}

                # Map CSV columns to opportunity fields
                name = row.get("name", row.get("opportunity_name", "")).strip()
                if not name:
                    continue

                opp["name"] = name
                opp["type"] = row.get("type", "").strip() or None
                opp["business_unit"] = row.get("business_unit", "").strip() or None
                opp["country"] = row.get("country", "").strip() or None

                # Optional numeric fields
                for field in ("location_lat", "location_lon"):
                    val = row.get(field, "").strip()
                    if val:
                        try:
                            opp[field] = float(val)
                        except ValueError:
                            pass

                opportunities.append(opp)

        logger.info("csv_opportunities_imported", count=len(opportunities))
        return opportunities

    def import_outcomes(self, file_path: str | Path) -> Dict[str, List[Dict[str, Any]]]:
        """Import outcomes from a CSV file.

        Expected columns: opportunity_name, outcome_name, weight
        """
        file_path = Path(file_path)
        outcomes: Dict[str, List[Dict[str, Any]]] = {}

        with open(file_path, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)

            for row in reader:
                opp_name = row.get("opportunity_name", row.get("opportunity", "")).strip()
                outcome_name = row.get("outcome_name", row.get("outcome", "")).strip()
                weight_str = row.get("weight", row.get("probability", "0")).strip()

                if not opp_name or not outcome_name:
                    continue

                try:
                    weight = float(weight_str)
                except ValueError:
                    weight = 0.0

                if opp_name not in outcomes:
                    outcomes[opp_name] = []

                outcomes[opp_name].append({
                    "name": outcome_name,
                    "weight": weight,
                })

        logger.info("csv_outcomes_imported", groups=len(outcomes))
        return outcomes

    def import_metrics(
        self,
        file_path: str | Path,
    ) -> Dict[str, Dict[str, Dict[str, List[float]]]]:
        """Import time-series metrics from a CSV file.

        Expected columns: opportunity_name, outcome_name, metric_name, year_0, year_1, ..., year_N

        Alternative format: opportunity_name, outcome_name, metric_name, year, value
        (long format — one row per year per metric)
        """
        file_path = Path(file_path)
        metrics: Dict[str, Dict[str, Dict[str, List[float]]]] = {}

        with open(file_path, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames or []

            # Detect format: wide (year_0, year_1, ...) or long (year, value)
            is_long_format = "year" in fieldnames and "value" in fieldnames

            if is_long_format:
                metrics = self._parse_long_format(reader)
            else:
                metrics = self._parse_wide_format(reader, fieldnames)

        logger.info("csv_metrics_imported", metric_types=len(metrics))
        return metrics

    def _parse_wide_format(
        self,
        reader: csv.DictReader,
        fieldnames: List[str],
    ) -> Dict[str, Dict[str, Dict[str, List[float]]]]:
        """Parse wide-format metrics (one row per metric, columns for years)."""
        metrics: Dict[str, Dict[str, Dict[str, List[float]]]] = {}

        # Identify year columns
        year_cols = [f for f in fieldnames if f.startswith("year_") or f.isdigit()]

        for row in reader:
            opp = row.get("opportunity_name", row.get("opportunity", "")).strip()
            out = row.get("outcome_name", row.get("outcome", "")).strip()
            mname = row.get("metric_name", row.get("metric", "")).strip()

            if not (opp and out and mname):
                continue

            values: List[float] = []
            for col in year_cols:
                try:
                    values.append(float(row.get(col, 0)))
                except (ValueError, TypeError):
                    values.append(0.0)

            if mname not in metrics:
                metrics[mname] = {}
            if opp not in metrics[mname]:
                metrics[mname][opp] = {}
            metrics[mname][opp][out] = values

        return metrics

    def _parse_long_format(
        self,
        reader: csv.DictReader,
    ) -> Dict[str, Dict[str, Dict[str, List[float]]]]:
        """Parse long-format metrics (one row per year)."""
        # Collect all entries first
        raw: Dict[str, Dict[str, Dict[str, Dict[int, float]]]] = {}

        for row in reader:
            opp = row.get("opportunity_name", row.get("opportunity", "")).strip()
            out = row.get("outcome_name", row.get("outcome", "")).strip()
            mname = row.get("metric_name", row.get("metric", "")).strip()

            if not (opp and out and mname):
                continue

            try:
                year = int(row["year"])
                value = float(row["value"])
            except (ValueError, TypeError, KeyError):
                continue

            if mname not in raw:
                raw[mname] = {}
            if opp not in raw[mname]:
                raw[mname][opp] = {}
            if out not in raw[mname][opp]:
                raw[mname][opp][out] = {}
            raw[mname][opp][out][year] = value

        # Convert to list format
        metrics: Dict[str, Dict[str, Dict[str, List[float]]]] = {}
        for mname, opp_data in raw.items():
            metrics[mname] = {}
            for opp, out_data in opp_data.items():
                metrics[mname][opp] = {}
                for out, year_vals in out_data.items():
                    max_year = max(year_vals.keys()) if year_vals else 0
                    values = [
                        year_vals.get(y, 0.0)
                        for y in range(max_year + 1)
                    ]
                    metrics[mname][opp][out] = values

        return metrics

    def import_all(
        self,
        opportunities_file: str | Path,
        outcomes_file: str | Path,
        metrics_file: str | Path,
        validate: bool = True,
    ) -> CSVImportResult:
        """Import all data from separate CSV files.

        Args:
            opportunities_file: Path to opportunities CSV
            outcomes_file: Path to outcomes CSV
            metrics_file: Path to metrics CSV
            validate: Run validation (default True)

        Returns:
            CSVImportResult with all parsed data
        """
        result = CSVImportResult()

        result.opportunities = self.import_opportunities(opportunities_file)
        result.outcomes = self.import_outcomes(outcomes_file)
        result.metrics = self.import_metrics(metrics_file)

        if validate:
            result.validation = self.validator.validate_full_import(
                result.opportunities, result.outcomes, result.metrics
            )

        return result
