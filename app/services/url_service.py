from typing import Optional
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.url_repository import URLRepository
from app.schemas.url import URLCreate, URLResponse, URLListResponse
from app.utils.short_code import generate_short_code
from app.core.cache import cache
from app.config import get_settings

settings = get_settings()


class URLService:
    def __init__(self, db: AsyncSession):
        self.repository = URLRepository(db)
        self.base_url = settings.BASE_URL

    async def create_url(self, url_data: URLCreate) -> URLResponse:
        if url_data.custom_code:
            existing = await self.repository.get_by_short_code(url_data.custom_code)
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Custom short code already exists"
                )
            short_code = url_data.custom_code
        else:
            existing = await self.repository.get_by_original_url(url_data.original_url)
            if existing:
                return self._to_response(existing)
            
            short_code = await self._generate_unique_code()

        url = await self.repository.create(url_data, short_code)
        await cache.set(f"url:{short_code}", url.original_url, expire=86400)
        return self._to_response(url)

    async def get_url(self, url_id: UUID) -> URLResponse:
        url = await self.repository.get_by_id(url_id)
        if not url:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="URL not found"
            )
        return self._to_response(url)

    async def redirect_url(self, short_code: str) -> str:
        cached_url = await cache.get(f"url:{short_code}")
        if cached_url:
            await self.repository.increment_clicks(short_code)
            return cached_url
        
        url = await self.repository.get_by_short_code(short_code)
        if not url:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="URL not found"
            )
        await cache.set(f"url:{short_code}", url.original_url, expire=86400)
        await self.repository.increment_clicks(short_code)
        return url.original_url

    async def delete_url(self, url_id: UUID) -> bool:
        url = await self.repository.get_by_id(url_id)
        if not url:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="URL not found"
            )
        await cache.delete(f"url:{url.short_code}")
        return await self.repository.delete(url_id)

    async def get_urls(self, skip: int = 0, limit: int = 100) -> URLListResponse:
        urls = await self.repository.get_urls(skip, limit)
        total = await self.repository.count()
        return URLListResponse(
            urls=[self._to_response(url) for url in urls],
            total=total,
            skip=skip,
            limit=limit
        )

    async def get_url_stats(self, url_id: UUID) -> dict:
        url = await self.repository.get_by_id(url_id)
        if not url:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="URL not found"
            )
        return {
            "id": url.id,
            "original_url": url.original_url,
            "short_code": url.short_code,
            "clicks": url.clicks,
            "created_at": url.created_at,
        }

    async def search_urls(self, query: str, limit: int = 20) -> list[URLResponse]:
        urls = await self.repository.search_urls(query, limit)
        return [self._to_response(url) for url in urls]

    async def _generate_unique_code(self) -> str:
        for _ in range(10):
            code = generate_short_code()
            existing = await self.repository.get_by_short_code(code)
            if not existing:
                return code
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate unique short code"
        )

    def _to_response(self, url) -> URLResponse:
        return URLResponse(
            id=url.id,
            original_url=url.original_url,
            short_code=url.short_code,
            short_url=f"{self.base_url}/{url.short_code}",
            is_active=url.is_active,
            clicks=url.clicks,
            created_at=url.created_at,
            updated_at=url.updated_at,
        )
