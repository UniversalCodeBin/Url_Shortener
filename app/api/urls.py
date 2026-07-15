from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.base import get_db
from app.services.url_service import URLService
from app.schemas.url import URLCreate, URLResponse, URLListResponse

router = APIRouter(prefix="/urls", tags=["URLs"])


@router.post("/", response_model=URLResponse, status_code=status.HTTP_201_CREATED)
async def create_url(
    url_data: URLCreate,
    db: AsyncSession = Depends(get_db),
) -> URLResponse:
    service = URLService(db)
    return await service.create_url(url_data)


@router.get("/", response_model=URLListResponse)
async def get_urls(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
) -> URLListResponse:
    service = URLService(db)
    return await service.get_urls(skip=skip, limit=limit)


@router.get("/{url_id}", response_model=URLResponse)
async def get_url(
    url_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> URLResponse:
    service = URLService(db)
    return await service.get_url(url_id)


@router.delete("/{url_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_url(
    url_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    service = URLService(db)
    await service.delete_url(url_id)


@router.get("/{url_id}/stats")
async def get_url_stats(
    url_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> dict:
    service = URLService(db)
    return await service.get_url_stats(url_id)
