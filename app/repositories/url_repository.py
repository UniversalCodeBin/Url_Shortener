from typing import Optional
from uuid import UUID
from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.url import URL
from app.schemas.url import URLCreate


class URLRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, url_data: URLCreate, short_code: str) -> URL:
        url = URL(
            original_url=url_data.original_url,
            short_code=short_code,
        )
        self.db.add(url)
        await self.db.flush()
        await self.db.refresh(url)
        return url

    async def get_by_id(self, url_id: UUID) -> Optional[URL]:
        result = await self.db.execute(
            select(URL).where(URL.id == str(url_id))
        )
        return result.scalar_one_or_none()

    async def get_by_short_code(self, short_code: str) -> Optional[URL]:
        result = await self.db.execute(
            select(URL).where(URL.short_code == short_code, URL.is_active == True)
        )
        return result.scalar_one_or_none()

    async def get_by_original_url(self, original_url: str) -> Optional[URL]:
        result = await self.db.execute(
            select(URL).where(URL.original_url == original_url, URL.is_active == True)
        )
        return result.scalar_one_or_none()

    async def update(self, url_id: UUID, url_data: dict) -> Optional[URL]:
        await self.db.execute(
            update(URL).where(URL.id == str(url_id)).values(**url_data)
        )
        await self.db.flush()
        return await self.get_by_id(url_id)

    async def delete(self, url_id: UUID) -> bool:
        result = await self.db.execute(
            delete(URL).where(URL.id == str(url_id))
        )
        await self.db.flush()
        return result.rowcount > 0

    async def increment_clicks(self, short_code: str) -> Optional[URL]:
        await self.db.execute(
            update(URL)
            .where(URL.short_code == short_code)
            .values(clicks=URL.clicks + 1)
        )
        await self.db.flush()
        return await self.get_by_short_code(short_code)

    async def get_urls(self, skip: int = 0, limit: int = 100) -> list[URL]:
        result = await self.db.execute(
            select(URL).offset(skip).limit(limit).order_by(URL.created_at.desc())
        )
        return list(result.scalars().all())

    async def count(self) -> int:
        result = await self.db.execute(select(func.count(URL.id)))
        return result.scalar_one()
