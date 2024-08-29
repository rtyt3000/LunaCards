import datetime

from sqlalchemy import ARRAY, BigInteger, DateTime, Integer, VARCHAR, Boolean
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    nickname: Mapped[str] = mapped_column(VARCHAR(64), default="Гость", unique=False)
    cards: Mapped[[int]] = mapped_column(MutableList.as_mutable(ARRAY(Integer)), default=[])
    points: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    all_points: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_usage: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=True)
    love_card: Mapped[int] = mapped_column(Integer, nullable=True)
    card_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    premium_expire: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=True)
    is_banned: Mapped[bool] = mapped_column(Boolean, default=False)


class Group(Base):
    __tablename__ = 'groups'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    group_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    title: Mapped[str] = mapped_column(VARCHAR(100), nullable=False)


class Card(Base):
    __tablename__ = 'cards'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(VARCHAR(80), nullable=False)
    photo: Mapped[str] = mapped_column(VARCHAR(160), nullable=False)
    points: Mapped[int] = mapped_column(Integer, nullable=False)
    rarity: Mapped[str] = mapped_column(VARCHAR(80), nullable=False)
