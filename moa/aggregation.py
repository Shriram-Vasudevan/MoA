from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Iterable, List, Sequence

from .models import Candidate


@dataclass
class AggregationResult:
    prompt_id: str
    strategy: str
    final_answer: str
    supporting_models: List[str]
    vote_counts: Counter
    rationale: str

    @property
    def support_size(self) -> int:
        return sum(self.vote_counts.values())


def extract_final_answer(candidate: Candidate) -> str:
    return candidate.final_answer.strip()


def aggregate_flat(candidates: Sequence[Candidate], *, strategy_name: str) -> AggregationResult:
    if not candidates:
        raise ValueError("aggregate_flat requires at least one candidate")

    votes = Counter()
    label_map = {}
    for cand in candidates:
        answer = extract_final_answer(cand)
        votes[answer] += 1
        label_map.setdefault(answer, []).append(cand)

    best_answer, best_count = votes.most_common(1)[0]
    supporting = label_map[best_answer]
    supporting = sorted(
        supporting,
        key=lambda c: (c.confidence, -c.sample_index),
        reverse=True,
    )
    rationale = _build_rationale(strategy_name, best_answer, votes, supporting)
    return AggregationResult(
        prompt_id=candidates[0].prompt_id,
        strategy=strategy_name,
        final_answer=best_answer,
        supporting_models=[cand.short_label() for cand in supporting],
        vote_counts=votes,
        rationale=rationale,
    )


def aggregate_sequential(
    candidates: Sequence[Candidate],
    *,
    window_size: int,
    strategy_name: str,
) -> AggregationResult:
    if not candidates:
        raise ValueError("aggregate_sequential requires candidates")
    if window_size <= 0:
        raise ValueError("window_size must be positive")

    votes = Counter()
    order = list(sorted(candidates, key=lambda c: c.sample_index))
    windows = [order[i : i + window_size] for i in range(0, len(order), window_size)]

    for window in windows:
        local = Counter(extract_final_answer(c) for c in window)
        votes.update(local)

    best_answer, best_count = votes.most_common(1)[0]
    supporting = [
        cand
        for cand in order
        if extract_final_answer(cand) == best_answer
    ]
    supporting = sorted(
        supporting,
        key=lambda c: (c.confidence, -c.sample_index),
        reverse=True,
    )
    rationale = _build_rationale(
        strategy_name,
        best_answer,
        votes,
        supporting,
        windows=len(windows),
        window_size=window_size,
    )
    return AggregationResult(
        prompt_id=candidates[0].prompt_id,
        strategy=strategy_name,
        final_answer=best_answer,
        supporting_models=[cand.short_label() for cand in supporting],
        vote_counts=votes,
        rationale=rationale,
    )


def _build_rationale(
    strategy_name: str,
    best_answer: str,
    votes: Counter,
    supporting: Sequence[Candidate],
    *,
    windows: int | None = None,
    window_size: int | None = None,
) -> str:
    vote_descriptions = ", ".join(
        f"{answer}: {count}" for answer, count in sorted(votes.items(), key=lambda x: -x[1])
    )
    supporters = ", ".join(c.short_label() for c in supporting)
    base = (
        f"{strategy_name} selected '{best_answer}' with vote distribution [{vote_descriptions}]."
        f" Supporting samples: {supporters}."
    )
    if windows is not None and window_size is not None:
        base += f" Processed in {windows} sliding windows of size {window_size}."
    return base


__all__ = [
    "AggregationResult",
    "aggregate_flat",
    "aggregate_sequential",
    "extract_final_answer",
]
