from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path, status
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth.dependencies import verify_token
from app.api.auth.schemas import TokenUser
from app.api.schemas import ErrorResponse
from app.clients.db import get_async_session
from app.services.order import OrderService

from ...clients.redis import get_redis
from .schemas import OrderCreate, OrderFromDB, OrdersList, OrderStatusUpdate

router = APIRouter(tags=["Order"])


@router.post(
    "/orders",
    response_model=OrderFromDB,
    status_code=status.HTTP_201_CREATED,
    name="Создать заказа",
    description="Создание заказа для пользователя",
    responses={
        401: {"model": ErrorResponse, "description": "Пользователь не авторизован"},
        500: {"model": ErrorResponse, "description": "Внутренняя ошибка сервера"},
    },
)
async def create_order(
    data: OrderCreate,
    session: AsyncSession = Depends(get_async_session),
    redis: Redis = Depends(get_redis),
    user: TokenUser = Depends(verify_token),
) -> OrderFromDB:
    order = await OrderService(session, redis).create_order(user.id, data.items, data.total_price)
    return OrderFromDB.model_validate(order)


@router.get(
    "/orders/{order_id}",
    response_model=OrderFromDB,
    status_code=status.HTTP_200_OK,
    name="Получить заказа",
    description="Получение заказа по его идентификатору",
    responses={
        401: {"model": ErrorResponse, "description": "Пользователь не авторизован"},
        403: {"model": ErrorResponse, "description": "Пользователь не имеет доступ к заказу"},
        404: {"model": ErrorResponse, "description": "Заказ не найден"},
        500: {"model": ErrorResponse, "description": "Внутренняя ошибка сервера"},
    },
)
async def get_order(
    order_id: UUID = Path(..., description="ID заказа"),
    session: AsyncSession = Depends(get_async_session),
    redis: Redis = Depends(get_redis),
    user: TokenUser = Depends(verify_token),
) -> OrderFromDB:
    order = await OrderService(session, redis).get_order(order_id, user.id)
    return OrderFromDB.model_validate(order)


@router.patch(
    "/orders/{order_id}",
    response_model=OrderFromDB,
    status_code=status.HTTP_200_OK,
    name="Изменить статус заказа",
    description="Изменение статуса заказа (PENDING, PAID, SHIPPED, CANCELED)",
    responses={
        401: {"model": ErrorResponse, "description": "Пользователь не авторизован"},
        403: {"model": ErrorResponse, "description": "Пользователь не имеет доступ к заказу"},
        404: {"model": ErrorResponse, "description": "Заказ не найден"},
        409: {"model": ErrorResponse, "description": "Конфликт изменения статуса заказа"},
        500: {"model": ErrorResponse, "description": "Внутренняя ошибка сервера"},
    },
)
async def update_order_status(
    data: OrderStatusUpdate,
    order_id: UUID = Path(..., description="ID заказа"),
    session: AsyncSession = Depends(get_async_session),
    redis: Redis = Depends(get_redis),
    user: TokenUser = Depends(verify_token),
) -> OrderFromDB:
    order = await OrderService(session, redis).update_order_status(order_id, data.status, user.id)
    return OrderFromDB.model_validate(order)


@router.get(
    "/orders/user/{user_id}",
    response_model=OrdersList,
    status_code=status.HTTP_200_OK,
    name="Получить заказы пользователя",
    description="Получение списка заказов пользователя",
    responses={
        401: {"model": ErrorResponse, "description": "Пользователь не авторизован"},
        403: {"model": ErrorResponse, "description": "Пользователь не имеет доступ к заказам другого пользователя"},
        500: {"model": ErrorResponse, "description": "Внутренняя ошибка сервера"},
    },
)
async def get_user_orders(
    user_id: int = Path(..., description="ID пользователя"),
    session: AsyncSession = Depends(get_async_session),
    user: TokenUser = Depends(verify_token),
) -> OrdersList:
    if user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User ({user.id=}) don't have access to the orders of another user ({user_id=})",
        )
    orders = await OrderService(session).get_user_orders(user_id)
    return OrdersList(items=[OrderFromDB.model_validate(order) for order in orders], count=len(orders))
