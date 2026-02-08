from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .rate_limit import RateLimitMiddleware


def setup_middleware(app: FastAPI) -> None:
    """
    Подключение всех middleware приложения.
    """

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Rate limiting
    app.add_middleware(RateLimitMiddleware)
