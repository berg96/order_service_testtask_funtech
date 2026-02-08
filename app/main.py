from fastapi import FastAPI

from .api.router import main_router
from .config.middleware import setup_middleware
from .config.settings import settings

app = FastAPI(title=settings.APP_TITLE, description=settings.APP_DESCRIPTION)

setup_middleware(app)
app.include_router(main_router)
