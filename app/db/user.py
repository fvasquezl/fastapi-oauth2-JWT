from datetime import datetime
from typing import  Optional
from pydantic import BaseModel
from app.db.core import DBUser
from sqlalchemy.orm import Session
from app.lib.hasher import Hasher

class UserBase(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None

class UserCreate(UserBase):
    hashed_password: str


class User(UserBase):
    id: int
    disabled: bool | None = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


def read_db_user(user_id: int, session: Session) -> DBUser:
    db_user = session.query(DBUser).filter(DBUser.id == user_id).first()
    if db_user is None:
        raise FileNotFoundError(f"user with id {user_id} not found.")
    return db_user


def create_db_user(user: UserCreate, session: Session) -> DBUser:
    db_user = DBUser(**user.model_dump(exclude_none=True))
    db_user.hashed_password = Hasher.get_password_hash(user.hashed_password)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user