from fastapi import FastAPI

from app.routers.user_router import router as user_router
from app.routers.token_router import router as token_router
from app.routers.post_router import router as post_router


app = FastAPI()
app.include_router(token_router)
app.include_router(user_router)
app.include_router(post_router, tags=["Posts"])
