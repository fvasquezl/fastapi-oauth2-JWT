from fastapi import APIRouter, Body, Depends, HTTPException, Request
from fastapi.params import Depends
from sqlalchemy.orm import Session
from app.models.category_model import (
    Category,
    get_category_from_id,
    is_valid_category,
    read_db_category,
)
from app.db.core import DBCategory, get_db, NotFoundError
from app.models.post_model import (
    Post,
    PostCreate,
    PostUpdate,
    create_db_post,
    delete_db_post,
    read_db_post,
    update_db_post,
)


from typing import Annotated, List

from app.models.token_model import get_current_active_user
from app.models.user_model import User
from app.models.tag_model import Tag, get_tag_from_id


router = APIRouter(
    prefix="/posts",
)


# Rutas para las posts
@router.post("/")
def create_post(
    current_user: Annotated[User, Depends(get_current_active_user)],
    category: Annotated[Category, Depends(get_category_from_id)],
    post: PostCreate,
    db: Session = Depends(get_db),
) -> Post:
    db_post = create_db_post(current_user, post, category, db)
    return Post(**db_post.__dict__)


# @router.get("/{post_id}")
# def read_post(request: Request, post_id: int, db: Session = Depends(get_db)) -> Post:
#     try:
#         db_post = read_db_post(post_id, db)
#     except NotFoundError as e:
#         raise HTTPException(status_code=404) from e
#     return Post(**db_post.__dict__)


# @router.put("/{post_id}")
# def update_post(
#     post_id: int,
#     post: PostUpdate,
#     db: Session = Depends(get_db),
# ) -> Post:
#     try:
#         db_post = update_db_post(post_id, post, db)
#     except NotFoundError as e:
#         raise HTTPException(status_code=404) from e
#     return Post(**db_post.__dict__)


# @router.delete("/{post_id}")
# def delete_item(post_id: int, db: Session = Depends(get_db)) -> Post:
#     try:
#         db_post = delete_db_post(post_id, db)
#     except NotFoundError as e:
#         raise HTTPException(status_code=404) from e
#     return Post(**db_post.__dict__)


# @router.post("/posts/", response_model=Post)
# def create_post(
#     post: PostCreate, tag_ids: List[int], db: Session = Depends(get_db)
# ):
#     db_post = Post(**post.model_dump())

#     for tag_id in tag_ids:
#         tag = db.query(TagDB).filter(TagDB.id == tag_id).first()
#         if tag is None:
#             raise HTTPException(
#                 status_code=404, detail=f"Tag with id {tag_id} not found"
#             )
#         db_post.tags.append(tag)

#     db.add(db_post)
#     db.commit()
#     db.refresh(db_post)
#     return db_post


# # Ruta para obtener los tags relacionados con un post
# @router.get("/posts/{post_id}/tags/", response_model=List[Tag])
# def get_tags_for_post(post_id: int, db: Session = Depends(get_db)):
#     post = db.query(Post).filter(Post.id == post_id).first()
#     if post is None:
#         raise HTTPException(status_code=404, detail="Post not found")
#     return post.tags
