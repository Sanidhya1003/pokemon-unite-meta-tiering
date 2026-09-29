from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String

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


class PokemonMetaSnapshot(Base):
    __tablename__ = "pokemon_meta_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    source_url = Column(String, nullable=False)
    data_period = Column(String, nullable=True)
    games_analyzed = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class PokemonMetaEntry(Base):
    __tablename__ = "pokemon_meta_entries"

    id = Column(Integer, primary_key=True, index=True)
    snapshot_id = Column(Integer, ForeignKey("pokemon_meta_snapshots.id"), nullable=False)
    rank = Column(Integer, nullable=False)
    pokemon_name = Column(String, index=True, nullable=False)
    win_rate = Column(Float, nullable=False)
    pick_rate = Column(Float, nullable=False)
    ban_rate = Column(Float, nullable=False)
    meta_score = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class PokemonTierResult(Base):
    __tablename__ = "pokemon_tier_results"

    id = Column(Integer, primary_key=True, index=True)
    snapshot_id = Column(Integer, ForeignKey("pokemon_meta_snapshots.id"), nullable=False)
    pokemon_name = Column(String, index=True, nullable=False)
    cluster_label = Column(Integer, nullable=False)
    tier = Column(String, nullable=False)
    score = Column(Float, nullable=False)
    win_rate = Column(Float, nullable=False)
    pick_rate = Column(Float, nullable=False)
    ban_rate = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)