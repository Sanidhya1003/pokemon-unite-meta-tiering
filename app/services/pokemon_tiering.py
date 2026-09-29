import numpy as np


TIER_NAMES = ["S", "A", "B", "C", "D", "E", "F"]


def _segment_sse(values: np.ndarray, start: int, end: int) -> float:
    """
    Calculate within-group squared error for values[start:end].
    This helps find natural breaks in the score distribution.
    """

    group = values[start:end]

    if len(group) == 0:
        return 0.0

    mean = np.mean(group)
    return float(np.sum((group - mean) ** 2))


def _natural_breaks_labels(scores: list[float], n_classes: int) -> list[int]:
    """
    Fisher-Jenks style natural breaks for 1D score tiering.

    Important:
    - Uses ONLY meta_score.
    - Keeps all Pokémon.
    - Creates contiguous score bands.
    - Label 0 = lowest score group.
    - Label n_classes - 1 = highest score group.
    """

    n = len(scores)

    if n_classes < 2:
        raise ValueError("Number of tiers must be at least 2.")

    if n_classes > n:
        raise ValueError("Number of tiers cannot be greater than number of Pokémon.")

    sorted_indices = np.argsort(scores)
    sorted_scores = np.array(scores, dtype=float)[sorted_indices]

    dp = np.full((n_classes + 1, n + 1), np.inf)
    split = np.zeros((n_classes + 1, n + 1), dtype=int)

    dp[0][0] = 0.0

    for class_count in range(1, n_classes + 1):
        for end in range(class_count, n + 1):
            for start in range(class_count - 1, end):
                cost = dp[class_count - 1][start] + _segment_sse(
                    sorted_scores,
                    start,
                    end,
                )

                if cost < dp[class_count][end]:
                    dp[class_count][end] = cost
                    split[class_count][end] = start

    labels_sorted = np.zeros(n, dtype=int)

    end = n

    for class_count in range(n_classes, 0, -1):
        start = split[class_count][end]
        labels_sorted[start:end] = class_count - 1
        end = start

    labels = np.zeros(n, dtype=int)
    labels[sorted_indices] = labels_sorted

    return labels.tolist()


def generate_pokemon_tiers(meta_entries: list, n_clusters: int = 5) -> list[dict]:
    """
    Generate Pokémon tiers using ONLY meta_score.

    meta_score = win_rate * pick_rate

    This guarantees:
    S has the highest score band,
    then A,
    then B,
    then C,
    then D,
    etc.
    """

    if not meta_entries:
        raise ValueError("No Pokémon meta entries found.")

    if n_clusters < 2:
        raise ValueError("Number of tiers must be at least 2.")

    if n_clusters > len(meta_entries):
        raise ValueError("Number of tiers cannot be greater than number of Pokémon.")

    if n_clusters > len(TIER_NAMES):
        raise ValueError(f"Maximum supported tiers is {len(TIER_NAMES)}.")

    scores = [float(entry.meta_score) for entry in meta_entries]

    labels = _natural_breaks_labels(
        scores=scores,
        n_classes=n_clusters,
    )

    tier_results = []

    for entry, label in zip(meta_entries, labels):
        # Natural breaks labels are ascending:
        # 0 = lowest score group
        # n_clusters - 1 = highest score group
        tier_index = n_clusters - 1 - int(label)
        tier_name = TIER_NAMES[tier_index]

        tier_results.append(
            {
                "snapshot_id": entry.snapshot_id,
                "pokemon_name": entry.pokemon_name,
                "cluster_label": int(label),
                "tier": tier_name,
                "score": float(entry.meta_score),
                "win_rate": float(entry.win_rate),
                "pick_rate": float(entry.pick_rate),
                "ban_rate": float(entry.ban_rate),
            }
        )

    tier_results = sorted(
        tier_results,
        key=lambda item: (
            TIER_NAMES.index(item["tier"]),
            -item["score"],
        ),
    )

    return tier_results