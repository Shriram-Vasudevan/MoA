# MoA

This repository provides a lightweight, reproducible demonstration of the ideas
from the *Mixture-of-Agents* paper, focusing on why **Self-MoA** often beats a
mixed ensemble of weaker models.

## Project Layout

```
moa/                  # Core utilities: mock models, aggregation, evaluation
examples/             # Ready-to-run demos and prompt data
└── self_moa_showcase.py
                     # Main showcase script that prints and saves a markdown report
└── prompts.jsonl     # Tiny GSM8K-inspired prompt set with gold answers
└── output/           # Generated showcase artifacts (written at runtime)
tests/                # Unit tests covering the deterministic pipeline
```

All code relies only on the Python standard library, so you can run the demo on
any machine with Python ≥ 3.10 without downloading heavyweight language models.

## Quickstart

1. **Create a virtual environment (optional but recommended).**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. **Run the showcase.**
   ```bash
   python examples/self_moa_showcase.py
   ```

   The script prints a detailed markdown report to the console and writes the
   same content to `examples/output/self_moa_showcase.md`. Each prompt includes:

   * The single-sample baseline from the strong proposer model.
   * The Mixed-MoA aggregation (strong + two weaker models) showing how noisy
     votes can derail the majority.
   * The Self-MoA aggregation (multiple samples from the strong proposer) that
     reliably surfaces the correct answer.
   * The sequential Self-MoA-Seq variant, illustrating sliding-window
     aggregation without exploding context.

3. **Inspect the generated artifact.** Drop the markdown file into any markdown
   viewer or slide deck to showcase the results visually.

## Expected Output

Running the showcase on the bundled prompts yields the following aggregate
accuracy table:

| Strategy | Accuracy | Correct / Total |
| --- | --- | --- |
| Single Strong Sample | 0.33 | 1 / 3 |
| Mixed-MoA (majority) | 0.33 | 1 / 3 |
| Self-MoA (majority) | 1.00 | 3 / 3 |
| Self-MoA-Seq | 1.00 | 3 / 3 |

In addition to the summary, the markdown transcript explains (with vote counts)
why the Self-MoA strategies succeed on each prompt.

## Running Tests

The repository includes lightweight unit tests to ensure the deterministic
behaviour of the mock models and aggregation logic:

```bash
python -m pytest
```

## Adapting the Demo

* Swap in your own prompts by editing `examples/prompts.jsonl`.
* Change the number of Self-MoA samples or the sequential window via CLI flags,
  e.g. `python examples/self_moa_showcase.py --self-samples 6 --sequential-window 3`.
* Replace the mock models with real model calls by implementing a wrapper that
  returns `Candidate` objects— the rest of the pipeline (aggregation, evaluation,
  reporting) stays the same.
