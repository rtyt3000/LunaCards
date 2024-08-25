from typing import Dict

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Group
from loader import engine


async def create_group(group_id: int, title: str) -> Group:
    """Creating group"""
    async with AsyncSession(engine) as session:
        group = Group(group_id=group_id, title=title)
        session.add(group)
        await session.commit()
        group = (await session.execute(select(Group).where(Group.group_id == group_id))).scalar_one()
        return group


async def get_group(group_id: int) -> Group:
    """Getting exists group or none"""
    async with AsyncSession(engine) as session:
        group = (await session.execute(select(Group).where(Group.group_id == group_id))).scalar_one_or_none()
        return group


async def get_all_groups() -> [Group]:
    async with AsyncSession(engine) as session:
        groups = (await session.execute(select(Group))).scalars().all()
        return groups
