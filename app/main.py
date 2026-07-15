from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.api import urls_router, redirect_router, analytics_router
from app.core.cache import cache
from app.core.exceptions import setup_exception_handlers
from app.core.logging import logger

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting application...")
    await cache.connect()
    yield
    await cache.disconnect()
    logger.info("Shutting down application...")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    docs_url=f"{settings.API_V1_PREFIX}/docs",
    redoc_url=f"{settings.API_V1_PREFIX}/redoc",
    lifespan=lifespan,
)

setup_exception_handlers(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(urls_router, prefix=settings.API_V1_PREFIX)
app.include_router(redirect_router, prefix=settings.API_V1_PREFIX)
app.include_router(analytics_router, prefix=settings.API_V1_PREFIX)


@app.get("/health", tags=["Health"])
async def health_check() -> dict[str, str]:
    return {"status": "healthy", "version": settings.APP_VERSION}


@app.get("/", tags=["Root"])
async def root() -> dict[str, str]:
    return {"message": f"Welcome to {settings.APP_NAME} API"}
