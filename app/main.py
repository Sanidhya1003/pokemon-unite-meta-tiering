from fastapi import FastAPI

from app.api.routes import router
from app.core.database import Base, engine
from app.models import db_models

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Agentic Web Tiering Platform",
    description="A deployable AI-assisted web intelligence and tiering system.",
    version="0.2.0",
)

app.include_router(router)