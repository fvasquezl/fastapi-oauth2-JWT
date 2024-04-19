from datetime import datetime

from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
from app.db.core import DBPost, NotFoundError
from app.categories.category_schema import read_db_category


class PostBase(BaseModel):
    name: str
    description: str


class PostCreate(PostBase):
    slug: str


class PostUpdate(BaseModel):
    name: Optional[int] = None
    description: Optional[str] = None


class Post(PostBase):
    id: int
    category_id: int
    user_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


def read_db_post(post_id: int, session: Session) -> DBPost:
    db_post = session.query(DBPost).filter(DBPost.id == post_id).first()
    if db_post is None:
        raise NotFoundError(f"Post with id {post_id} not found.")
    return db_post


def create_db_post(
    current_user, category_id: int, post: PostCreate, session: Session
) -> DBPost:
    category = read_db_category(category_id, session)
    # category_id = category.id
    db_post = DBPost(**post.model_dump())

    # for tag_id in tags:
    #     tag = read_db_tag(tag_id, session)
    #     db_post.tags.append(tag)
    db_post.user = current_user
    db_post.category = category
    session.add(db_post)
    session.commit()
    session.refresh(db_post)
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
