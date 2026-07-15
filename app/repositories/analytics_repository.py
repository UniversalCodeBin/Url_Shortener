from datetime import datetime
from typing import Optional
from uuid import UUID
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.analytics import ClickEvent
from app.models.url import URL


class AnalyticsRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def record_click(
        self,
        url_id: UUID,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        referer: Optional[str] = None,
        country: Optional[str] = None,
        city: Optional[str] = None,
    ) -> ClickEvent:
        click = ClickEvent(
            url_id=str(url_id),
            ip_address=ip_address,
            user_agent=user_agent,
            referer=referer,
            country=country,
            city=city,
        )
        self.db.add(click)
        await self.db.flush()
        await self.db.refresh(click)
        return click

    async def get_clicks_by_url(
        self,
        url_id: UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> list[ClickEvent]:
        query = select(ClickEvent).where(ClickEvent.url_id == str(url_id))
        
        if start_date:
            query = query.where(ClickEvent.clicked_at >= start_date)
        if end_date:
            query = query.where(ClickEvent.clicked_at <= end_date)
        
        query = query.order_by(ClickEvent.clicked_at.desc())
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_click_count_by_url(
        self,
        url_id: UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> int:
        query = select(func.count(ClickEvent.id)).where(ClickEvent.url_id == str(url_id))
        
        if start_date:
            query = query.where(ClickEvent.clicked_at >= start_date)
        if end_date:
            query = query.where(ClickEvent.clicked_at <= end_date)
        
        result = await self.db.execute(query)
        return result.scalar_one()

    async def get_top_urls(self, limit: int = 10) -> list[dict]:
        result = await self.db.execute(
            select(
                URL.id,
                URL.original_url,
                URL.short_code,
                func.count(ClickEvent.id).label("click_count"),
            )
            .join(ClickEvent, URL.id == ClickEvent.url_id)
            .group_by(URL.id, URL.original_url, URL.short_code)
            .order_by(func.count(ClickEvent.id).desc())
            .limit(limit)
        )
        return [
            {
                "id": row.id,
                "original_url": row.original_url,
                "short_code": row.short_code,
                "click_count": row.click_count,
            }
            for row in result.all()
        ]
