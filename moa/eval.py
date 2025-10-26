from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List


@dataclass
class EvaluationResult:
    total: int
    correct: int

    @property
    def accuracy(self) -> float:
        if self.total == 0:
            return 0.0
        return self.correct / self.total


def normalize_answer(answer: str) -> str:
    return answer.strip().lower()


def exact_match(prediction: str, reference: str) -> bool:
    return normalize_answer(prediction) == normalize_answer(reference)


def evaluate(predictions: Iterable[tuple[str, str]]) -> EvaluationResult:
    total = 0
    correct = 0
    for pred, ref in predictions:
        total += 1
        correct += int(exact_match(pred, ref))
    return EvaluationResult(total=total, correct=correct)


__all__ = ["EvaluationResult", "evaluate", "exact_match", "normalize_answer"]
