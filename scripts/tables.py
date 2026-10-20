"""Appendix tables generated from data/, so their numbers cannot drift from the released files.

    python scripts/tables.py

Writes figures/tab_groups.tex (every cause group: the failures from one run of one problem that share a primary class,
with the second pass's class for the same failures) and figures/tab_points.tex (per-point replay counts).
"""
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SHORT = {"default method used without a test": "default", "assumption never checked per unit": "per-unit",
         "disproving number on screen, not acted on": "on screen",
         "task wording and reference convention disagree": "convention", "tooling or environment": "tooling",
         "not established": "not established"}


def groups() -> None:
    rows = list(csv.DictReader(open(ROOT / "data" / "failure_classification.csv", encoding="utf-8")))
    g = defaultdict(list)
    for r in rows:
        g[(r["benchmark"], r["problem"], r["run"], r["primary_class"])].append(r)
    out = []
    def order(kv):
        bench, prob, run, cls = kv[0]
        num = int(prob.split()[-1]) if bench == "BixBench3" else 0
        return bench, num, prob, run, cls

    for (bench, prob, run, cls), rs in sorted(g.items(), key=order):
        second = Counter(SHORT[r["second_rater_class"]] for r in rs)
        est = sum(r["cause_status"] == "established" for r in rs)
        model = run.split("(")[-1].rstrip(")") if "(" in run else run
        if bench == "BixBench3":
            model = "GPT-6.1 Sol root"
        out.append(f"{prob} & {model} & {len(rs)} & {SHORT[cls]} & "
                   f"{', '.join(f'{k} {v}' for k, v in sorted(second.items()))} & {est}\\\\")
    (ROOT / "figures" / "tab_groups.tex").write_text("\n".join(out) + "\n", encoding="utf-8")
    print("cause groups:", len(out))


def points() -> None:
    D = json.loads((ROOT / "data" / "replay_outcomes.json").read_text(encoding="utf-8"))
    ST = D["single_turn"]
    conds = D["conditions"]
    lines = []
    for p in D["failure_points"]:
        cells = " & ".join(str(sum(ST[c][p["id"]])) for c in conds)
        lines.append(f"{p['problem']} ({p['run_model'].split(',')[0]}) & {cells}\\\\")
    tot = " & ".join(str(sum(sum(ST[c][p['id']]) for p in D['failure_points'])) for c in conds)
    lines.append("\\midrule")
    lines.append(f"All failure points (of 78) & {tot}\\\\")
    # the answer-informed arm is not defined at the control points (it received the generic reminder there)
    rew = " & ".join("n/a" if c == "Answer-informed question" else str(sum(sum(ST[c][q]) for q in D["control_points"]))
                     for c in conds)
    lines.append(f"Control points, rework (of 18) & {rew}\\\\")
    (ROOT / "figures" / "tab_points.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("point rows:", len(D["failure_points"]))


if __name__ == "__main__":
    groups()
    points()
