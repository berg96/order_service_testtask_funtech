from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.api.auth.jwt import JWTToken
from app.api.schemas import ErrorResponse
from app.clients.db import get_async_session
from app.domain.exceptions import UserAlreadyExists
from app.services.user.service import UserService

from .schemas import Token, UserFromDB, UserRegister

router = APIRouter(tags=["User [Auth]"])


@router.post(
    "/register",
    response_model=UserFromDB,
    status_code=status.HTTP_201_CREATED,
    name="Зарегистрировать пользователя",
    description="Зарегистрировать пользователя по уникальному email и паролю",
    responses={
        409: {"model": ErrorResponse, "description": "Пользователь уже существует"},
        500: {"model": ErrorResponse, "description": "Внутренняя ошибка сервера"},
    },
)
async def register(
    data: UserRegister,
    session: AsyncSession = Depends(get_async_session),
) -> UserFromDB:
    try:
        user = await UserService(session).register_user(str(data.email), data.password)
    except UserAlreadyExists:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists")

    return UserFromDB.model_validate(user)


@router.post(
    "/token",
    response_model=Token,
    status_code=status.HTTP_200_OK,
    name="Авторизовать пользователя",
    description="Получить JWT пользователя по его email и паролю",
    responses={
        401: {"model": ErrorResponse, "description": "Неверный email или пароль"},
        500: {"model": ErrorResponse, "description": "Внутренняя ошибка сервера"},
    },
)
async def login(
    data: UserRegister,
    session: AsyncSession = Depends(get_async_session),
) -> Token:
    try:
        user = await UserService(session).authenticate_user(str(data.email), data.password)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

    return Token(
        access_token=JWTToken().encode({"uuid": str(user.uuid)}),
        refresh_token=JWTToken().create_refresh_token(user_uuid=user.uuid),
    )
