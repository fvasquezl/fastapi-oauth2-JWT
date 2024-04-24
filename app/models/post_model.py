from datetime import datetime
from sqlite3 import IntegrityError

from fastapi import HTTPException
from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import Optional
from slugify import slugify
from sqlalchemy.orm import Session
from app.db.core import DBTag, DBPost, NotFoundError, session_local
from app.models.category_model import Category
from app.models.tag_model import Tag, TagCreate, create_db_tag


class PostBase(BaseModel):
    name: str
    description: str


class PostCreate(PostBase):
    model_config = ConfigDict(str_to_lower=True)

    tag_names: list[str] = Field(..., min_items=1, exclude=True)

    @field_validator("name")
    def title_must_be_unique(cls, v, values):
        db = session_local()
        post_with_same_name = db.query(DBPost).filter(DBPost.name == v).first()
        if post_with_same_name:
            raise ValueError("Name must be unique")
        return v


class PostUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class Post(PostBase):
    id: int
    slug: str
    category_id: int
    author_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    tags: list[Tag] = []

    class Config:
        from_attributes = True


def read_db_post(post_id: int, session: Session) -> DBPost:
    db_post = session.query(DBPost).filter(DBPost.id == post_id).first()
    if db_post is None:
        raise NotFoundError(f"Post with id {post_id} not found.")
    return db_post


def create_db_post(
    current_user,
    post: PostCreate,
    category: Category,
    db: Session,
) -> DBPost:
    existing_tags = db.query(DBTag).filter(DBTag.name.in_(post.tag_names)).all()
    tag_names_exist = [tag.name for tag in existing_tags]
    new_tag_names = set(post.tag_names) - set(tag_names_exist)
    new_tags = [create_db_tag(TagCreate(name=name), db) for name in new_tag_names]
    all_tags = existing_tags + new_tags
    post_data = post.model_dump()
    db_post = DBPost(
        **post_data,
        tags=all_tags,
        slug=slugify(post.name),
        author=current_user,
        category=category,
    )
    try:
        db.add(db_post)
        db.commit()
        db.refresh(db_post)
    except IntegrityError as e:
        db.rollback()
        # Manejar error de integridad, por ejemplo, una clave duplicada
        raise HTTPException(
            status_code=400, detail="Error de integridad: {}".format(str(e))
        )
    except Exception as e:
        # Manejar otros errores generales
        db.rollback()
        raise HTTPException(status_code=500, detail="Error al crear el post")

    return db_post


def update_db_post(post_id: int, post: PostUpdate, session: Session) -> DBPost:
    db_post = read_db_post(post_id, session)
    for key, value in post.model_dump(exclude_none=True).items():
        setattr(db_post, key, value)
    session.commit()
    session.refresh(db_post)
    return db_post


def delete_db_post(post_id: int, session: Session) -> DBPost:
    db_post = read_db_post(post_id, session)
    session.delete(db_post)
    session.commit()
