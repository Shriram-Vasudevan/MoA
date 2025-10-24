from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional


@dataclass
class Candidate:
    """Container for a single model sample."""

    prompt_id: str
    model_name: str
    sample_index: int
    text: str
    final_answer: str
    confidence: float
    is_correct: Optional[bool] = None
    metadata: Dict[str, str] = field(default_factory=dict)

    def short_label(self) -> str:
        return f"{self.model_name}#${self.sample_index}".replace("$", "")


class MockModel:
    """Deterministic mock model that simulates strong or weak proposers."""

    def __init__(
        self,
        name: str,
        strength: float,
        *,
        scripted_outcomes: Optional[Dict[str, List[bool]]] = None,
        scripted_final_answers: Optional[Dict[str, List[str]]] = None,
        seed: int = 13,
    ) -> None:
        if not 0.0 <= strength <= 1.0:
            raise ValueError("strength must be between 0 and 1")
        self.name = name
        self.strength = strength
        self.scripted_outcomes = scripted_outcomes or {}
        self.scripted_final_answers = scripted_final_answers or {}
        self.seed = seed

    def generate(
        self,
        *,
        prompt: Dict[str, str],
        sample_index: int,
        temperature: float = 0.7,
    ) -> Candidate:
        prompt_id = prompt["id"]
        gold_answer = prompt["answer"]
        distractors: Iterable[str] = prompt.get("distractors", [])

        final_answer = self._scripted_answer(prompt_id, sample_index)
        if final_answer is not None:
            correct = final_answer == gold_answer
        else:
            scripted = self._scripted_outcome(prompt_id, sample_index)
            if scripted is None:
                rng = random.Random(
                    f"{self.seed}:{self.name}:{prompt_id}:{sample_index}:{temperature}"
                )
                correct = rng.random() < self.strength
            else:
                correct = scripted
            if correct:
                final_answer = gold_answer
            else:
                rng = random.Random(
                    f"miss:{self.seed}:{self.name}:{prompt_id}:{sample_index}:{temperature}"
                )
                fallback_answers = list(distractors) or [str(int(gold_answer) + 1)]
                final_answer = rng.choice(fallback_answers)

        if final_answer is None:
            raise RuntimeError("final_answer could not be determined")

        if final_answer == gold_answer:
            confidence = 0.85 + 0.1 * (self.strength - 0.5)
            reasoning = self._build_correct_reasoning(prompt, final_answer)
            is_correct = True
        else:
            confidence = 0.35 + 0.2 * (self.strength - 0.5)
            reasoning = self._build_incorrect_reasoning(prompt, final_answer)
            is_correct = False

        text = f"{reasoning}\nFinal Answer: {final_answer}"
        return Candidate(
            prompt_id=prompt_id,
            model_name=self.name,
            sample_index=sample_index,
            text=text,
            final_answer=final_answer,
            confidence=max(0.0, min(confidence, 0.99)),
            is_correct=is_correct,
            metadata={"temperature": f"{temperature:.2f}"},
        )

    def _scripted_outcome(self, prompt_id: str, sample_index: int) -> Optional[bool]:
        outcomes = self.scripted_outcomes.get(prompt_id)
        if outcomes is None:
            return None
        if sample_index < len(outcomes):
            return outcomes[sample_index]
        return outcomes[-1]

    def _scripted_answer(self, prompt_id: str, sample_index: int) -> Optional[str]:
        answers = self.scripted_final_answers.get(prompt_id)
        if answers is None:
            return None
        if sample_index < len(answers):
            return answers[sample_index]
        return answers[-1]

    def _build_correct_reasoning(self, prompt: Dict[str, str], final_answer: str) -> str:
        return (
            f"Considering the question: {prompt['question']}\n"
            "Break it into steps, compute carefully, and verify the result.\n"
            f"Double-checking gives {final_answer}, which matches all constraints."
        )

    def _build_incorrect_reasoning(self, prompt: Dict[str, str], final_answer: str) -> str:
        return (
            f"Quick intuition on: {prompt['question']}\n"
            "A faster mental calculation suggests the answer is"
            f" {final_answer}, even if not every step is fully justified."
        )


__all__ = ["Candidate", "MockModel"]
