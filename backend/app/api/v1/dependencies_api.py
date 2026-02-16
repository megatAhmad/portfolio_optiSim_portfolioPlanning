"""
Project Dependencies API Routes

Manages interdependencies between projects (prerequisites, mutual exclusivity,
synergies, shared infrastructure, resource constraints).
"""

from typing import Dict, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.models.base import get_async_session
from app.models.dependency import SelectionDependency, SelectionGroup, GroupMember
from app.schemas.project import DependencyCreate, DependencyRead, SelectionGroupCreate, SelectionGroupRead

logger = structlog.get_logger(__name__)
router = APIRouter()


# ---------------------------------------------------------------------------
# Selection Dependencies
# ---------------------------------------------------------------------------


@router.post("/", response_model=DependencyRead, status_code=status.HTTP_201_CREATED)
async def create_dependency(
    dependency: DependencyCreate,
    session: AsyncSession = Depends(get_async_session),
) -> SelectionDependency:
    """
    Create a new project dependency.

    Types:
    - PREREQUISITE: Parent must be selected before child
    - MUTEX: Projects cannot both be selected (mutual exclusivity)
    - SYNERGY: Combined selection provides additional value
    - SHARED_INFRASTRUCTURE: Projects share limited physical capacity
    - RESOURCE_CONSTRAINT: Projects compete for limited resources
    """
    db_dependency = SelectionDependency(**dependency.model_dump())
    session.add(db_dependency)
    await session.commit()
    await session.refresh(db_dependency)

    logger.info(
        "dependency_created",
        dependency_id=str(db_dependency.id),
        type=db_dependency.dependency_type,
        parent_id=str(db_dependency.parent_opportunity_id),
        child_id=str(db_dependency.child_opportunity_id),
    )

    return db_dependency


@router.get("/", response_model=List[DependencyRead])
async def list_dependencies(
    opportunity_id: UUID = Query(None, description="Filter by opportunity (as parent or child)"),
    dependency_type: str = Query(None, description="Filter by type"),
    session: AsyncSession = Depends(get_async_session),
) -> List[SelectionDependency]:
    """
    List all dependencies with optional filtering.
    """
    stmt = select(SelectionDependency)

    if opportunity_id:
        stmt = stmt.where(
            (SelectionDependency.parent_opportunity_id == opportunity_id) |
            (SelectionDependency.child_opportunity_id == opportunity_id)
        )

    if dependency_type:
        stmt = stmt.where(SelectionDependency.dependency_type == dependency_type)

    result = await session.execute(stmt)
    dependencies = result.scalars().all()

    return list(dependencies)


@router.delete("/{dependency_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_dependency(
    dependency_id: UUID,
    session: AsyncSession = Depends(get_async_session),
) -> None:
    """
    Delete a project dependency.
    """
    stmt = select(SelectionDependency).where(SelectionDependency.id == dependency_id)
    result = await session.execute(stmt)
    db_dependency = result.scalar_one_or_none()

    if not db_dependency:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dependency {dependency_id} not found",
        )

    await session.delete(db_dependency)
    await session.commit()

    logger.info("dependency_deleted", dependency_id=str(dependency_id))


# ---------------------------------------------------------------------------
# Selection Groups
# ---------------------------------------------------------------------------


@router.post("/groups", response_model=SelectionGroupRead, status_code=status.HTTP_201_CREATED)
async def create_selection_group(
    group: SelectionGroupCreate,
    session: AsyncSession = Depends(get_async_session),
) -> SelectionGroup:
    """
    Create a new selection group.

    Types:
    - EXCLUSIVE: At most 1 project can be selected
    - INCLUSIVE: All or nothing
    - AT_LEAST_N: At least N projects must be selected
    - AT_MOST_N: At most N projects can be selected
    - EXACTLY_N: Exactly N projects must be selected
    """
    db_group = SelectionGroup(**group.model_dump(exclude={"member_opportunity_ids"}))
    session.add(db_group)
    await session.flush()

    # Add members
    for opp_id in group.member_opportunity_ids:
        member = GroupMember(
            group_id=db_group.id,
            opportunity_id=opp_id,
        )
        session.add(member)

    await session.commit()
    await session.refresh(db_group)

    logger.info(
        "selection_group_created",
        group_id=str(db_group.id),
        name=db_group.name,
        type=db_group.group_type,
        num_members=len(group.member_opportunity_ids),
    )

    return db_group


@router.get("/groups", response_model=List[SelectionGroupRead])
async def list_selection_groups(
    session: AsyncSession = Depends(get_async_session),
) -> List[SelectionGroup]:
    """
    List all selection groups.
    """
    stmt = select(SelectionGroup)
    result = await session.execute(stmt)
    groups = result.scalars().all()

    return list(groups)


@router.delete("/groups/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_selection_group(
    group_id: UUID,
    session: AsyncSession = Depends(get_async_session),
) -> None:
    """
    Delete a selection group and all memberships.
    """
    stmt = select(SelectionGroup).where(SelectionGroup.id == group_id)
    result = await session.execute(stmt)
    db_group = result.scalar_one_or_none()

    if not db_group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Selection group {group_id} not found",
        )

    await session.delete(db_group)
    await session.commit()

    logger.info("selection_group_deleted", group_id=str(group_id))


@router.get("/graph")
async def get_dependency_graph(
    session: AsyncSession = Depends(get_async_session),
) -> Dict:
    """
    Get the full dependency graph for visualization.

    Returns nodes (projects) and edges (dependencies) in a format
    suitable for D3.js force-directed layout or React Flow.
    """
    # TODO: Build NetworkX graph and convert to JSON
    return {
        "nodes": [],
        "edges": [],
        "message": "Dependency graph visualization not yet implemented",
    }
