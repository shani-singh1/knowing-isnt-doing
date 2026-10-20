"""Check every number in paper.tex against values computed from data/ or recorded in scripts/paper_numbers.py.

    python scripts/check_numbers.py

Each number in the body (bibliography excluded) must match an entry in a registry. Entries are computed here from the
released files, or listed in RECORDED with the record they come from (values printed by the agents, probe counts,
study constants). Prints every number with its source and exits non-zero if any number is unmatched.
"""
import csv
import json
import re
import sys
from collections import Counter
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import paper_numbers as N  # noqa: E402
from stats import cohen_kappa  # noqa: E402

REG: dict[str, str] = {}


def add(value, source):
    forms = {value} if isinstance(value, str) else set()
    if not isinstance(value, str):
        if float(value).is_integer():
            forms.add(str(int(value)))
        forms |= {f"{value:.{d}f}" for d in (1, 2, 3, 4)}
    for f in forms:
        REG.setdefault(f, source)


# ── replay outcomes ─────────────────────────────────────────────────────────────────────────────────
D = json.loads((ROOT / "data" / "replay_outcomes.json").read_text(encoding="utf-8"))
ST = D["single_turn"]
PTS = [p["id"] for p in D["failure_points"]]
CTL = D["control_points"]
add(len(PTS), "failure points")
add(len(CTL), "control points")
add(len(D["conditions"]), "conditions")
for c in D["conditions"]:
    k, n = sum(sum(ST[c][p]) for p in PTS), sum(len(ST[c][p]) for p in PTS)
    add(k, f"follow-ups: {c}")
    add(n, "samples per condition")
    add(round(100 * k / n), f"percent follow-up: {c}")
    for p in PTS:
        add(sum(ST[c][p]), f"per-point count: {c} / {p}")
        add(len(ST[c][p]), "samples per point")
    hk, hn = sum(sum(ST[c][q]) for q in CTL), sum(len(ST[c][q]) for q in CTL)
    add(hk, f"rework: {c}")
    add(hn, "control samples per condition")
B, P, A, R = "No note (baseline)", "Pointer to the output", "Answer-informed question", "Fresh reader: disagreements"
kb, kp, ka, kr = (sum(sum(ST[c][p]) for p in PTS) for c in (B, P, A, R))
add(kp - kb, "pointer increase over baseline (samples)")
add(ka - kb, "answer-informed increase over baseline (samples)")
add(round(100 * (kp - kb) / (ka - kb)), "share of the increase recovered by the pointer (%)")
add(round(ka / 78, 2), "uptake estimate under Equation 1")
add(round((kr - kb) / (ka - kb), 2), "best reader implied selection under Equation 1")
add(round(100 * (1 - 0.025 ** (1 / 18))), "two-sided 95% upper bound for 0 of 18 (%)")
for c1, c2 in ((R, B), (P, B), (P, R), (A, P)):
    d = [sum(ST[c1][p]) - sum(ST[c2][p]) for p in PTS]
    add(sum(x > 0 for x in d), f"{c1} above {c2} (points)")
    add(sum(x < 0 for x in d), f"{c1} below {c2} (points)")
    add(sum(x == 0 for x in d), f"{c1} tied with {c2} (points)")
for v, s in ((0.22, "sign test, reader vs baseline"), (0.0005, "sign and permutation tests, pointer vs baseline"),
             (0.02, "sign test, pointer vs reader"), (0.006, "permutation test, pointer vs reader"),
             (0.07, "sign test, answer-informed vs pointer"), (0.13, "permutation test, answer-informed vs pointer")):
    add(v, s + " (scripts/stats.py)")
for arm, per in D["multi_turn"].items():
    add(sum(sum(v) for v in per.values()), f"six-turn forks following up: {arm}")
    add(sum(len(v) for v in per.values()), f"six-turn forks: {arm}")
add(len(D["multi_turn"][B]), "six-turn points")
E = D["early_list"]
for arm in (B, "Given a list of checks"):
    add(sum(sum(v) for v in E[arm].values()), f"early forks following up: {arm}")
    add(sum(len(v) for v in E[arm].values()), f"early forks: {arm}")
add(len(E["problems"]), "early-fork problems")
add(sum(q["list_named_decisive_check"] for q in E["problems"]), "problems where the list named the check")

