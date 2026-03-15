from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence, TypeVar


T = TypeVar("T")


@dataclass(frozen=True)
class PathSimBreakdown:
    node_similarity: float
    edge_similarity: float
    sequence_similarity: float
    total_score: float


def jaccard_similarity(items_a: Iterable[T], items_b: Iterable[T]) -> float:
    set_a = set(items_a)
    set_b = set(items_b)

    if not set_a and not set_b:
        return 1.0

    union = set_a.union(set_b)
    if not union:
        return 1.0

    return len(set_a.intersection(set_b)) / len(union)


def path_to_edges(path: Sequence[T]) -> list[tuple[T, T]]:
    return [(path[index], path[index + 1]) for index in range(len(path) - 1)]


def normalized_levenshtein_similarity(path_a: Sequence[T], path_b: Sequence[T]) -> float:
    if not path_a and not path_b:
        return 1.0

    rows = len(path_a) + 1
    cols = len(path_b) + 1
    distance = [[0] * cols for _ in range(rows)]

    for row in range(rows):
        distance[row][0] = row
    for col in range(cols):
        distance[0][col] = col

    for row in range(1, rows):
        for col in range(1, cols):
            substitution_cost = 0 if path_a[row - 1] == path_b[col - 1] else 1
            distance[row][col] = min(
                distance[row - 1][col] + 1,
                distance[row][col - 1] + 1,
                distance[row - 1][col - 1] + substitution_cost,
            )

    max_length = max(len(path_a), len(path_b))
    if max_length == 0:
        return 1.0

    return 1.0 - (distance[-1][-1] / max_length)


def compute_pathsim(
    generated_path: Sequence[T],
    ideal_path: Sequence[T],
    *,
    node_weight: float = 0.4,
    edge_weight: float = 0.3,
    sequence_weight: float = 0.3,
) -> PathSimBreakdown:
    total_weight = node_weight + edge_weight + sequence_weight
    if total_weight <= 0:
        raise ValueError("PathSim weights must sum to a positive value")

    normalized_node_weight = node_weight / total_weight
    normalized_edge_weight = edge_weight / total_weight
    normalized_sequence_weight = sequence_weight / total_weight

    node_similarity = jaccard_similarity(generated_path, ideal_path)
    edge_similarity = jaccard_similarity(path_to_edges(generated_path), path_to_edges(ideal_path))
    sequence_similarity = normalized_levenshtein_similarity(generated_path, ideal_path)

    total_score = (
        normalized_node_weight * node_similarity
        + normalized_edge_weight * edge_similarity
        + normalized_sequence_weight * sequence_similarity
    )

    return PathSimBreakdown(
        node_similarity=node_similarity,
        edge_similarity=edge_similarity,
        sequence_similarity=sequence_similarity,
        total_score=total_score,
    )


def best_pathsim(
    generated_paths: Sequence[Sequence[T]],
    ideal_path: Sequence[T],
    **weights: float,
) -> tuple[int, PathSimBreakdown] | None:
    best_result: tuple[int, PathSimBreakdown] | None = None

    for index, generated_path in enumerate(generated_paths):
        breakdown = compute_pathsim(generated_path, ideal_path, **weights)
        if best_result is None or breakdown.total_score > best_result[1].total_score:
            best_result = (index, breakdown)

    return best_result