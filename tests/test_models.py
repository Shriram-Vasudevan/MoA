from moa.models import MockModel


def test_scripted_final_answers_override_correctness():
    prompt = {"id": "p", "question": "q", "answer": "10", "distractors": ["5"]}
    model = MockModel(
        "Demo",
        strength=0.1,
        scripted_final_answers={"p": ["5", "10"]},
    )
    cand0 = model.generate(prompt=prompt, sample_index=0)
    cand1 = model.generate(prompt=prompt, sample_index=1)
    assert cand0.final_answer == "5"
    assert not cand0.is_correct
    assert cand1.final_answer == "10"
    assert cand1.is_correct
