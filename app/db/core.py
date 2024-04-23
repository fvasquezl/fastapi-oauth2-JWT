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


class Base(DeclarativeBase):
    pass


class NotFoundError(Exception):
    pass


class TimeStampedModel(Base):
    __abstract__ = True
    created_at = mapped_column(DateTime(timezone=True), default=datetime.now())
    updated_at = mapped_column(DateTime(timezone=True), onupdate=datetime.now())


"""
 Class DBUser - Table "users"
 Representa a un usuario del sistema con información básica y relaciones con roles y publicaciones.
"""


class DBUser(TimeStampedModel):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    username: Mapped[str] = mapped_column(nullable=False)
    full_name: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(nullable=False, unique=True)
    hashed_password: Mapped[str] = mapped_column(nullable=False)
    is_disabled: Mapped[bool] = mapped_column(unique=False, default=False)

    """
    Relación muchos a muchos con la tabla DBRole a través de la tabla de 
    asociación DBUserRole. Un usuario puede tener varios roles y un rol puede ser 
    asignado a varios usuarios.
    """
    roles: Mapped[list["DBRole"]] = relationship(
        secondary="users_roles", back_populates="users", passive_deletes=True
    )

    """
    Relación uno a muchos con la tabla DBPost. Un usuario puede crear muchas 
    publicaciones, pero una publicación solo puede pertenecer a un usuario.
    """
    created_posts: Mapped[List["DBPost"]] = relationship(  # Nombre más descriptivo
        back_populates="author", passive_deletes=True  # Relación con 'author'
    )


"""
Class DBUserRole - Tabla de asociación "user_roles"
Representa la relación muchos a muchos entre usuarios y roles.
"""


class DBUserRole(Base):
    __tablename__ = "users_roles"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    role_id: Mapped[int] = mapped_column(
        ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True
    )


"""
Class DBRole - Table "roles"
Representa un rol dentro del sistema con un nombre y un slug único.
"""


class DBRole(TimeStampedModel):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    slug: Mapped[str] = mapped_column(String(80), nullable=False, unique=True)

    """
    Relación muchos a muchos con la tabla DBUser a través de la tabla de 
    asociación DBUserRole. Un rol puede ser asignado a varios usuarios y un 
    usuario puede tener varios roles.
    """
    users: Mapped[List["DBUser"]] = relationship(
        secondary="users_roles", back_populates="roles", passive_deletes=True
    )


"""
Class DBCategory - Table "categories"
Representa una categoría para clasificar las publicaciones.
"""


class DBCategory(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    slug: Mapped[str] = mapped_column(String(80), nullable=False, unique=True)

    """
    Relación uno a muchos con la tabla DBPost. Una categoría puede tener 
    muchas publicaciones, pero una publicación solo puede pertenecer a una 
    categoría.
    """
    posts: Mapped[List["DBPost"]] = relationship(back_populates="category")


"""
Class DBPost - Table "posts"
Representa una publicación con información como nombre, slug, descripción, 
autor, categoría y etiquetas.
"""


class DBPost(TimeStampedModel):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    slug: Mapped[str] = mapped_column(String(80), nullable=False, unique=True)
    description: Mapped[str]

    """
    Relación muchos a uno con la tabla DBUser. Una publicación pertenece a un solo usuario (autor).
    """
    author_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    author: Mapped["DBUser"] = relationship(back_populates="created_posts")

    """
    Relación muchos a uno con la tabla DBCategory. Una publicación pertenece a una sola categoría.
    """
    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id", ondelete="CASCADE"), nullable=False
    )
    category: Mapped["DBCategory"] = relationship(back_populates="posts")

    """
    Relación muchos a muchos con la tabla DBTag a través de la tabla de 
    asociación DBPostTag. Una publicación puede tener varias etiquetas y una 
    etiqueta puede ser asignada a varias publicaciones. 
    """
    tags: Mapped[List["DBTag"]] = relationship(
        secondary="posts_tags", back_populates="posts", passive_deletes=True
    )


"""
Class DBPostTag - Tabla de asociación "post_tags"
Representa la relación muchos a muchos entre publicaciones y etiquetas.
"""


class DBPostTag(Base):
    __tablename__ = "posts_tags"

    post_id: Mapped[int] = mapped_column(
        ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True
    )
    tag_id: Mapped[int] = mapped_column(
        ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True
    )


"""
Class DBTag - Table "tags"
Representa una etiqueta que se puede asignar a una publicación.
"""


class DBTag(TimeStampedModel):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    slug: Mapped[str] = mapped_column(String(80), nullable=False, unique=True)

    """
    Relación muchos a muchos con la tabla DBPost a través de la tabla de 
    asociación DBPostTag. Una etiqueta puede ser asignada a varias 
    publicaciones y una publicación puede tener varias etiquetas.
    """
    posts: Mapped[List["DBPost"]] = relationship(
        secondary="posts_tags", back_populates="tags", passive_deletes=True
    )


engine = create_engine(DATABASE_URL)
session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)


def get_db():
    database = session_local()
    try:
        yield database
    finally:
        database.close()
