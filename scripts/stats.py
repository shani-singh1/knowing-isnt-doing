"""Every derived number the paper quotes, recomputed from data/.

    python scripts/stats.py

Prints: follow-up rates per condition with bootstrap intervals that resample failure points; the implied selection
rate of each condition under the paper's Equation 1; exact per-point sign and sign-flip permutation tests; the share
of the answer-informed effect recovered by the pointer; the upper bound for zero rework events; classification
agreement and shares over failures and cause groups; the timing of the first disproving print; and the relabelling
test on the admixture table.
"""
import csv
import json
import sys
from collections import Counter
from itertools import product
from math import comb
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import paper_numbers as N  # noqa: E402

D = json.loads((ROOT / "data" / "replay_outcomes.json").read_text(encoding="utf-8"))
ST = D["single_turn"]
POINTS = [p["id"] for p in D["failure_points"]]
CONTROLS = D["control_points"]
CONDS = D["conditions"]
BASE, POINTER, ANSWER = "No note (baseline)", "Pointer to the output", "Answer-informed question"
BEST_READER = "Fresh reader: disagreements"
RNG = np.random.default_rng(20261020)
REPS = 20000
AGENT = ("default method used without a test", "assumption never checked per unit",
         "disproving number on screen, not acted on")


def k_of(c, pts=POINTS):
    return sum(sum(ST[c][p]) for p in pts), sum(len(ST[c][p]) for p in pts)


def interventions() -> None:
    K = {c: np.array([sum(ST[c][p]) for p in POINTS]) for c in CONDS}
    n = np.array([len(ST[BASE][p]) for p in POINTS])
    idx = RNG.integers(0, len(POINTS), size=(REPS, len(POINTS)))
    nn = n[idx].sum(1)
    b, u = K[BASE][idx].sum(1) / nn, K[ANSWER][idx].sum(1) / nn
    print("condition                        follow-up  rate   95% bootstrap     implied selection [95%]   rework")
    for c in CONDS:
        a = K[c][idx].sum(1) / nn
        lo, hi = np.percentile(a, [2.5, 97.5])
        line = f"{c:32s} {K[c].sum():3d}/{n.sum()}   {K[c].sum() / n.sum():.3f}  [{lo:.3f}, {hi:.3f}]"
        if c not in (BASE, ANSWER):
            s = (a - b) / (u - b)
            point = (K[c].sum() - K[BASE].sum()) / (K[ANSWER].sum() - K[BASE].sum())
            slo, shi = np.percentile(s, [2.5, 97.5])
            line += f"   {point:+.3f} [{slo:+.3f}, {shi:+.3f}]"
        else:
            line += " " * 28
        hk, hn = k_of(c, CONTROLS)
        print(line + f"   {hk}/{hn}")
    print("\npaired per-point tests")
    for c1, c2 in ((ANSWER, BEST_READER), (ANSWER, BASE), (BEST_READER, BASE), (POINTER, BASE),
                   (POINTER, BEST_READER), (ANSWER, POINTER)):
        paired(c1, c2)
    bb, pp, oo = (k_of(c)[0] for c in (BASE, POINTER, ANSWER))
    print(f"  share of the answer-informed increase recovered by the pointer: ({pp} - {bb}) / ({oo} - {bb}) = "
          f"{(pp - bb) / (oo - bb):.3f}")
    nh = 18
    print(f"  0/{nh} rework: two-sided 95% upper bound {1 - 0.025 ** (1 / nh):.3f}")


