# Knowing isn't doing: research agents see the disproving evidence and move on

Shani Singh, Propab AI. October 2026.

**Paper:** [`paper.pdf`](paper.pdf) (LaTeX source: [`paper.tex`](paper.tex))

Language-model agents now carry out multi-hour data analyses, and on research benchmarks their answers are often
wrong. This study traces 104 failed outputs from 16 runs of two computational biology benchmarks (BixBench3 and
GeneBench-Pro), produced by three models, to the step in each transcript where the error entered, and replays 13 of
those steps with Claude Haiku 5.5 under eleven conditions.

- In 42 of the 58 failed GeneBench-Pro answer keys, the agent had itself printed a number that contradicted the answer
  it later gave.
- In five case studies, the fact that would have prevented the failure was stated correctly when the model was asked
  directly, outside the task.
- At the replayed steps, interventions that did not use knowledge of the answer (more reasoning effort, a generic
  reminder, a self-review prompt, five fresh-reader variants) did not raise the follow-up rate above the baseline
  interval. A note that only pointed to the relevant printed output raised it from 10 of 78 to 51 of 78 samples.

## Contents

```
paper.tex, paper.pdf        the paper
figures/                    every figure, as vector PDF and 300 dpi PNG
data/
  replay_outcomes.json      per-sample outcome (followed up: true/false) for every condition, failure point and
                            control point; six-turn forks; forks given an early list of checks
  failure_classification.csv  one row per failed output: benchmark, run, problem, graded item, primary cause under
                            each of two classification passes, contributing cause (GeneBench-Pro), cause status
  judge_agreement.json      agreement between the two model judges on a stratified sample of 132 turns
conditions/
  conditions.md             the exact text of every condition, reader prompt, pointer note and answer-informed note
  criteria.md               the follow-up criterion for each failure point, the control-point criterion, the judge prompt
scripts/
  stats.py                  recomputes every derived number in the paper (intervals, tests, shares, agreement)
  figures.py                draws every figure from data/
  check_numbers.py          checks every number in paper.tex against the released data
  paper_numbers.py          values the figures use that are not per-sample outcomes, each described in the paper
  build_pdf.sh              compiles paper.tex
```

## Reproduce

```bash
pip install -r requirements.txt
python scripts/stats.py
python scripts/figures.py
python scripts/check_numbers.py
TECTONIC=/path/to/tectonic bash scripts/build_pdf.sh
```

`check_numbers.py` exits non-zero if any number in the paper does not match the released data or a documented value.
The figures use Segoe UI where it is installed and fall back to Arial or DejaVu Sans.

## Not released

The benchmark run transcripts and the captured model requests that the replays start from. Both contain benchmark
inputs and outputs, and releasing them would expose benchmark answers. The released counts are sufficient to recompute
every result in the paper.

## Citation

```bibtex
@misc{singh2026knowing,
  title  = {Knowing isn't doing: research agents see the disproving evidence and move on},
  author = {Singh, Shani},
  year   = {2026},
  note   = {Propab AI},
  url    = {https://github.com/shani-singh1/knowing-isnt-doing}
}
```

## License

Code (`scripts/`) is released under the MIT License. The paper, figures, data and condition texts are released under
CC BY 4.0. See [`LICENSE`](LICENSE).

## Contact

shani@propabai.com