# ── classification ──────────────────────────────────────────────────────────────────────────────────
rows = list(csv.DictReader(open(ROOT / "data" / "failure_classification.csv", encoding="utf-8")))
a, b = [r["first_pass"] for r in rows], [r["second_pass"] for r in rows]
add(len(rows), "failed outputs")
for bench, n in Counter(r["benchmark"] for r in rows).items():
    add(n, f"failed outputs: {bench}")
add(sum(x == y for x, y in zip(a, b)), "classification agreement (failures)")
add(sum(x != y for x, y in zip(a, b)), "classification disagreements")
add(round(100 * sum(x == y for x, y in zip(a, b)) / len(rows)), "classification agreement (%)")
add(round(cohen_kappa(a, b), 2), "classification kappa")
for (x, y), n in Counter((x, y) for x, y in zip(a, b) if x != y).items():
    add(n, f"disagreements {x} / {y}")
add(sum(r["cause_status"] == "established" for r in rows), "established causes")
add(sum(r["cause_status"] == "probable" for r in rows), "probable causes")
AG = ("default method used without a test", "assumption never checked per unit",
      "disproving number on screen, not acted on")
for lab in (a, b):
    c = Counter(lab)
    tot = sum(c[k] for k in AG)
    add(tot, "agent-attributable failures")
    for k in AG:
        add(round(100 * c[k] / tot), f"agent-attributable share: {k}")
    for k, v in c.items():
        add(round(100 * v / len(rows)), f"share of all failures: {k}")
groups = {(r["run"], r["problem"], r["first_pass"]) for r in rows}
add(len(groups), "cause groups")
gc = Counter(g[2] for g in groups)
gp = sum(gc[k] for k in AG)
add(gp, "agent-attributable cause groups")
for k in AG:
    add(round(100 * gc[k] / gp), f"cause-group share: {k}")
on = "disproving number on screen, not acted on"
gb = [r for r in rows if r["benchmark"] == "GeneBench-Pro"]
n_p = sum(r["first_pass"] == on for r in gb)
n_c = sum(r["first_pass"] != on and r["contributing_cause"] == on for r in gb)
add(n_p + n_c, "GeneBench-Pro keys with the disproving number printed")
add(round(100 * (n_p + n_c) / len(gb)), "GeneBench-Pro keys with the disproving number printed (%)")

# ── judge agreement ─────────────────────────────────────────────────────────────────────────────────
J = json.loads((ROOT / "data" / "judge_agreement.json").read_text(encoding="utf-8"))
add(J["n_turns"], "re-scored turns")
add(J["agreements"], "judge agreements")
add(J["percent_agreement"], "judge agreement (%)")
add(round(J["cohen_kappa"], 2), "judge kappa")
add(J["first_judge_follow_ups"], "first judge follow-ups")
add(J["second_judge_follow_ups"], "second judge follow-ups")
add(J["answer_informed_turns_agreement"][0], "agreement on answer-informed turns")
add(J["answer_informed_turns_agreement"][1], "turns per condition in the agreement sample")

# ── timing and relabelling ──────────────────────────────────────────────────────────────────────────
gaps = [(s - ev[0]) / s for _, s, ev, _ in N.RASTER]
add(len(N.RASTER), "runs in the timing figure")
add(round(100 * float(np.median(gaps))), "median share of steps ahead (%)")
add(round(100 * min(gaps)), "minimum share of steps ahead (%)")
add(round(100 * max(gaps)), "maximum share of steps ahead (%)")
h1, h2 = np.array(N.POPGEN["h1"]), np.array(N.POPGEN["h2"])
add(round(h1.std(ddof=1) + h2.std(ddof=1), 3), "summed SD before relabelling")
others = []
for k in range(4):
    g1, g2 = h1.copy(), h2.copy()
    g1[k], g2[k] = 1 - g1[k], 1 - g2[k]
    v = round(g1.std(ddof=1) + g2.std(ddof=1), 3)
    if k == 2:
        add(v, "summed SD after relabelling chromosome 3")
    else:
        others.append(v)
add(round(min(others), 2), "smallest summed SD among the other relabellings")
for v in list(h1) + list(h2):
    add(v, "per-chromosome fraction printed by the agent")

