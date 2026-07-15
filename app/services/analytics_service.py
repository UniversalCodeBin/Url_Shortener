from datetime import datetime
from typing import Optional
from uuid import UUID
from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.analytics_repository import AnalyticsRepository


class AnalyticsService:
    def __init__(self, db: AsyncSession):
        self.repository = AnalyticsRepository(db)

    async def record_click(
        self,
        url_id: UUID,
        request: Optional[Request] = None,
    ) -> None:
        ip_address = None
        user_agent = None
        referer = None

        if request:
            ip_address = request.client.host if request.client else None
            user_agent = request.headers.get("user-agent")
            referer = request.headers.get("referer")

        await self.repository.record_click(
            url_id=url_id,
            ip_address=ip_address,
            user_agent=user_agent,
            referer=referer,
        )

    async def get_url_analytics(
        self,
        url_id: UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> dict:
        clicks = await self.repository.get_clicks_by_url(url_id, start_date, end_date)
        total_clicks = await self.repository.get_click_count_by_url(url_id, start_date, end_date)

        return {
            "url_id": str(url_id),
            "total_clicks": total_clicks,
            "clicks": [
                {
                    "id": str(click.id),
                    "ip_address": click.ip_address,
                    "user_agent": click.user_agent,
                    "referer": click.referer,
                    "clicked_at": click.clicked_at.isoformat(),
                }
                for click in clicks
            ],
        }

    async def get_top_urls(self, limit: int = 10) -> list[dict]:
        return await self.repository.get_top_urls(limit)
