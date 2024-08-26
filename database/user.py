from datetime import datetime, timedelta
from typing import Dict

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import count, func

from database.models import User
from loader import engine


async def create_user(telegram_id: int, username: str, first_name: str):
    async with AsyncSession(engine) as session:
        user = User(telegram_id=telegram_id, username=username, first_name=first_name)
        session.add(user)
        await session.commit()
        user = (await session.execute(select(User).where(User.telegram_id == telegram_id))).scalar_one()
        return user


async def get_user(telegram_id: int):
    async with AsyncSession(engine) as session:
        user: User = (await session.execute(select(User).where(User.telegram_id == telegram_id))).scalar_one_or_none()
        return user


async def set_love_card(telegram_id: int, love_card_id: int):
    async with AsyncSession(engine) as session:
        user: User = (await session.execute(select(User).where(User.telegram_id == telegram_id))).scalar_one_or_none()
        if user is None:
            return False
        user.love_card = love_card_id
        await session.commit()
        return True


async def update_last_get(telegram_id: int):
    async with AsyncSession(engine) as session:
        user: User = (await session.execute(select(User).where(User.telegram_id == telegram_id))).scalar_one_or_none()
        user.last_usage = datetime.now()
        await session.commit()


async def add_points(telegram_id: int, points: int):
    async with AsyncSession(engine) as session:
        user: User = (await session.execute(select(User).where(User.telegram_id == telegram_id))).scalar_one_or_none()
        user.points += points
        user.all_points += points
        await session.commit()


async def add_card(telegram_id: int, card_id: int):
    async with AsyncSession(engine) as session:
        user: User = (await session.execute(select(User).where(User.telegram_id == telegram_id))).scalar_one_or_none()
        user.cards += [card_id]
        user.card_count += 1
        await session.commit()


async def change_username(telegram_id: int, username: str):
    async with AsyncSession(engine) as session:
        user = (await session.execute(select(User).where(User.telegram_id == telegram_id))).scalar_one_or_none()
        user.username = username
        await session.commit()


async def check_premium(premium_expire: datetime):
    return True if premium_expire is not None and premium_expire > datetime.now() else False


async def get_top_users_by_cards():
    async with AsyncSession(engine) as session:
        top_users = (
            await session.execute(
                select(User)
                .order_by(desc(func.array_length(User.cards, 1)), desc(User.telegram_id))
                .limit(10)
            )
        ).scalars().all()
        top = []
        i = 1
        for top_user in top_users:
            icon = "💎" if await check_premium(top_user.premium_expire) else ""
            top += [[i, icon, top_user.username, len(top_user.cards)]]
            i += 1
        return top



async def get_top_users_by_points():
    async with (AsyncSession(engine) as session):
        top_users = (
            await session.execute(
                select(User).order_by(desc(User.points)).limit(10)
            )
        ).scalars().all()
        top = []
        i = 1
        for top_user in top_users:
            icon = "💎" if await check_premium(top_user.premium_expire) else ""
            top += [[i, icon, top_user.username, top_user.points]]
            i += 1
        return top


async def get_top_users_by_all_points():
    async with (AsyncSession(engine) as session):
        top_users = (
            await session.execute(
                select(User).order_by(desc(User.all_points)).limit(10)
            )
        ).scalars().all()
        top = []
        i = 1
        for top_user in top_users:
            icon = "💎" if await check_premium(top_user.premium_expire) else ""
            top += [[i, icon, top_user.username, top_user.all_points]]
            i += 1
        return top


async def get_me_on_top(by, telegram_id: int):
    async with AsyncSession(engine) as session:
        position = (await session.execute(
            select(1 + count("*")).where(by > select(by).where(User.telegram_id == telegram_id).scalar_subquery())
        )).scalar_one()
        return position


async def premium_from_datetime(telegram_id: int, end_date: datetime):
    async with AsyncSession(engine) as session:
        user: User = (await session.execute(select(User).where(User.telegram_id == telegram_id))).scalar_one_or_none()
        user.premium_expire = end_date
        await session.commit()


async def add_premium(telegram_id: int, days: timedelta):
    async with AsyncSession(engine) as session:
        user: User = (await session.execute(select(User).where(User.telegram_id == telegram_id))).scalar_one_or_none()
        user.premium_expire = datetime.now() + days
        await session.commit()


async def clear_season():
    async with AsyncSession(engine) as session:
        users: [User] = (await session.execute(select(User))).scalars().all()
        for user in users:
            user.cards = []
            user.points = 0
            user.last_usage = None
        await session.commit()
        return


async def ban_user(telegram_id: int):
    async with AsyncSession(engine) as session:
        user: User = (await session.execute(select(User).where(User.telegram_id == telegram_id))).scalar_one_or_none()
        user.is_banned = True
        await session.commit()
        return


async def unban_user(telegram_id: int):
    async with AsyncSession(engine) as session:
        user: User = (await session.execute(select(User).where(User.telegram_id == telegram_id))).scalar_one_or_none()
        user.is_banned = False
        await session.commit()
        return


async def get_all_users() -> [User]:
    async with AsyncSession(engine) as session:
        users: Dict[User] = (await session.execute(select(User))).scalars().all()
        return users