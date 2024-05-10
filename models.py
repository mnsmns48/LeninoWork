from typing import Optional
from datetime import datetime
from sqlalchemy import DateTime, BIGINT
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped

from config import config


class Base(DeclarativeBase):
    __abstract__ = True


class LeninoWork(Base):
    __tablename__ = config.db_table
    id: Mapped[int] = mapped_column(BIGINT, primary_key=True, unique=True)
    title: Mapped[str]
    author: Mapped[Optional[str]]
    payment: Mapped[str]
    cond: Mapped[str]
    desc: Mapped[str]
    performance: Mapped[str]
    locality: Mapped[str]
    link: Mapped[str]
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=False))
    publication: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=False))
