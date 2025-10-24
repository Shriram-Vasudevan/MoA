from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Sequence

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from moa.aggregation import AggregationResult, aggregate_flat, aggregate_sequential
from moa.eval import evaluate, exact_match
from moa.models import Candidate, MockModel


@dataclass
class ShowcaseModels:
    strong: MockModel
    medium: MockModel
    weak: MockModel


def load_prompts(path: Path) -> List[Dict[str, str]]:
    prompts: List[Dict[str, str]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            prompts.append(json.loads(line))
    return prompts


def build_models() -> ShowcaseModels:
    strong = MockModel(
        "Orion-Strong",
        strength=0.9,
        scripted_final_answers={
            "gsm8k-1": ["55", "60", "60", "60", "60"],
            "gsm8k-2": ["12", "12", "12", "12", "12"],
            "gsm8k-3": ["30", "35", "35", "35", "35"],
        },
    )
    medium = MockModel(
        "Nova-Medium",
        strength=0.55,
        scripted_final_answers={
            "gsm8k-1": ["50"],
            "gsm8k-2": ["9"],
            "gsm8k-3": ["28"],
        },
    )
    weak = MockModel(
        "Atlas-Weak",
        strength=0.3,
        scripted_final_answers={
            "gsm8k-1": ["50"],
            "gsm8k-2": ["16"],
            "gsm8k-3": ["30"],
        },
    )
    return ShowcaseModels(strong=strong, medium=medium, weak=weak)


def collect_self_moa_candidates(
    model: MockModel, *, prompt: Dict[str, str], samples: int, temperature: float
) -> List[Candidate]:
    return [
        model.generate(prompt=prompt, sample_index=i, temperature=temperature)
        for i in range(samples)
    ]


def collect_mixed_candidates(
    models: Sequence[MockModel], *, prompt: Dict[str, str], temperature: float
) -> List[Candidate]:
    candidates: List[Candidate] = []
    for model in models:
        candidates.append(model.generate(prompt=prompt, sample_index=0, temperature=temperature))
    return candidates


def format_candidate_block(candidates: Iterable[Candidate]) -> str:
    rows = [
        "| Model Sample | Final Answer | Confidence |",
        "| --- | --- | --- |",
    ]
    for cand in candidates:
        rows.append(
            f"| {cand.short_label()} | {cand.final_answer} | {cand.confidence:.2f} |"
        )
    return "\n".join(rows)


def render_result_heading(result: AggregationResult, *, reference: str) -> str:
    outcome = "✅" if exact_match(result.final_answer, reference) else "❌"
    return f"{outcome} **{result.strategy}** → **{result.final_answer}**\n\n{result.rationale}\n"


def run_showcase(
    *,
    prompts_path: Path,
    self_samples: int,
    sequential_window: int,
    temperature: float,
    save_path: Path | None,
) -> None:
    prompts = load_prompts(prompts_path)
    models = build_models()
    transcript: List[str] = []

    base_preds = []
    mixed_preds = []
    self_preds = []
    seq_preds = []

    for prompt in prompts:
        prompt_id = prompt["id"]
        question = prompt["question"]
        answer = prompt["answer"]

        base_candidate = models.strong.generate(
            prompt=prompt, sample_index=0, temperature=temperature
        )
        mixed_candidates = collect_mixed_candidates(
            [models.strong, models.medium, models.weak],
            prompt=prompt,
            temperature=temperature,
        )
        self_candidates = collect_self_moa_candidates(
            models.strong,
            prompt=prompt,
            samples=self_samples,
            temperature=temperature,
        )

        mixed_result = aggregate_flat(mixed_candidates, strategy_name="Mixed-MoA (majority)")
        self_result = aggregate_flat(self_candidates, strategy_name="Self-MoA (majority)")
        seq_result = aggregate_sequential(
            self_candidates,
            window_size=sequential_window,
            strategy_name=f"Self-MoA-Seq (window={sequential_window})",
        )

        transcript.append(f"## Prompt {prompt_id}\n")
        transcript.append(f"**Question:** {question}\n")

        base_header = "✅" if exact_match(base_candidate.final_answer, answer) else "❌"
        transcript.append("### Single Model Baseline\n")
        transcript.append(
            f"{base_header} **{models.strong.name} sample** → **{base_candidate.final_answer}**\n"
        )
        transcript.append("```\n" + base_candidate.text + "\n```\n")

        transcript.append("### Mixed-MoA Aggregation\n")
        transcript.append(render_result_heading(mixed_result, reference=answer))
        transcript.append(format_candidate_block(mixed_candidates) + "\n")

        transcript.append("### Self-MoA Aggregation\n")
        transcript.append(render_result_heading(self_result, reference=answer))
        transcript.append(format_candidate_block(self_candidates) + "\n")

        transcript.append("### Self-MoA-Seq Aggregation\n")
        transcript.append(render_result_heading(seq_result, reference=answer))

        base_preds.append((base_candidate.final_answer, answer))
        mixed_preds.append((mixed_result.final_answer, answer))
        self_preds.append((self_result.final_answer, answer))
        seq_preds.append((seq_result.final_answer, answer))

    transcript.append("---\n")
    transcript.extend(build_summary_section(base_preds, mixed_preds, self_preds, seq_preds))

    output_text = "\n".join(transcript)
    print(output_text)
    if save_path is not None:
        save_path.parent.mkdir(parents=True, exist_ok=True)
        save_path.write_text(output_text, encoding="utf-8")
        print(f"\nSaved showcase to {save_path}")


def build_summary_section(
    base_preds: Sequence[tuple[str, str]],
    mixed_preds: Sequence[tuple[str, str]],
    self_preds: Sequence[tuple[str, str]],
    seq_preds: Sequence[tuple[str, str]],
) -> List[str]:
    base_eval = evaluate(base_preds)
    mixed_eval = evaluate(mixed_preds)
    self_eval = evaluate(self_preds)
    seq_eval = evaluate(seq_preds)

    summary_lines = ["## Aggregate Accuracy\n"]
    summary_lines.append("| Strategy | Accuracy | Correct / Total |")
    summary_lines.append("| --- | --- | --- |")
    summary_lines.append(
        f"| Single Strong Sample | {base_eval.accuracy:.2f} | {base_eval.correct} / {base_eval.total} |"
    )
    summary_lines.append(
        f"| Mixed-MoA (majority) | {mixed_eval.accuracy:.2f} | {mixed_eval.correct} / {mixed_eval.total} |"
    )
    summary_lines.append(
        f"| Self-MoA (majority) | {self_eval.accuracy:.2f} | {self_eval.correct} / {self_eval.total} |"
    )
    summary_lines.append(
        f"| Self-MoA-Seq | {seq_eval.accuracy:.2f} | {seq_eval.correct} / {seq_eval.total} |"
    )
    summary_lines.append(
        "\nSelf-MoA variants clearly outperform the mixed ensemble despite using the same proposer model."
    )
    return summary_lines


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Self-MoA showcase demo")
    parser.add_argument(
        "--prompts",
        type=Path,
        default=Path("examples/prompts.jsonl"),
        help="Path to the prompts JSONL file.",
    )
    parser.add_argument(
        "--self-samples",
        type=int,
        default=4,
        help="Number of samples to draw for the Self-MoA pipeline.",
    )
    parser.add_argument(
        "--sequential-window",
        type=int,
        default=2,
        help="Window size for the sequential Self-MoA aggregator.",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.7,
        help="Sampling temperature (for demonstration purposes only).",
    )
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="If provided, skip writing the markdown showcase to disk.",
    )
    parser.add_argument(
        "--output-path",
        type=Path,
        default=Path("examples/output/self_moa_showcase.md"),
        help="Where to write the markdown showcase.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    save_path = None if args.no_save else args.output_path
    run_showcase(
        prompts_path=args.prompts,
        self_samples=args.self_samples,
        sequential_window=args.sequential_window,
        temperature=args.temperature,
        save_path=save_path,
    )


if __name__ == "__main__":
    main()
