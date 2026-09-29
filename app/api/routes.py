from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.db_models import (
    CrawlResult,
    PokemonMetaEntry,
    PokemonMetaSnapshot,
    PokemonTierResult,
)
from app.models.schemas import (
    CrawlRecord,
    CrawlRequest,
    PokemonMetaEntryRecord,
    PokemonMetaFetchResponse,
    PokemonTierRecord,
    PokemonTierRequest,
)
from app.services.crawler import crawl_website
from app.services.pokemon_meta import fetch_and_parse_pokemon_meta
from app.services.pokemon_tiering import generate_pokemon_tiers
from app.services.sample_loader import load_sample_pokemon_meta

router = APIRouter()


@router.get("/")
def health_check():
    return {
        "status": "running",
        "project": "Agentic Pokémon Unite Meta Tiering Platform",
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


@router.post("/meta/fetch", response_model=PokemonMetaFetchResponse)
def fetch_pokemon_meta(db: Session = Depends(get_db)):
    try:
        parsed_data = fetch_and_parse_pokemon_meta()
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch or parse Pokémon meta data: {str(error)}",
        )

    snapshot = PokemonMetaSnapshot(
        source_url=parsed_data["source_url"],
        data_period=parsed_data["data_period"],
        games_analyzed=parsed_data["games_analyzed"],
    )

    db.add(snapshot)
    db.commit()
    db.refresh(snapshot)

    saved_entries = []

    for item in parsed_data["entries"]:
        entry = PokemonMetaEntry(
            snapshot_id=snapshot.id,
            rank=item["rank"],
            pokemon_name=item["pokemon_name"],
            win_rate=item["win_rate"],
            pick_rate=item["pick_rate"],
            ban_rate=item["ban_rate"],
            meta_score=item["meta_score"],
        )

        db.add(entry)
        saved_entries.append(entry)

    db.commit()

    for entry in saved_entries:
        db.refresh(entry)

    return {
        "snapshot_id": snapshot.id,
        "source_url": snapshot.source_url,
        "data_period": snapshot.data_period,
        "games_analyzed": snapshot.games_analyzed,
        "total_pokemon": len(saved_entries),
        "entries": saved_entries,
    }

@router.post("/meta/load-sample", response_model=PokemonMetaFetchResponse)
def load_sample_meta(db: Session = Depends(get_db)):
    try:
        parsed_data = load_sample_pokemon_meta()
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load sample Pokémon meta data: {str(error)}",
        )

    snapshot = PokemonMetaSnapshot(
        source_url=parsed_data["source_url"],
        data_period=parsed_data["data_period"],
        games_analyzed=parsed_data["games_analyzed"],
    )

    db.add(snapshot)
    db.commit()
    db.refresh(snapshot)

    saved_entries = []

    for item in parsed_data["entries"]:
        entry = PokemonMetaEntry(
            snapshot_id=snapshot.id,
            rank=item["rank"],
            pokemon_name=item["pokemon_name"],
            win_rate=item["win_rate"],
            pick_rate=item["pick_rate"],
            ban_rate=item["ban_rate"],
            meta_score=item["meta_score"],
        )

        db.add(entry)
        saved_entries.append(entry)

    db.commit()

    for entry in saved_entries:
        db.refresh(entry)

    return {
        "snapshot_id": snapshot.id,
        "source_url": snapshot.source_url,
        "data_period": snapshot.data_period,
        "games_analyzed": snapshot.games_analyzed,
        "total_pokemon": len(saved_entries),
        "entries": saved_entries,
    }

@router.get("/meta/latest", response_model=List[PokemonMetaEntryRecord])
def get_latest_pokemon_meta(db: Session = Depends(get_db)):
    latest_snapshot = (
        db.query(PokemonMetaSnapshot)
        .order_by(PokemonMetaSnapshot.created_at.desc())
        .first()
    )

    if not latest_snapshot:
        raise HTTPException(
            status_code=404,
            detail="No Pokémon meta snapshot found. Run POST /meta/fetch first.",
        )

    entries = (
        db.query(PokemonMetaEntry)
        .filter(PokemonMetaEntry.snapshot_id == latest_snapshot.id)
        .order_by(PokemonMetaEntry.rank.asc())
        .all()
    )

    return entries


@router.post("/meta/tier", response_model=List[PokemonTierRecord])
def create_pokemon_tiers(
    request: PokemonTierRequest,
    db: Session = Depends(get_db),
):
    if request.n_clusters < 2:
        raise HTTPException(
            status_code=400,
            detail="n_clusters must be at least 2.",
        )

    latest_snapshot = (
        db.query(PokemonMetaSnapshot)
        .order_by(PokemonMetaSnapshot.created_at.desc())
        .first()
    )

    if not latest_snapshot:
        raise HTTPException(
            status_code=404,
            detail="No Pokémon meta snapshot found. Run POST /meta/fetch first.",
        )

    meta_entries = (
        db.query(PokemonMetaEntry)
        .filter(PokemonMetaEntry.snapshot_id == latest_snapshot.id)
        .order_by(PokemonMetaEntry.rank.asc())
        .all()
    )

    if len(meta_entries) < request.n_clusters:
        raise HTTPException(
            status_code=400,
            detail=f"Need at least {request.n_clusters} Pokémon entries. "
                   f"Currently found {len(meta_entries)}.",
        )

    try:
        tier_data = generate_pokemon_tiers(
            meta_entries=meta_entries,
            n_clusters=request.n_clusters,
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    db.query(PokemonTierResult).filter(
        PokemonTierResult.snapshot_id == latest_snapshot.id
    ).delete()
    db.commit()

    saved_results = []

    for item in tier_data:
        tier_result = PokemonTierResult(
            snapshot_id=item["snapshot_id"],
            pokemon_name=item["pokemon_name"],
            cluster_label=item["cluster_label"],
            tier=item["tier"],
            score=item["score"],
            win_rate=item["win_rate"],
            pick_rate=item["pick_rate"],
            ban_rate=item["ban_rate"],
        )

        db.add(tier_result)
        saved_results.append(tier_result)

    db.commit()

    for result in saved_results:
        db.refresh(result)

    tier_order = {
        "S": 0,
        "A": 1,
        "B": 2,
        "C": 3,
        "D": 4,
        "E": 5,
        "F": 6,
    }

    sorted_results = sorted(
        saved_results,
        key=lambda item: (
            tier_order.get(item.tier, 999),
            -item.score,
        ),
    )

    return sorted_results


@router.get("/meta/tiers", response_model=List[PokemonTierRecord])
def get_latest_pokemon_tiers(db: Session = Depends(get_db)):
    latest_snapshot = (
        db.query(PokemonMetaSnapshot)
        .order_by(PokemonMetaSnapshot.created_at.desc())
        .first()
    )

    if not latest_snapshot:
        raise HTTPException(
            status_code=404,
            detail="No Pokémon meta snapshot found. Run POST /meta/fetch or POST /meta/load-sample first.",
        )

    results = (
        db.query(PokemonTierResult)
        .filter(PokemonTierResult.snapshot_id == latest_snapshot.id)
        .all()
    )

    tier_order = {
        "S": 0,
        "A": 1,
        "B": 2,
        "C": 3,
        "D": 4,
        "E": 5,
        "F": 6,
    }

    return sorted(
        results,
        key=lambda item: (
            tier_order.get(item.tier, 999),
            -item.score,
        ),
    )