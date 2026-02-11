from fastapi import APIRouter

from .order.router import router as order_router
from .user.router import router as user_router

main_router = APIRouter(prefix="/api")
main_router.include_router(user_router)
main_router.include_router(order_router)
