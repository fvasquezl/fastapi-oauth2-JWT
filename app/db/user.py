from datetime import datetime, timedelta, timezone
from typing import Annotated, Optional

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from app.db.core import DBUser, get_db
from sqlalchemy.orm import Session
from app.lib.hasher import Hasher


# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


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



pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()



def get_user(db, username: str):
    user = db.query(DBUser).filter(DBUser.username == username).first()
    return user


def authenticate_user(db,username: str, password: str):
    user = get_user(db, username)
    print(user.username)
    if not user:
        return False
    if not Hasher.verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(db: Session = Depends(get_db), token: str= Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

#User Routers

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