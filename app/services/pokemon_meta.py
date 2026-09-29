import re
from typing import Any

import requests


META_SOURCE_URLS = [
    "https://r.jina.ai/http://uniteapi.dev/en/meta",
    "https://r.jina.ai/http://www.uniteapi.dev/en/meta",
    "https://r.jina.ai/http://uniteapi.dev/en",
]


def fetch_meta_page(url: str) -> str:
    response = requests.get(
        url,
        headers={"User-Agent": "Mozilla/5.0 AgenticPokemonMetaBot/1.0"},
        timeout=60,
    )
    response.raise_for_status()
    return response.text


def parse_snapshot_metadata(text: str) -> dict[str, Any]:
    pattern = re.compile(
        r"(?:Pokemon Meta Statistics\s*)?Data from\s+(.*?)\s*\(([\d,]+)\s+games analyzed\)",
        re.IGNORECASE,
    )

    match = pattern.search(text)

    if not match:
        return {
            "data_period": "Unknown",
            "games_analyzed": None,
        }

    return {
        "data_period": match.group(1).strip(),
        "games_analyzed": int(match.group(2).replace(",", "")),
    }


def _clean_markdown(value: str) -> str:
    value = re.sub(r"!\[[^\]]*\]\([^)]+\)", "", value)
    value = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", value)
    value = value.replace("Image:", "")
    return value.strip()


def _clean_rank(rank_text: str) -> int:
    match = re.search(r"\d+", rank_text)

    if not match:
        raise ValueError(f"Could not parse rank: {rank_text}")

    return int(match.group(0))


def _extract_first_percentage(value: str) -> float:
    match = re.search(r"(\d+(?:\.\d+)?)%", value)

    if not match:
        raise ValueError(f"Could not parse percentage from: {value}")

    return float(match.group(1))


def _parse_table_rows(text: str) -> list[dict[str, Any]]:
    rows = []

    normalized_text = text.replace("│", "|")

    for raw_line in normalized_text.splitlines():
        line = raw_line.strip()

        if not line:
            continue

        if "Rank" in line and "Pokemon" in line:
            continue

        if "---" in line:
            continue

        if "|" not in line:
            continue

        parts = [part.strip() for part in line.strip("|").split("|")]

        if len(parts) < 5:
            continue

        if not re.search(r"\d+", parts[0]):
            continue

        try:
            rank = _clean_rank(parts[0])
            pokemon_name = _clean_markdown(parts[1])
            win_rate = _extract_first_percentage(parts[2])
            pick_rate = _extract_first_percentage(parts[3])
            ban_rate = _extract_first_percentage(parts[4])
        except ValueError:
            continue

        if not pokemon_name or pokemon_name.lower() == "pokemon":
            continue

        rows.append(
            {
                "rank": rank,
                "pokemon_name": pokemon_name,
                "win_rate": win_rate,
                "pick_rate": pick_rate,
                "ban_rate": ban_rate,
                "meta_score": win_rate * pick_rate,
            }
        )

    return rows


def _find_section_lines(text: str, section_name: str) -> list[str]:
    lines = [
        _clean_markdown(line.strip())
        for line in text.splitlines()
        if _clean_markdown(line.strip())
    ]

    start_index = None

    for index, line in enumerate(lines):
        clean_line = line.replace("#", "").strip().lower()

        if clean_line == section_name.lower():
            start_index = index + 1
            break

    if start_index is None:
        return []

    end_index = len(lines)

    known_sections = {
        "win rate",
        "pick rate",
        "ban rate",
    }

    for index in range(start_index, len(lines)):
        clean_line = lines[index].replace("#", "").strip().lower()

        if clean_line in known_sections and clean_line != section_name.lower():
            end_index = index
            break

    return lines[start_index:end_index]


def _parse_ranked_section(text: str, section_name: str, field_name: str) -> dict[str, dict[str, Any]]:
    section_lines = _find_section_lines(text, section_name)
    parsed = {}

    index = 0

    while index < len(section_lines) - 2:
        rank_line = section_lines[index]
        name_line = section_lines[index + 1]
        value_line = section_lines[index + 2]

        if re.fullmatch(r"\d+[+-]?", rank_line) and re.search(r"\d+(?:\.\d+)?%", value_line):
            try:
                rank = _clean_rank(rank_line)
                pokemon_name = _clean_markdown(name_line)
                value = _extract_first_percentage(value_line)
            except ValueError:
                index += 1
                continue

            if pokemon_name:
                parsed[pokemon_name] = {
                    "rank": rank,
                    field_name: value,
                }

            index += 3
        else:
            index += 1

    return parsed


def _parse_section_rows(text: str) -> list[dict[str, Any]]:
    win_data = _parse_ranked_section(text, "Win Rate", "win_rate")
    pick_data = _parse_ranked_section(text, "Pick Rate", "pick_rate")
    ban_data = _parse_ranked_section(text, "Ban Rate", "ban_rate")

    pokemon_names = set()
    pokemon_names.update(win_data.keys())
    pokemon_names.update(pick_data.keys())
    pokemon_names.update(ban_data.keys())

    rows = []

    for pokemon_name in pokemon_names:
        win_rate = win_data.get(pokemon_name, {}).get("win_rate")
        pick_rate = pick_data.get(pokemon_name, {}).get("pick_rate")
        ban_rate = ban_data.get(pokemon_name, {}).get("ban_rate", 0.0)

        if win_rate is None or pick_rate is None:
            continue

        rank = win_data.get(pokemon_name, {}).get("rank", 9999)

        rows.append(
            {
                "rank": rank,
                "pokemon_name": pokemon_name,
                "win_rate": win_rate,
                "pick_rate": pick_rate,
                "ban_rate": ban_rate,
                "meta_score": win_rate * pick_rate,
            }
        )

    rows.sort(key=lambda item: item["rank"])

    return rows


def parse_pokemon_meta_rows(text: str) -> list[dict[str, Any]]:
    table_rows = _parse_table_rows(text)

    if table_rows:
        return table_rows

    section_rows = _parse_section_rows(text)

    if section_rows:
        return section_rows

    preview = text[:1000].replace("\n", " ")

    raise ValueError(
        "No Pokémon meta rows were parsed. "
        f"Source preview: {preview}"
    )


def fetch_and_parse_pokemon_meta() -> dict[str, Any]:
    errors = []

    for source_url in META_SOURCE_URLS:
        try:
            text = fetch_meta_page(source_url)
            metadata = parse_snapshot_metadata(text)
            rows = parse_pokemon_meta_rows(text)

            return {
                "source_url": source_url,
                "data_period": metadata["data_period"],
                "games_analyzed": metadata["games_analyzed"],
                "entries": rows,
            }

        except Exception as error:
            errors.append(f"{source_url}: {str(error)}")

    raise ValueError("All source URLs failed. " + " | ".join(errors))