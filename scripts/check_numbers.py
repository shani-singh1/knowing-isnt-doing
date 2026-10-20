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
W = "Pointer to another output"
kb, kp, ka, kr = (sum(sum(ST[c][p]) for p in PTS) for c in (B, P, A, R))
add(kp - kb, "pointer increase over baseline (samples)")
add(ka - kb, "answer-informed increase over baseline (samples)")
add(round(100 * (kp - kb) / (ka - kb)), "share of the increase recovered by the pointer (%)")
add(round(100 * (1 - 0.025 ** (1 / 18))), "two-sided 95% upper bound for 0 of 18 (%)")
for c1, c2 in ([(c, B) for c in D["conditions"] if c != B] + [(P, W), (P, R), (A, P)]):
    d = [sum(ST[c1][p]) - sum(ST[c2][p]) for p in PTS]
    add(sum(x > 0 for x in d), f"{c1} above {c2} (points)")
    add(sum(x < 0 for x in d), f"{c1} below {c2} (points)")
    add(sum(x == 0 for x in d), f"{c1} tied with {c2} (points)")
SENS = D["carrier_note_visible"]
for c in D["conditions"]:
    add(sum(SENS[c]), f"carrier sensitivity: {c}")
    add(sum(sum(ST[c][p]) for p in PTS) - sum(ST[c]["carrier-frequency/deepseek"]) + sum(SENS[c]),
        f"pooled follow-ups under the carrier sensitivity: {c}")
# reasoning after tool results (Claude Haiku 5.5 live runs)
E4 = list(csv.DictReader(open(ROOT / "data" / "reasoning_after_results.csv", encoding="utf-8")))
add(len(E4), "turns that read a tool result")
add(len({r["run"] for r in E4}), "live runs in the reasoning table")
for cls in ("clean_numeric", "traceback"):
    med = float(np.median([int(r["reasoning_chars"]) for r in E4 if r["result"] == cls]))
    add(f"{round(med):,}", f"median reasoning, {cls} ({med})")
both = [run for run in {r["run"] for r in E4}
        if {"clean_numeric", "traceback"} <= {r["result"] for r in E4 if r["run"] == run}]
add(len(both), "runs with both clean and traceback turns")
add(f"{int(E4[0]['output_limit_tokens']):,}", "output limit of the live runs")
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
a, b = [r["primary_class"] for r in rows], [r["second_rater_class"] for r in rows]
add(len(rows), "failed outputs")
for bench, n in Counter(r["benchmark"] for r in rows).items():
    add(n, f"failed outputs: {bench}")
add(sum(x == y for x, y in zip(a, b)), "classification agreement with the independent rater (failures)")
add(round(cohen_kappa(a, b), 2), "classification kappa")
for bench in ("BixBench3", "GeneBench-Pro"):
    aa = [r["primary_class"] for r in rows if r["benchmark"] == bench]
    bb = [r["second_rater_class"] for r in rows if r["benchmark"] == bench]
    add(sum(x == y for x, y in zip(aa, bb)), f"rater agreement: {bench}")
    add(sum(x != y for x, y in zip(aa, bb)), f"rater disagreements: {bench}")
    add(round(cohen_kappa(aa, bb), 2), f"rater kappa: {bench}")
    add(sum(x != y and "convention" in x + y for x, y in zip(aa, bb)), f"rater disagreements involving convention: {bench}")
add(sum(bool(r["co_dominant_alternative"]) for r in rows), "failures with two co-dominant causes")
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
        add(v, f"failures in class: {k}")
groups = {(r["run"], r["problem"], r["primary_class"]) for r in rows}
add(len(groups), "cause groups")
gc = Counter(g[2] for g in groups)
gp = sum(gc[k] for k in AG)
add(gp, "agent-attributable cause groups")
for k in AG:
    add(round(100 * gc[k] / gp), f"cause-group share: {k}")
on = "disproving number on screen, not acted on"
gb = [r for r in rows if r["benchmark"] == "GeneBench-Pro"]
n_p = sum(r["primary_class"] == on for r in gb)
n_c = sum(r["primary_class"] != on and r["contributing_cause"] == on for r in gb)
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
# documented constants the figures draw (scripts/paper_numbers.py)
for label, steps, ev, dis in N.RASTER:
    for v in [steps, *ev, *dis]:
        add(v, f"transcript step, {label}")
for k, (lo, hi) in N.TASK1.items():
    add(f"{lo:,}", f"DamID {k}")
    add(f"{hi:,}", f"DamID {k}")
for name, k, m in N.FEEDER_SCHEDULES:
    add(k, f"load-series forks correct, {name}")
for p in N.PROBES:
    for v in (*p["asked"], *p["run"]):
        add(v, f"knowledge probe, {p['problem']}")

