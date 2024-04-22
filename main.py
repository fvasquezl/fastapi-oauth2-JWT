from fastapi import FastAPI

from app.routers.users.user_router import router as user_router
from app.routers.tokens.token_router import router as token_router
from app.routers.posts.post_router import router as post_router
from app.routers.categories.category_router import router as category_router


app = FastAPI()
app.include_router(token_router)
app.include_router(user_router)
app.include_router(post_router, tags=["Posts"])
app.include_router(category_router, tags=["Categories"])
