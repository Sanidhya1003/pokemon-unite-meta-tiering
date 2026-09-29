from fastapi import FastAPI

from app.api.routes import router
from app.core.database import Base, engine
from app.models import db_models

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Pokémon Unite Meta Tiering",
    description="A FastAPI backend for loading Pokémon Unite meta data, calculating meta scores, and generating score-based tiers.",
    version="0.1.0",
)

app.include_router(router)
