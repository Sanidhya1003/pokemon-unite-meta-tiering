import csv
from pathlib import Path
from typing import Any


SAMPLE_DATA_PATH = Path("data/sample_unite_meta.csv")


def load_sample_pokemon_meta() -> dict[str, Any]:
    if not SAMPLE_DATA_PATH.exists():
        raise FileNotFoundError(f"Sample data file not found: {SAMPLE_DATA_PATH}")

    entries = []

    with SAMPLE_DATA_PATH.open("r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            win_rate = float(row["win_rate"])
            pick_rate = float(row["pick_rate"])
            ban_rate = float(row["ban_rate"])

            entries.append(
                {
                    "rank": int(row["rank"]),
                    "pokemon_name": row["pokemon_name"],
                    "win_rate": win_rate,
                    "pick_rate": pick_rate,
                    "ban_rate": ban_rate,
                    "meta_score": win_rate * pick_rate,
                }
            )

    return {
        "source_url": "local_sample_data",
        "data_period": "Sample development dataset",
        "games_analyzed": None,
        "entries": entries,
    }