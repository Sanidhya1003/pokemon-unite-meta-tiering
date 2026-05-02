from datetime import datetime
from typing import Optional

from pydantic import BaseModel, HttpUrl


class CrawlRequest(BaseModel):
    url: HttpUrl


class CrawlMetrics(BaseModel):
    url: str
    title: Optional[str] = None
    word_count: int
    link_count: int
    image_count: int
    heading_count: int
    status: str


class CrawlRecord(CrawlMetrics):
    id: int
    created_at: datetime