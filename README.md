# Pokémon Unite Meta Tiering

A FastAPI backend that loads Pokémon Unite meta data, calculates a custom performance score, and assigns Pokémon into score-based tiers.

This project converts a notebook-style analysis workflow into a backend API with structured data storage, reproducible sample loading, and deterministic tier generation.

## Features

- FastAPI backend with interactive Swagger docs
- SQLite database storage using SQLAlchemy
- Pokémon meta score calculation: `win_rate × pick_rate`
- Score-only tiering logic using natural score breaks
- Reproducible sample dataset for local testing
- Optional live fetch endpoint for UniteAPI/Jina-rendered data
- API endpoints for loading data, viewing latest entries, generating tiers, and retrieving tier results

## Tech Stack

- Python
- FastAPI
- SQLAlchemy
- SQLite
- NumPy
- Requests
- BeautifulSoup
- uv
- Uvicorn

## Project Structure

```text
app/
├── api/
│   └── routes.py
├── core/
│   └── database.py
├── models/
│   ├── db_models.py
│   └── schemas.py
├── services/
│   ├── crawler.py
│   ├── pokemon_meta.py
│   ├── pokemon_tiering.py
│   └── sample_loader.py
└── main.py

data/
└── sample_unite_meta.csv
```

## How to Run Locally

Clone the repository:

```bash
git clone https://github.com/Sanidhya1003/pokemon-unite-meta-tiering.git
cd pokemon-unite-meta-tiering
```

Install dependencies:

```bash
uv sync
```

Run the API:

```bash
uv run python -m uvicorn app.main:app --reload
```

Open Swagger UI:

```text
http://127.0.0.1:8000/docs
```

## Recommended Local Flow

Use the sample dataset for a reproducible demo:

```text
POST /meta/load-sample
GET  /meta/latest
POST /meta/tier
GET  /meta/tiers
```

The live fetch endpoint is available but experimental:

```text
POST /meta/fetch
```

The upstream UniteAPI site may return bot-protection pages to automated requests, so `/meta/load-sample` is the reliable local testing path.

## Tiering Logic

The project uses this custom score:

```text
meta_score = win_rate × pick_rate
```

Tiering is based only on `meta_score`.

This means higher tiers always represent higher score ranges:

```text
S → A → B → C → D → E → F
```

Ban rate is stored for reference but is not used for tier assignment.

## Current Status

Completed:

- FastAPI backend
- SQLite database persistence
- Pokémon meta sample loader
- Meta score calculation
- Score-based tiering
- Swagger API testing flow

Planned improvements:

- CSV upload endpoint
- Frontend dashboard
- Docker deployment
- LangGraph workflow orchestration
- AI-generated tier explanations
