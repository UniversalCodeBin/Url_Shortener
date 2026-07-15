from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, HttpUrl


class URLCreate(BaseModel):
    original_url: str = Field(..., max_length=2048, description="The original URL to shorten")
    custom_code: Optional[str] = Field(None, min_length=3, max_length=10, description="Optional custom short code")


class URLResponse(BaseModel):
    id: UUID
    original_url: str
    short_code: str
    short_url: str
    is_active: bool
    clicks: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class URLListResponse(BaseModel):
    urls: list[URLResponse]
    total: int
    skip: int
    limit: int


class URLStatsResponse(BaseModel):
    id: UUID
    original_url: str
    short_code: str
    clicks: int
    created_at: datetime
