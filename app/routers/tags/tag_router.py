from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.db.core import NotFoundError, get_db
from app.models.tag_model import (
    Tag,
    TagCreate,
    TagUpdate,
    read_db_tag,
    create_db_tag,
    update_db_tag,
    delete_db_tag,
    # read_db_posts_for_tag,
)

from app.models.post_model import Post


router = APIRouter(
    prefix="/tags",
)


# Rutas para usuarios


@router.post("/")
def create_tag(request: Request, tag: TagCreate, db: Session = Depends(get_db)) -> Tag:
    db_tag = create_db_tag(tag, db)
    return Tag(**db_tag.__dict__)


@router.get("/{tag_id}", response_model=Tag)
def read_tag(request: Request, tag_id: int, db: Session = Depends(get_db)) -> Tag:
    try:
        db_tag = read_db_tag(tag_id, db)
    except NotFoundError as e:
        raise HTTPException(status_code=400) from e
    return Tag(**db_tag.__dict__)


# @router.get("/{item_id}/posts")
# def read_item_automations(
#     request: Request, item_id: int, db: Session = Depends(get_db)
# ) -> list[Post]:
#     try:
#         automations = read_db_posts_for_tag(item_id, db)
#     except NotFoundError as e:
#         raise HTTPException(status_code=404) from e
#     return [Post(**automation.__dict__) for automation in automations]


@router.put("/{tag_id}")
def update_tag(
    request: Request,
    tag_id: int,
    tag: TagUpdate,
    db: Session = Depends(get_db),
) -> Tag:
    try:
        db_tag = update_db_tag(tag_id, tag, db)
    except NotFoundError as e:
        raise HTTPException(status_code=404) from e
    return Tag(**db_tag.__dict__)


@router.delete("/{tag_id}")
def delete_tag(request: Request, tag_id: int, db: Session = Depends(get_db)) -> Tag:
    try:
        db_tag = delete_db_tag(tag_id, db)
    except NotFoundError as e:
        raise HTTPException(status_code=404) from e
    return Tag(**db_tag.__dict__)


# from fastapi import APIRouter, Depends, HTTPException, Request
# from sqlalchemy.orm import Session
# from app.db.tag import TagDB
# from app.db.tag import Tag, TagCreate

# from typing import List

# tag_router = APIRouter()


# def get_db(request: Request):
#     return request.state.db


# # Rutas para las etiquetas
# @tag_router.post("/tag/", response_model=Tag)
# def create_tag(tag: TagCreate, db: Session = Depends(get_db)):
#     db_tag = TagDB(**tag.model_dump())
#     db.add(db_tag)
#     db.commit()
#     db.refresh(db_tag)
#     return db_tag


# @tag_router.get("/tag/{tag_id}", response_model=Tag)
# def read_tag(tag_id: int, db: Session = Depends(get_db)):
#     tag = db.query(TagDB).filter(TagDB.id == tag_id).first()
#     if tag is None:
#         raise HTTPException(status_code=404, detail="Tag not found")
#     return tag
