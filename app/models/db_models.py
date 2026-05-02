from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String

from app.core.database import Base


class CrawlResult(Base):
    __tablename__ = "crawl_results"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, index=True, nullable=False)
    title = Column(String, nullable=True)
    word_count = Column(Integer, nullable=False, default=0)
    link_count = Column(Integer, nullable=False, default=0)
    image_count = Column(Integer, nullable=False, default=0)
    heading_count = Column(Integer, nullable=False, default=0)
    status = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)