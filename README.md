# Knowing isn't doing: why research agents look past their own evidence

Shani Singh, Propab AI. October 2026.

**Paper:** [`paper.pdf`](paper.pdf) (LaTeX source: [`paper.tex`](paper.tex))

This repository holds the paper and its failure-replay method and data. It is not a benchmark.

We traced 104 failed outputs from 43 runs of two computational biology benchmarks (BixBench3 and GeneBench-Pro), lasting
up to 37 hours, to the turn where each error entered, and replayed 13 of those turns with Claude Haiku 5.5 under controlled
changes, one change at a time.

- Most failures attributable to the agent were a default method applied without testing its assumption (58 to 60%) or an
  assumption checked only in aggregate (23 to 24%). In 42 of 58 failed GeneBench-Pro answers the agent had itself printed a
  number that contradicted its answer.
- Asked directly, the model that ran each of six tasks stated the fact that would have prevented the failure.
- In replay, a note stating the decisive question raised follow-up of the disproving evidence from 10 of 78 samples to 67 of
  78. A note naming only the disproving output gave 51 of 78. The same note naming another output of the same result gave 11.
  Every mechanism that lacked the answer, from maximum reasoning effort to fresh readers, gave 9 to 18.
- The bottleneck is choosing which of their own results to doubt. Making that choice without the answer is the open problem.

## Contents

```
paper.tex, paper.pdf          the paper
figures/                      every figure (vector PDF and 300 dpi PNG), the generated appendix tables (tab_*.tex) and
                              the Propab wordmark used on page 1 (vector PDF and SVG)
data/
  replay_outcomes.json        per-sample outcome (followed up: true/false) for every replay condition, failure point and
                              control point; six-turn forks; forks given an early list of checks; the carrier-point
                              sensitivity scoring with the note visible to the judge
  failure_classification.csv  one row per failed output: benchmark, run, problem, graded item, primary class, the
                              independent rater's class, the co-dominant alternative where the report names two causes,
                              contributing cause (GeneBench-Pro), cause status
  judge_agreement.json        agreement between the two model judges on a stratified sample of 132 turns
  reasoning_after_results.csv visible reasoning of every turn that read a tool result in 15 live Claude Haiku 5.5 runs
conditions/
  conditions.md               the exact text of every condition, pointer, reader prompt and knowledge probe
  criteria.md                 the follow-up criteria, the judge prompt, the sensitivity scoring and the rater's task
scripts/
  stats.py                    recomputes every derived number (intervals, paired tests, shares, agreement) and writes
                              the appendix test and sensitivity tables
  figures.py                  draws every figure from data/
  tables.py                   writes the per-point and cause-group appendix tables from data/
  check_numbers.py            checks every number in paper.tex against the released data or a documented value
  lint_prose.py               checks the body against the paper's writing rules
  paper_numbers.py            values the figures use that are not per-sample outcomes, each described in the paper
  build_pdf.sh                compiles paper.tex
```

## Reproduce

```bash
pip install -r requirements.txt
python scripts/stats.py
python scripts/tables.py
python scripts/figures.py
python scripts/check_numbers.py
TECTONIC=/path/to/tectonic bash scripts/build_pdf.sh
```

`check_numbers.py` exits non-zero if any number in the paper does not match the released data or a documented value.
The figures use Segoe UI where it is installed and fall back to Arial or DejaVu Sans.

## Not released

The benchmark run transcripts and the captured model requests that the replays start from. Both contain benchmark
inputs and outputs, and the benchmarks' answers. The released per-sample outcomes are sufficient to recompute every
result in the paper.

## Changes from the first version

The first version (commit 785ebf6) reported agreement between "two independent classification passes". The second
pass was not independent: it was the alternative reading of 16 failures whose reports name two causes of equal weight.
This version replaces it with an independent rating of all 104 failures by a separate model rater, blind to the primary
classification, and reports that agreement by benchmark. It also corrects an admixture value (0.81 to 0.82) and the
attribution of one printed table, removes a printed coefficient that equals a benchmark reference value, adds the
pointer-to-another-output and control-point conditions, and restructures the paper.

## Citation

```bibtex
@misc{singh2026knowing,
  title  = {Knowing isn't doing: why research agents look past their own evidence},
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