def paired(c1: str, c2: str) -> None:
    d = np.array([sum(ST[c1][p]) - sum(ST[c2][p]) for p in POINTS])
    pos, neg = int((d > 0).sum()), int((d < 0).sum())
    k, n = min(pos, neg), pos + neg
    p_sign = min(1.0, 2 * sum(comb(n, i) for i in range(k + 1)) / 2 ** n) if n else 1.0
    obs = abs(d.sum())
    hits = sum(abs((d * np.array(s)).sum()) >= obs for s in product((1, -1), repeat=len(d)))
    print(f"  {c1} vs {c2}: above at {pos}, below at {neg}, tied at {len(d) - n} of {len(d)} points; "
          f"sign test p = {p_sign:.5f}; sign-flip permutation p = {hits / 2 ** len(d):.5f}")


def cohen_kappa(a: list[str], b: list[str]) -> float:
    cats = sorted(set(a) | set(b))
    n = len(a)
    po = sum(x == y for x, y in zip(a, b)) / n
    pe = sum((a.count(c) / n) * (b.count(c) / n) for c in cats)
    return (po - pe) / (1 - pe)


def classification() -> None:
    rows = list(csv.DictReader(open(ROOT / "data" / "failure_classification.csv", encoding="utf-8")))
    a, b = [r["first_pass"] for r in rows], [r["second_pass"] for r in rows]
    agree = sum(x == y for x, y in zip(a, b))
    print(f"\nfailures {len(rows)} ({Counter(r['benchmark'] for r in rows)}); established "
          f"{sum(r['cause_status'] == 'established' for r in rows)}, probable {sum(r['cause_status'] == 'probable' for r in rows)}")
    print(f"agreement between passes {agree}/{len(rows)} = {agree / len(rows):.3f}; Cohen kappa {cohen_kappa(a, b):.3f}")
    print("disagreements:", dict(Counter((x, y) for x, y in zip(a, b) if x != y)))
    for name, lab in (("first pass", a), ("second pass", b)):
        c = Counter(lab)
        tot = sum(c[k] for k in AGENT)
        print(f"  {name}: share of {len(rows)}: " + "; ".join(f"{k} {v / len(rows):.3f}" for k, v in sorted(c.items())))
        print(f"  {name}: agent-attributable {tot}: " + "; ".join(f"{k} {c[k] / tot:.3f}" for k in AGENT))
    on = "disproving number on screen, not acted on"
    gb = [r for r in rows if r["benchmark"] == "GeneBench-Pro"]
    prim = sum(r["first_pass"] == on for r in gb)
    contrib = sum(r["first_pass"] != on and r["contributing_cause"] == on for r in gb)
    print(f"GeneBench-Pro keys with the disproving number printed: primary {prim}, contributing {contrib}, "
          f"total {prim + contrib} of {len(gb)} ({(prim + contrib) / len(gb):.3f})")
    groups = {}
    for r in rows:
        groups.setdefault((r["run"], r["problem"], r["first_pass"]), []).append(r)
    gc = Counter(k[2] for k in groups)
    gp = sum(gc[k] for k in AGENT)
    print(f"cause groups (same run, same problem, same primary class): {len(groups)}; agent-attributable {gp}: "
          + "; ".join(f"{k} {gc[k]}/{gp} = {gc[k] / gp:.3f}" for k in AGENT))


def timing_and_relabel() -> None:
    gaps = [(s - ev[0]) / s for _, s, ev, _ in N.RASTER]
    print(f"\nshare of steps after the first disproving print: median {np.median(gaps):.2f}, "
          f"range {min(gaps):.2f} to {max(gaps):.2f} ({len(gaps)} runs)")
    h1, h2 = np.array(N.POPGEN["h1"]), np.array(N.POPGEN["h2"])
    print(f"admixture table: summed SD across chromosomes {h1.std(ddof=1) + h2.std(ddof=1):.3f}")
    for k in range(4):
        g1, g2 = h1.copy(), h2.copy()
        g1[k], g2[k] = 1 - g1[k], 1 - g2[k]
        print(f"  relabel chromosome {k + 1}: summed SD {g1.std(ddof=1) + g2.std(ddof=1):.3f}")


if __name__ == "__main__":
    interventions()
    classification()
    timing_and_relabel()
