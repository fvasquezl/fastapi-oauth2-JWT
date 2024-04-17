from datetime import  timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.db.core import get_db
from app.db.user import(
    Token,
    authenticate_user,
    create_access_token,
)
from sqlalchemy.orm import Session


# to get a string like this run:
# openssl rand -hex 32
# SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
# # ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


router = APIRouter(
    prefix="/token",
)


@router.post("/")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db)
) -> Token:
    user = authenticate_user(db,form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    ) 
    return Token(access_token=access_token, token_type="bearer")


# @router.get("/me/", response_model=User)
# async def read_users_me(
#     current_user: Annotated[User, Depends(get_current_active_user)],
# ):
#     return current_user



