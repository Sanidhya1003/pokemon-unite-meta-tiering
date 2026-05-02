from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.db_models import CrawlResult
from app.models.schemas import CrawlRecord, CrawlRequest
from app.services.crawler import crawl_website

router = APIRouter()


@router.get("/")
def health_check():
    return {
        "status": "running",
        "project": "Agentic Web Tiering Platform",
    }


@router.post("/crawl", response_model=CrawlRecord)
def crawl(request: CrawlRequest, db: Session = Depends(get_db)):
    metrics = crawl_website(str(request.url))

    crawl_result = CrawlResult(
        url=metrics["url"],
        title=metrics["title"],
        word_count=metrics["word_count"],
        link_count=metrics["link_count"],
        image_count=metrics["image_count"],
        heading_count=metrics["heading_count"],
        status=metrics["status"],
    )

    db.add(crawl_result)
    db.commit()
    db.refresh(crawl_result)

    return crawl_result


@router.get("/history", response_model=List[CrawlRecord])
def get_history(db: Session = Depends(get_db)):
    results = (
        db.query(CrawlResult)
        .order_by(CrawlResult.created_at.desc())
        .all()
    )

    return results