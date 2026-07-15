from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.base import get_db
from app.services.url_service import URLService

router = APIRouter(tags=["Redirect"])


@router.get("/{short_code}")
async def redirect_url(
    short_code: str,
    db: AsyncSession = Depends(get_db),
) -> RedirectResponse:
    service = URLService(db)
    original_url = await service.redirect_url(short_code)
    return RedirectResponse(url=original_url)
