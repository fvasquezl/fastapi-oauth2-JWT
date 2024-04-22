from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.db.core import NotFoundError, get_db
from app.models.category_model import (
    Category,
    CategoryCreate,
    CategoryUpdate,
    read_db_category,
    create_db_category,
    update_db_category,
    delete_db_category,
    # read_db_posts_for_category,
)

from app.models.post_model import Post


router = APIRouter(
    prefix="/categories",
)


# Rutas para usuarios


@router.post("/")
def create_category(
    request: Request, category: CategoryCreate, db: Session = Depends(get_db)
) -> Category:
    db_category = create_db_category(category, db)
    return Category(**db_category.__dict__)


@router.get("/{category_id}", response_model=Category)
def read_category(
    request: Request, category_id: int, db: Session = Depends(get_db)
) -> Category:
    try:
        db_category = read_db_category(category_id, db)
    except NotFoundError as e:
        raise HTTPException(status_code=400) from e
    return Category(**db_category.__dict__)


# @router.get("/{item_id}/posts")
# def read_item_automations(
#     request: Request, item_id: int, db: Session = Depends(get_db)
# ) -> list[Post]:
#     try:
#         automations = read_db_posts_for_category(item_id, db)
#     except NotFoundError as e:
#         raise HTTPException(status_code=404) from e
#     return [Post(**automation.__dict__) for automation in automations]


@router.put("/{category_id}")
def update_category(
    request: Request,
    category_id: int,
    category: CategoryUpdate,
    db: Session = Depends(get_db),
) -> Category:
    try:
        db_category = update_db_category(category_id, category, db)
    except NotFoundError as e:
        raise HTTPException(status_code=404) from e
    return Category(**db_category.__dict__)


@router.delete("/{category_id}")
def delete_category(
    request: Request, category_id: int, db: Session = Depends(get_db)
) -> Category:
    try:
        db_category = delete_db_category(category_id, db)
    except NotFoundError as e:
        raise HTTPException(status_code=404) from e
    return Category(**db_category.__dict__)


# from fastapi import APIRouter, Depends, HTTPException, Request
# from sqlalchemy.orm import Session
# from app.db.category import CategoryDB
# from app.db.category import Category, CategoryCreate

# from typing import List

# category_router = APIRouter()


# def get_db(request: Request):
#     return request.state.db


# # Rutas para las etiquetas
# @category_router.post("/category/", response_model=Category)
# def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
#     db_category = CategoryDB(**category.model_dump())
#     db.add(db_category)
#     db.commit()
#     db.refresh(db_category)
#     return db_category


# @category_router.get("/category/{category_id}", response_model=Category)
# def read_category(category_id: int, db: Session = Depends(get_db)):
#     category = db.query(CategoryDB).filter(CategoryDB.id == category_id).first()
#     if category is None:
#         raise HTTPException(status_code=404, detail="Category not found")
#     return category
