from typing import List
from sqlalchemy import (
    DateTime,
    create_engine,
)
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from datetime import datetime


DATABASE_URL = "sqlite:///./test.db"


class Base(DeclarativeBase):
    pass


class NotFoundError(Exception):
    pass


class TimeStampedModel(Base):
    __abstract__ = True
    created_at = mapped_column(DateTime(timezone=True), default=datetime.now())
    updated_at = mapped_column(DateTime(timezone=True), onupdate=datetime.now())


class DBUser(TimeStampedModel):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    username: Mapped[str] = mapped_column(nullable=False)
    full_name: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(nullable=False, unique=True)
    hashed_password: Mapped[str] = mapped_column(nullable=False)
    disabled: Mapped[bool] = mapped_column(unique=False, default=False)


engine = create_engine(DATABASE_URL)
session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def get_db():
    database = session_local()
    try:
        yield database
    finally:
        database.close()