from datetime import  timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm

from app.db.core import get_db
from app.db.user import(
    User,
    get_current_active_user,
    create_db_user,
    UserCreate
)
from sqlalchemy.orm import Session


# to get a string like this run:
# openssl rand -hex 32
# SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
# # ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES = 30


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


#User Routes

@router.post("/create")
def create_user(
    current_user: Annotated[User, Depends(get_current_active_user)],
    request: Request,
    user: UserCreate,
    db: Session = Depends(get_db),
) -> User:
    db_user = create_db_user(user, db)
    return User(**db_user.__dict__)