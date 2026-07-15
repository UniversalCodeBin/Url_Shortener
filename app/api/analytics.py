from datetime import datetime
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.base import get_db
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/{url_id}")
async def get_url_analytics(
    url_id: UUID,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db),
) -> dict:
    service = AnalyticsService(db)
    return await service.get_url_analytics(url_id, start_date, end_date)


@router.get("/top/urls")
async def get_top_urls(
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    service = AnalyticsService(db)
    return await service.get_top_urls(limit)