# ── recorded values: printed by the agents, probe counts, study constants ───────────────────────────
RECORDED = {
    "0.2337": "carrier, printed by the agent", "0.1553": "carrier, reported estimate", "0.236": "carrier trial 3, printed",
    "0.119": "carrier trial 3, chosen", "0.117": "carrier trial 3, reported span", "0.146": "carrier trial 3, reported span",
    "0.427": "treatment effect, printed variant", "0.466": "treatment effect, headline", "0.37": "structural, printed variant",
    "0.29": "structural, primary estimate", "121": "structural, printed count", "0.992": "CRISPRi, printed R2",
    "0.048": "CRISPRi, printed coefficient", "0.968": "CRISPRi, printed R2", "0.158": "CRISPRi, printed coefficient",
    "0.014": "Mendelian randomization, printed permutation p", "6,733": "Mendelian randomization, printed Q",
    "40": "Mendelian randomization, printed degrees of freedom", "0.48": "admixture, printed fraction (trial 2)",
    "8": "chromatin contacts, block pixels among the top", "11": "chromatin contacts, top case pixels",
    "0.08": "single-cell, printed minimum", "0.24": "single-cell, printed minimum", "587": "read counting, printed",
    "5,126": "read counting, loci", "170": "Gene Ontology, printed", "250": "Gene Ontology, genes",
    "0.62": "single-cell, printed variant", "0.55": "single-cell, printed variant", "28": "load series, gap rows",
    "761": "median reasoning characters at high", "1,579": "median reasoning characters at maximum",
    "30": "first replies per effort level", "24": "first replies splitting at maximum",
    "17": "first replies splitting with the encouraging sentence", "15": "forks per effort schedule",
    "12": "forks correct at maximum throughout", "5": "probes / live survey runs / forks correct at extra-high",
    "3": "samples per probe / plans per wording", "4": "kinetics runs", "1.3": "rate ratio, asked directly",
    "1.7": "rate ratio, asked directly", "87": "kinetics jump", "0.15": "reads per fragment, asked directly",
    "1,000": "plan prediction", "20,000": "plan prediction / bootstrap draws", "100": "plan prediction",
    "3,594": "agent result, task 1", "6,904": "agent result, task 1", "85": "plan output shape",
    "1,144": "plan output shape", "1,605": "peaks per replicate", "1,747": "peaks per replicate",
    "64,000": "output limit at maximum effort", "0.8": "BixBench3 failure threshold", "20": "BixBench3 tasks",
    "16": "benchmark runs", "37": "longest run, hours", "9": "first replies splitting at high / failure points",
    "10": "GeneBench-Pro problems / probe samples", "7": "load-series shift, hours", "2": "DeepSeek trials",
    "1": "one run / one tie", "0": "zero counts", "6": "samples per point / per-point count",
    "0.86": "uptake estimate under Equation 1", "0.14": "best reader implied selection under Equation 1",
}
for k, v in RECORDED.items():
    REG.setdefault(k, v)
STRUCTURE = {"4.1": "model version", "5.5": "model version", "6": "model version", "6.1": "model version",
             "2026": "date", "1960": "cited year", "1951": "cited year", "95": "interval level"}


def body_numbers(tex: str):
    tex = tex.split("\\begin{thebibliography}")[0]
    tex = re.sub(r"\\(label|ref|sref|figref|tabref|citep|citet|cite|includegraphics|url)\{[^}]*\}", " ", tex)
    tex = re.sub(r"\\begin\{tabularx\}\{[^}]*\}\{[^}]*\}", " ", tex)
    tex = re.sub(r"\\(setlength|titlespacing\*?|titleformat|usepackage|newcolumntype|renewcommand|setcounter|"
                 r"documentclass|setlist)[^\n]*", " ", tex)
    tex = re.sub(r"[Pp]\{[\d.]+cm\}|[\d.]+(pt|em|in|cm)\b", " ", tex)
    tex = tex.replace("{,}", ",").replace("--", " ")
    return [t.rstrip(",") for t in re.findall(r"(?<![\w.])\d[\d,]*(?:\.\d+)?", tex)]


def main() -> int:
    nums = body_numbers((ROOT / "paper.tex").read_text(encoding="utf-8"))
    bad = []
    for t in sorted(set(nums), key=lambda s: float(s.replace(",", ""))):
        src = REG.get(t) or REG.get(t.replace(",", "")) or STRUCTURE.get(t)
        print(f"{t:>10}  x{nums.count(t):<3} {src or 'UNMATCHED'}")
        if not src:
            bad.append(t)
    print(f"\n{len(set(nums))} distinct numbers, {len(bad)} unmatched: {bad}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