# ── recorded values: printed by the agents, probe counts, study constants ───────────────────────────
RECORDED = {
    "0.2337": "carrier, printed by the agent", "0.1553": "carrier, reported estimate", "0.236": "carrier trial 3, printed",
    "0.119": "carrier trial 3, chosen", "0.117": "carrier trial 3, reported span", "0.146": "carrier trial 3, reported span",
    "0.427": "treatment effect, printed variant", "0.466": "treatment effect, headline", "0.37": "structural, printed variant",
    "0.29": "structural, primary estimate", "121": "structural, printed count",
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
    "37": "longest run, hours (36.8 rounded)", "9": "first replies splitting at high / failure points",
    "10": "GeneBench-Pro problems / probe samples", "7": "load-series shift, hours", "2": "DeepSeek trials",
    "1": "one run / one tie", "0": "zero counts", "6": "samples per point / per-point count",
    # scale of the study (run archive: task.json wall clocks, transcript.json steps, record.json calls, manifests)
    "43": "complete runs traced (13 BixBench3 + 30 GeneBench-Pro problem runs)", "23": "distinct tasks (13 + 10)",
    "1.9": "shortest BixBench3 run, hours", "36.8": "longest BixBench3 run, hours", "734": "BixBench3 staged input, GB",
    "3,808": "BixBench3 staged files", "1.65": "raw reads in the read-counting task, billions",
    "42,404": "GeneBench-Pro input table rows", "2.8": "longest GeneBench-Pro problem run, hours",
    "143": "agent-hours over the 43 runs", "8,421": "transcript steps", "7,852": "model calls in the traced runs",
    "49": "interventions designed", "46": "interventions tested", "25": "interventions, first phase",
    "3,461": "agent-side replay calls in the lab (lab/count_calls.py)", "65,536": "output limit of the live runs",
    "13": "BixBench3 tasks / failure points", "15": "15-minute interval / forks per schedule / live runs in the table",
    "0.25": "quoted: MW x 0.25 per 15-minute interval", "5": "BixBench3 reports with delegated work / live runs",
    "18": "control samples per condition / October date", "8": "October date / block pixels",
    # knowledge probes (lab/out/bare_*.jsonl and the live and replayed run records)
    "60": "largest run-side use rate among the probes (3 of 5)",
    # receipts from the forensic and design records (2026-10-20 receipts audit)
    "12": "reader notes, sound turns (9 of 12)", "4": "referee violations (4 of 8) / keys changed",
    "30": "keys per GeneBench-Pro run / first replies",
}
for k, v in RECORDED.items():
    REG.setdefault(k, v)
STRUCTURE = {"3.3": "section number", "3.4": "section number", "4.1": "model version", "5.5": "model version", "6": "model version", "6.1": "model version",
             "2026": "date", "1960": "cited year", "1951": "cited year", "95": "interval level"}


def body_numbers(tex: str):
    tex = tex.split("\\begin{thebibliography}")[0] + "\n" + tex.split("\\end{thebibliography}")[1]
    tex = re.sub(r"10\.\d{4,5}/[\w.\-]+", " ", tex)                       # task DOIs in the appendix
    tex = re.sub(r"\\texttt\{[^}]*\}", " ", tex)                          # identifiers and printed labels
    tex = re.sub(r"\\(label|ref|sref|figref|tabref|citep|citet|cite|includegraphics|url)\{[^}]*\}", " ", tex)
    tex = re.sub(r"\\begin\{tabularx\}\{[^}]*\}\{[^}]*\}", " ", tex)
    tex = re.sub(r"\\(setlength|titlespacing\*?|titleformat|usepackage|newcolumntype|renewcommand|setcounter|"
                 r"documentclass|setlist)[^\n]*", " ", tex)
    tex = re.sub(r"[Pp]\{[\d.]+cm\}|[\d.]+(pt|em|in|cm)\b", " ", tex)
    tex = tex.replace("{,}", ",").replace("--", " ")
    return [t.rstrip(",") for t in re.findall(r"(?<![\w.])\d[\d,]*(?:\.\d+)?", tex)]


AXIS = {"0", "10", "20", "25", "40", "50", "60", "75", "80", "100", "1,000", "10,000", "1", "1k", "10k"}


def figure_numbers() -> dict[str, list[str]]:
    """Numbers printed in each figure PDF (needs PyMuPDF; skipped with a note if it is not installed)."""
    try:
        import fitz
    except ImportError:
        print("figures not checked: PyMuPDF (fitz) is not installed")
        return {}
    out = {}
    for pdf in sorted((ROOT / "figures").glob("fig*.pdf")):
        text = " ".join(page.get_text() for page in fitz.open(pdf))
        text = re.sub(r"GPT-6(\.1)?|V4\.1|(Haiku|Sonnet|Opus) 5\.5|BixBench3|2x2|DST|chr\d|\d+ ?°C|\d+×", " ", text)
        out[pdf.name] = [t.rstrip(",") for t in re.findall(r"(?<![\w.])\d[\d,]*(?:\.\d+)?k?", text)]
    return out


def main() -> int:
    figs = figure_numbers()
    fbad = []
    for name, nums in figs.items():
        for t in nums:
            if not (REG.get(t) or REG.get(t.replace(",", "")) or STRUCTURE.get(t) or t in AXIS):
                fbad.append(f"{name}:{t}")
    if figs:
        print(f"figures: {sum(len(v) for v in figs.values())} numbers in {len(figs)} figures, {len(fbad)} unmatched: {fbad}")
    nums = body_numbers((ROOT / "paper.tex").read_text(encoding="utf-8"))
    bad = []
    for t in sorted(set(nums), key=lambda s: float(s.replace(",", ""))):
        src = REG.get(t) or REG.get(t.replace(",", "")) or STRUCTURE.get(t)
        print(f"{t:>10}  x{nums.count(t):<3} {src or 'UNMATCHED'}")
        if not src:
            bad.append(t)
    print(f"\n{len(set(nums))} distinct numbers, {len(bad)} unmatched: {bad}")
    return 1 if bad or fbad else 0


if __name__ == "__main__":
    sys.exit(main())
