from typing import List
from sqlalchemy import (
    DateTime,
    ForeignKey,
    String,
    create_engine,
)
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from datetime import datetime


DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(DATABASE_URL)
session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)


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

    """relationship one to many to Posts"""
    posts: Mapped[List["DBPost"]] = relationship(
        back_populates="user", passive_deletes=True
    )


class DBCategory(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    slug: Mapped[str] = mapped_column(String(80), nullable=False, unique=True)

    """relationship one to many to Posts"""
    posts: Mapped[List["DBPost"]] = relationship(back_populates="category")


class DBPost(TimeStampedModel):
    __tablename__ = "post"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    slug: Mapped[str] = mapped_column(String(80), nullable=False, unique=True)
    description: Mapped[str]

    """Relationship Many to One To User"""
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    user: Mapped["DBUser"] = relationship(back_populates="posts")

    """Relationship Many to One To Category"""
    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id", ondelete="CASCADE"), nullable=False
    )
    category: Mapped["DBCategory"] = relationship(back_populates="posts")


Base.metadata.create_all(bind=engine)


def get_db():
    database = session_local()
    try:
        yield database
    finally:
        database.close()
