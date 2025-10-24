from moa.aggregation import aggregate_flat, aggregate_sequential
from moa.models import Candidate


def make_candidate(prompt_id: str, model_name: str, sample_index: int, answer: str, confidence: float):
    return Candidate(
        prompt_id=prompt_id,
        model_name=model_name,
        sample_index=sample_index,
        text=f"Answer {answer}",
        final_answer=answer,
        confidence=confidence,
    )


def test_flat_majority_prefers_highest_vote():
    candidates = [
        make_candidate("p", "A", 0, "42", 0.9),
        make_candidate("p", "B", 1, "42", 0.6),
        make_candidate("p", "C", 2, "13", 0.95),
    ]
    result = aggregate_flat(candidates, strategy_name="test")
    assert result.final_answer == "42"
    assert result.supporting_models == ["A#0", "B#1"]


def test_sequential_counts_votes_across_windows():
    candidates = [
        make_candidate("p", "A", 0, "7", 0.5),
        make_candidate("p", "B", 1, "7", 0.5),
        make_candidate("p", "C", 2, "9", 0.6),
        make_candidate("p", "D", 3, "7", 0.4),
    ]
    result = aggregate_sequential(candidates, window_size=2, strategy_name="seq")
    assert result.final_answer == "7"
    assert result.vote_counts["7"] == 3
    assert "A#0" in result.supporting_models
