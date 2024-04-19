from typing import Annotated
from fastapi import APIRouter, Depends, Request
from app.db.core import get_db
from app.users.user_schema import User, create_db_user, UserCreate
from app.tokens.token_schema import get_current_active_user
from sqlalchemy.orm import Session


router = APIRouter(
    prefix="/users",
)


@router.get("/me/", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return current_user


@router.get("/me/items/")
async def read_own_items(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return [{"item_id": "Foo", "owner": current_user.username}]


@router.post("/create")
def create_user(
    # current_user: Annotated[User, Depends(get_current_active_user)],
    user: UserCreate,
    db: Session = Depends(get_db),
) -> User:
    db_user = create_db_user(user, db)
    return User(**db_user.__dict__)
