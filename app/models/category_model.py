from typing import Optional
from fastapi import Depends, HTTPException
from pydantic import BaseModel, field_validator
from slugify import slugify
from app.db.core import DBCategory, DBPost, NotFoundError, get_db, session_local
from sqlalchemy.orm import Session
import re


class CategoryBase(BaseModel):
    name: str


class CategoryCreate(CategoryBase):
    @field_validator("name")
    def name_must_be_unique(cls, v, values):
        db = session_local()
        post_with_same_name = db.query(DBCategory).filter(DBCategory.name == v).first()
        if post_with_same_name:
            raise ValueError("Name must be unique")
        return v


class CategoryUpdate(CategoryBase):
    name: Optional[str] = None


class Category(CategoryBase):
    id: int
    slug: str

    class Config:
        from_attributes = True


def get_category_from_id(category_id: int, db: Session = Depends(get_db)) -> DBCategory:
    category = db.query(DBCategory).filter(DBCategory.id == category_id).first()
    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category does not exist",
            headers={"X-Error": "Category does not exist"},
        )
    return category


def is_valid_category(db: Session, category_id: int) -> bool:
    category = db.query(DBCategory).filter(DBCategory.id == category_id).first()
    return category is not None


def read_db_category(category_id: int, session: Session) -> DBCategory:
    db_category = session.query(DBCategory).filter(DBCategory.id == category_id).first()
    if not db_category:
        raise NotFoundError(f"category with id {category_id} not found.")
    return db_category


def read_db_posts_for_category(category_id: int, session: Session) -> list[DBPost]:
    return session.query(DBPost).filter(DBPost.category_id == category_id).all()


def create_db_category(category: CategoryCreate, session: Session) -> DBCategory:
    try:
        slug = slugify(category.name)
        db_category = DBCategory(**category.model_dump(exclude_none=True))
        db_category.slug = slug
        session.add(db_category)
        session.commit()
        session.refresh(db_category)
        return db_category
    except Exception as e:
        session.rollback()
        raise e


def update_db_category(
    category_id: int, category: CategoryUpdate, session: Session
) -> DBCategory:
    db_category = read_db_category(category_id, session)
    for key, value in category.model_dump(exclude_none=True).items():
        setattr(db_category, key, value)
    session.commit()
    session.refresh(db_category)

    # get the posts
    # posts = read_db_posts_for_category(db_category.id, session)
    # run_posts(posts)

    return db_category


def delete_db_category(category_id: int, session: Session) -> DBCategory:
    db_category = read_db_category(category_id, session)
    session.delete(db_category)
    session.commit()
    return db_category
