from typing import Optional
from fastapi import Depends, HTTPException
from pydantic import BaseModel, field_validator
from slugify import slugify
from app.db.core import DBTag, DBPost, NotFoundError, get_db, session_local
from sqlalchemy.orm import Session
import re


class TagBase(BaseModel):
    name: str


class TagCreate(TagBase):
    @field_validator("name")
    def name_must_be_unique(cls, v, values):
        db = session_local()
        post_with_same_name = db.query(DBTag).filter(DBTag.name == v).first()
        if post_with_same_name:
            raise ValueError("Name must be unique")
        return v


class TagUpdate(TagBase):
    name: Optional[str] = None


class Tag(TagBase):
    id: int
    slug: str

    class Config:
        from_attributes = True


def get_tag_from_id(tag_id: int, db: Session = Depends(get_db)) -> DBTag:
    tag = db.query(DBTag).filter(DBTag.id == tag_id).first()
    if not tag:
        raise HTTPException(
            status_code=404,
            detail="Tag does not exist",
            headers={"X-Error": "Tag does not exist"},
        )
    return tag


def is_valid_tag(db: Session, tag_id: int) -> bool:
    tag = db.query(DBTag).filter(DBTag.id == tag_id).first()
    return tag is not None


def read_db_tag(tag_id: int, db: Session) -> DBTag:
    db_tag = db.query(DBTag).filter(DBTag.id == tag_id).first()
    if db_tag is None:
        raise NotFoundError(f"tag with id {tag_id} not found.")
    return db_tag


def read_db_posts_for_tag(tag_id: int, session: Session) -> list[DBPost]:
    return session.query(DBPost).filter(DBPost.tag_id == tag_id).all()


def create_db_tag(tag: TagCreate, session: Session) -> DBTag:
    try:
        slug = slugify(tag.name)
        db_tag = DBTag(**tag.model_dump(exclude_none=True))
        db_tag.slug = slug
        session.add(db_tag)
        session.commit()
        session.refresh(db_tag)
        return db_tag
    except Exception as e:
        session.rollback()
        raise e


def update_db_tag(tag_id: int, tag: TagUpdate, session: Session) -> DBTag:
    db_tag = read_db_tag(tag_id, session)
    for key, value in tag.model_dump(exclude_none=True).items():
        setattr(db_tag, key, value)
    session.commit()
    session.refresh(db_tag)

    # get the posts
    # posts = read_db_posts_for_tag(db_tag.id, session)
    # run_posts(posts)

    return db_tag


def delete_db_tag(tag_id: int, session: Session) -> DBTag:
    db_tag = read_db_tag(tag_id, session)
    session.delete(db_tag)
    session.commit()
    return db_tag
