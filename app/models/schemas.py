from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, HttpUrl


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

    model_config = ConfigDict(from_attributes=True)


class PokemonMetaEntryRecord(BaseModel):
    id: int
    snapshot_id: int
    rank: int
    pokemon_name: str
    win_rate: float
    pick_rate: float
    ban_rate: float
    meta_score: float
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PokemonMetaFetchResponse(BaseModel):
    snapshot_id: int
    source_url: str
    data_period: Optional[str] = None
    games_analyzed: Optional[int] = None
    total_pokemon: int
    entries: list[PokemonMetaEntryRecord]


class PokemonTierRequest(BaseModel):
    n_clusters: int = 5


class PokemonTierRecord(BaseModel):
    id: int
    snapshot_id: int
    pokemon_name: str
    cluster_label: int
    tier: str
    score: float
    win_rate: float
    pick_rate: float
    ban_rate: float
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)