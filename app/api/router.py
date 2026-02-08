from fastapi import APIRouter

from .user.router import router as user_router

main_router = APIRouter(prefix="/api")
main_router.include_router(user_router)
