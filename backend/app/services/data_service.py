"""
Data Service - Project import, validation, transformation, graph analysis

Business logic for managing portfolio data: importing from Excel/CSV,
validating data integrity, building dependency graphs, and preparing
project data for optimization.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Set
from uuid import UUID

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.graph.dependency_graph import DependencyGraphBuilder
from app.importers.csv_importer import CSVImporter, CSVImportResult
from app.importers.excel_importer import ExcelImporter, ExcelImportResult
from app.importers.validators import ImportValidator, ValidationResult
from app.models.dependency import SelectionDependency, SelectionGroup
from app.models.project import Opportunity, Outcome

logger = structlog.get_logger(__name__)


class DataService:
    """Service for managing portfolio data and project imports.

    Follows the repository pattern: database access through this service,
    not directly in route handlers.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    # ------------------------------------------------------------------
    # Import Operations
    # ------------------------------------------------------------------

    async def import_from_excel(
        self,
        file_path: str | Path,
        planning_horizon: int = 30,
    ) -> ExcelImportResult:
        """Import portfolio data from an Excel file.

        Parses the file, validates data, and persists to the database
        if validation passes.

        Args:
            file_path: Path to .xlsx file
            planning_horizon: Number of years in the planning horizon

        Returns:
            ExcelImportResult with parsed data and validation results
        """
        importer = ExcelImporter(planning_horizon)
        result = importer.import_file(file_path, validate=True)

        if result.validation and result.validation.is_valid:
            await self._persist_import(
                result.opportunities,
                result.outcomes,
                result.metrics,
                result.attributes,
            )
            logger.info(
                "excel_import_persisted",
                opportunities=len(result.opportunities),
            )
        else:
            logger.warning(
                "excel_import_validation_failed",
                errors=len(result.validation.errors) if result.validation else 0,
            )

        return result

    async def import_from_csv(
        self,
        opportunities_file: str | Path,
        outcomes_file: str | Path,
        metrics_file: str | Path,
        planning_horizon: int = 30,
    ) -> CSVImportResult:
        """Import portfolio data from CSV files.

        Args:
            opportunities_file: Path to opportunities CSV
            outcomes_file: Path to outcomes CSV
            metrics_file: Path to metrics CSV
            planning_horizon: Number of years

        Returns:
            CSVImportResult with parsed data and validation results
        """
        importer = CSVImporter(planning_horizon)
        result = importer.import_all(
            opportunities_file, outcomes_file, metrics_file, validate=True
        )

        if result.validation and result.validation.is_valid:
            await self._persist_import(
                result.opportunities,
                result.outcomes,
                result.metrics,
            )

        return result

    # ------------------------------------------------------------------
    # Query Operations
    # ------------------------------------------------------------------

    async def get_all_opportunities(self) -> List[Opportunity]:
        """Get all opportunities from the database."""
        stmt = select(Opportunity).order_by(Opportunity.name)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_opportunity_ids(self) -> Set[str]:
        """Get all opportunity IDs as a set of strings."""
        opportunities = await self.get_all_opportunities()
        return {str(opp.id) for opp in opportunities}

    async def get_dependencies(self) -> List[SelectionDependency]:
        """Get all active selection dependencies."""
        stmt = select(SelectionDependency).where(
            SelectionDependency.is_active == True  # noqa: E712
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_groups(self) -> List[SelectionGroup]:
        """Get all active selection groups."""
        stmt = select(SelectionGroup).where(
            SelectionGroup.is_active == True  # noqa: E712
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    # ------------------------------------------------------------------
    # Graph Operations
    # ------------------------------------------------------------------

    async def build_dependency_graph(self) -> DependencyGraphBuilder:
        """Build the NetworkX dependency graph from all active dependencies.

        Returns:
            DependencyGraphBuilder with the populated graph
        """
        dependencies = await self.get_dependencies()
        builder = DependencyGraphBuilder()

        for dep in dependencies:
            parent = str(dep.independent_opportunity_id)
            child = str(dep.dependent_opportunity_id)

            if dep.must_or_must_not == "Must":
                builder.add_prerequisite(
                    parent, child, time_offset=dep.time_offset
                )
            elif dep.must_or_must_not == "Must Not":
                builder.add_mutex(parent, child)

        logger.info(
            "dependency_graph_built",
            nodes=builder.graph.number_of_nodes(),
            edges=builder.graph.number_of_edges(),
        )

        return builder

    # ------------------------------------------------------------------
    # Internal: Persistence
    # ------------------------------------------------------------------

    async def _persist_import(
        self,
        opportunities: List[Dict[str, Any]],
        outcomes: Dict[str, List[Dict[str, Any]]],
        metrics: Dict[str, Dict[str, Dict[str, Any]]],
        attributes: Optional[Dict[str, Dict[str, Any]]] = None,
    ) -> None:
        """Persist imported data to the database."""
        opp_id_map: Dict[str, UUID] = {}

        # Create opportunities
        for opp_data in opportunities:
            db_opp = Opportunity(
                name=opp_data["name"],
                type=opp_data.get("type"),
                business_unit=opp_data.get("business_unit"),
                country=opp_data.get("country"),
            )
            self.session.add(db_opp)
            await self.session.flush()
            opp_id_map[opp_data["name"]] = db_opp.id

        # Create outcomes
        for opp_name, outcome_list in outcomes.items():
            opp_id = opp_id_map.get(opp_name)
            if not opp_id:
                continue

            for out_data in outcome_list:
                db_outcome = Outcome(
                    opportunity_id=opp_id,
                    name=out_data["name"],
                    weight=out_data["weight"],
                )
                self.session.add(db_outcome)

        await self.session.commit()

        logger.info(
            "import_data_persisted",
            opportunities=len(opportunities),
            outcome_groups=len(outcomes),
        )
