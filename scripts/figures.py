"""The paper's figures. Every number comes from data/ or scripts/paper_numbers.py.

    python scripts/figures.py

One style for every figure: a headline stating the finding and a subtitle stating what was measured; two meaning
colours (blue: the targeted question / what is known, orange: what happens in the run), warm greys for everything
else; meaning is also carried by shape, fill or position so that every figure reads in greyscale; no boxes, no tick
marks; small samples drawn as units. Writes figures/<name>.pdf (vector, fonts embedded) and figures/<name>.png.
"""
import json
import math
import sys
import textwrap
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import paper_numbers as N  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
FIG = ROOT / "figures"
FIG.mkdir(exist_ok=True)
D = json.loads((ROOT / "data" / "replay_outcomes.json").read_text(encoding="utf-8"))
J2 = ROOT / "data" / "judge_agreement.json"
RNG = np.random.default_rng(20261020)

INK, MUTED, FAINT, RULE, PAPER, TRACK = "#1d2330", "#5d6573", "#a3a9b4", "#e4e2dd", "#f5f3ee", "#eceae4"
GREY, GREY_D = "#cfcac0", "#8f897e"
KNOW, KNOW_L = "#2348b0", "#c4d1f3"
DO, DO_L = "#e8743b", "#f8d3bd"
GOOD = "#2f8a5c"
WIDTH = 7.2

mpl.rcParams.update({
    "font.family": "sans-serif", "font.sans-serif": ["Segoe UI", "Arial", "DejaVu Sans"], "font.size": 8,
    "axes.spines.top": False, "axes.spines.right": False, "axes.spines.left": False, "axes.spines.bottom": False,
    "axes.grid": False, "xtick.color": FAINT, "ytick.color": INK, "xtick.labelsize": 7.5, "ytick.labelsize": 8,
    "xtick.major.size": 0, "ytick.major.size": 0, "xtick.minor.size": 0, "xtick.major.pad": 3,
    "text.color": INK, "figure.facecolor": "white", "savefig.facecolor": "white", "pdf.fonttype": 42,
    "savefig.dpi": 300, "legend.frameon": False,
})
SEMI = {"fontfamily": "Segoe UI Semibold"}


def header(fig, title, subtitle):
    h = fig.get_figheight()
    fig.text(0.012, 1 - 0.06 / h, title, fontsize=11.5, color=INK, va="top", ha="left", **SEMI)
    fig.text(0.012, 1 - 0.30 / h, subtitle, fontsize=8.2, color=MUTED, va="top", ha="left")


def top(fig, gap=0.72):
    return 1 - gap / fig.get_figheight()


def save(fig, name):
    for ext in ("pdf", "png"):
        fig.savefig(FIG / f"{name}.{ext}", bbox_inches="tight", pad_inches=0.06)
    plt.close(fig)
    print("wrote", name)


def pill(ax, x0, x1, y, color, lw=7.0, z=2):
    ax.plot([x0, x1], [y, y], color=color, lw=lw, solid_capstyle="round", zorder=z)


def dot(ax, x, y, color, s=46, z=4, edge="white", marker="o", lw=1.1):
    ax.scatter([x], [y], s=s, color=color, edgecolors=edge, linewidths=lw, zorder=z, marker=marker)


def ring(ax, x, y, color, filled, s=60, z=4):
    ax.scatter([x], [y], s=s, facecolors=color if filled else "white", edgecolors=color, linewidths=1.2, zorder=z)


def vgrid(ax, xs, ymin, ymax, labels):
    for v in xs:
        ax.plot([v, v], [ymin, ymax], color=RULE, lw=0.7, zorder=0)
    ax.set_xticks(xs, labels)


# ── conditions ──────────────────────────────────────────────────────────────────────────────────────
ST = D["single_turn"]
FAILM = [p["id"] for p in D["failure_points"]]
HEALTHM = D["control_points"]
ORDER = D["conditions"]
BASE, POINTER, ANSWER = "No note (baseline)", "Pointer to the output", "Answer-informed question"
LABEL = {c: c for c in ORDER}
SHORT = {"No note (baseline)": "Base-\nline", "Maximum reasoning effort": "Max\neffort",
         "Generic reminder": "Generic\nreminder", "Self-review prompt": "Self-\nreview",
         "Fresh reader: open question": "Reader:\nopen", "Fresh reader: assumptions": "Reader:\nassump.",
         "Fresh reader: largest impact": "Reader:\nimpact", "Fresh readers: all questions": "Readers:\nall",
         "Fresh reader: disagreements": "Reader:\ndisagree", "Pointer to the output": "Pointer\nonly",
         "Answer-informed question": "Answer-\ninformed"}
POINTS = {p["id"]: (p["problem"], f"{p['benchmark']}, {p['run_model'].split(',')[0]}") for p in D["failure_points"]}


def acts(c, points=FAILM):
    return sum(sum(ST[c][m]) for m in points), sum(len(ST[c][m]) for m in points)


def cluster_boot(c, reps=20000):
    k = np.array([sum(ST[c][m]) for m in FAILM])
    n = np.array([len(ST[c][m]) for m in FAILM])
    idx = RNG.integers(0, len(FAILM), size=(reps, len(FAILM)))
    return np.percentile(k[idx].sum(1) / n[idx].sum(1), [2.5, 97.5])


# ── Figure 1: study design ──────────────────────────────────────────────────────────────────────────
def card(ax, x, y, w, h, title, lines, col=INK, fill=PAPER):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=1.2", facecolor=fill,
                                edgecolor="none", zorder=1))
    ax.text(x + 1.4, y + h - 2.2, title, ha="left", va="top", fontsize=8.6, color=col, **SEMI)
    ax.text(x + 1.4, y + h - 6.6, "\n".join(lines), ha="left", va="top", fontsize=6.9, color=MUTED, linespacing=1.3)


def arrow(ax, p0, p1):
    ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle="-|>", mutation_scale=8, color=FAINT, lw=0.9, zorder=2))


def fig1():
    kappa_judge = ""
    if J2.exists():
        kappa_judge = f"second-judge agreement κ = {json.loads(J2.read_text())['cohen_kappa']:.2f}"
    fig = plt.figure(figsize=(WIDTH, 3.05))
    header(fig, "Study design: trace each failure, then replay the moment it was decided",
           "Tracing of 104 failed outputs, controlled replays at 13 failure points, and direct probes of the "
           "same facts")
    ax = fig.add_axes([0.0, 0.0, 1.0, top(fig, 0.62)])
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 50)
    ax.axis("off")
    card(ax, 0.5, 26, 23, 23, "16 benchmark runs",
         ["13 BixBench3 task runs", "(GPT-6.1 Sol root agent,", " DeepSeek V4.1 Flash sub-agents)",
          "3 GeneBench-Pro runs of 10 problems", "(DeepSeek V4.1 Flash ×2, GPT-6 Astra)"])
    card(ax, 26.5, 26, 23, 23, "104 failed outputs, traced",
         ["each reproduced against the reference", "smallest change that removes it", "transcript read back to the step",
          "where the error entered", "two independent passes, κ = 0.79"])
    card(ax, 52.5, 26, 21, 23, "Where failures occur",
         ["primary cause per output", "48 cause groups", "printed disproving evidence:", "42 of 58 GeneBench-Pro keys",
          "Section 4"], col=DO)
    card(ax, 26.5, 1, 23, 22, "13 failure points",
         ["the exact model request sent just", "after the disproving number was", "printed; 3 points from passing",
          "runs as controls"])
    card(ax, 52.5, 1, 21, 22, "Controlled replays",
         ["Claude Haiku 5.5 answers in the", "original agent's place", f"{len(ORDER)} conditions × 6 samples",
          "scored by Claude Sonnet 5.5", kappa_judge or "Section 6"], col=KNOW)
    card(ax, 76.5, 1, 23, 48, "Direct probes",
         ["the fact that would have prevented", "a failure, asked outside the task", "", "5 probes, 3 to 30 samples each",
          "compared with what the agent did", "in the run", "", "Section 5"], col=KNOW)
    arrow(ax, (23.6, 37.5), (26.4, 37.5))
    arrow(ax, (49.6, 37.5), (52.4, 37.5))
    arrow(ax, (38, 25.9), (38, 23.1))
    arrow(ax, (49.6, 12), (52.4, 12))
    save(fig, "fig1_design")


# ── Figure 2: the taxonomy ──────────────────────────────────────────────────────────────────────────
def fig2():
    fig = plt.figure(figsize=(WIDTH, 3.25))
    header(fig, "Most failures are process failures; the disproving number was often already on screen",
           "Primary cause of 104 failed outputs, two classification passes (left); 58 failed GeneBench-Pro answer keys "
           "(right)")
    t = top(fig)
    a = fig.add_axes([0.31, 0.07, 0.32, t - 0.07])
    import csv
    from collections import Counter

    rows_ = list(csv.DictReader(open(ROOT / "data" / "failure_classification.csv", encoding="utf-8")))
    c1, c2 = Counter(r["first_pass"] for r in rows_), Counter(r["second_pass"] for r in rows_)

    def both(cls):
        return c1[cls], c2[cls]

    groups = [
        ("THE AGENT'S ANALYSIS", [("Default method used without a test", *both("default method used without a test")),
                                  ("Assumption never checked per unit", *both("assumption never checked per unit")),
                                  ("Disproving number on screen, not acted on",
                                   *both("disproving number on screen, not acted on"))]),
        ("OUTSIDE THE AGENT'S ANALYSIS", [("Task wording and reference convention disagree",
                                           *both("task wording and reference convention disagree")),
                                          ("Tooling or environment", *both("tooling or environment"))]),
        ("NOT FOUND AS A PRIMARY CAUSE", [("State lost over a long run", 0, 0), ("Output format", 0, 0)]),
    ]
    y, rows = 0.0, []
    for gname, items in groups:
        rows.append(("H", gname, y))
        y -= 0.85
        for item in items:
            rows.append(("R", item, y))
            y -= 1.0
        y -= 0.35
    vgrid(a, [0, 10, 20, 30, 40], y + 0.6, 0.0, ["0", "10", "20", "30", "40%"])
    for kind, item, yy in rows:
        if kind == "H":
            a.text(-0.012, yy, item, transform=a.get_yaxis_transform(), ha="right", va="center", fontsize=6.3,
                   color=FAINT, **SEMI)
            continue
        name, ra, rb = item
        pa, pb = ra / len(rows_) * 100, rb / len(rows_) * 100
        lo, hi = min(pa, pb), max(pa, pb)
        proc = groups[0][1][0][0] == name or name in [i[0] for i in groups[0][1]]
        col, light = (DO, DO_L) if proc else (GREY_D, "#e7e3dc")
        a.text(-0.012, yy, name, transform=a.get_yaxis_transform(), ha="right", va="center", fontsize=7.6,
               color=INK if hi > 0 else MUTED)
        if hi > 0:
            if hi - lo > 0.3:
                pill(a, lo, hi, yy, light, lw=9)
            dot(a, pa, yy, col, s=34)
            dot(a, pb, yy, col, s=30, marker="D")
            txt = f"{lo:.0f}%" if hi - lo < 0.5 else f"{lo:.0f} to {hi:.0f}%"
            a.text(hi + 1.8, yy, txt, va="center", fontsize=7.3, color=col, **SEMI)
        else:
            a.text(0.6, yy, "0", va="center", fontsize=7.3, color=FAINT, **SEMI)
    a.set_xlim(-1.0, 52)
    a.set_ylim(y + 0.6, 0.75)
    a.set_yticks([])
    dot(a, 16, 0.55, GREY_D, s=26)
    a.text(17.3, 0.55, "first pass", va="center", fontsize=6.5, color=MUTED)
    dot(a, 30, 0.55, GREY_D, s=22, marker="D")
    a.text(31.3, 0.55, "second pass", va="center", fontsize=6.5, color=MUTED)
    b = fig.add_axes([0.70, 0.07, 0.29, t - 0.07])
    b.set_aspect("equal")
    b.axis("off")
    on = "disproving number on screen, not acted on"
    gb = [r for r in rows_ if r["benchmark"] == "GeneBench-Pro"]
    n_p = sum(r["first_pass"] == on for r in gb)
    n_c = sum(r["first_pass"] != on and r["contributing_cause"] == on for r in gb)
    n_n = len(gb) - n_p - n_c
    cells = ["P"] * n_p + ["C"] * n_c + ["N"] * n_n
    for i, c in enumerate(cells):
        r, q = divmod(i, 10)
        fc = {"P": DO, "C": DO_L, "N": "white"}[c]
        ec = {"P": DO, "C": DO_L, "N": GREY}[c]
        b.add_patch(FancyBboxPatch((q * 1.12 + 0.03, -r * 1.12 + 0.03), 0.86, 0.86,
                                   boxstyle="round,pad=0,rounding_size=0.2", facecolor=fc, edgecolor=ec, lw=0.9))
    b.text(0, 4.15, f"{n_p + n_c} of {len(gb)}", fontsize=17, color=DO, va="bottom", ha="left", **SEMI)
    b.text(0, 1.35, "failed keys where the agent had printed\na number contradicting its answer", fontsize=7.0,
           color=MUTED, va="bottom", ha="left", linespacing=1.25)
    for yy, kind, num, t_ in ((-7.7, "P", str(n_p), "the primary cause"), (-8.85, "C", str(n_c), "a contributing cause"),
                              (-10.0, "N", str(n_n), "not on screen")):
        fc = {"P": DO, "C": DO_L, "N": "white"}[kind]
        ec = {"P": DO, "C": DO_L, "N": GREY}[kind]
        b.add_patch(FancyBboxPatch((0.03, yy - 0.40), 0.8, 0.8, boxstyle="round,pad=0,rounding_size=0.18",
                                   facecolor=fc, edgecolor=ec, lw=0.9))
        b.text(1.4, yy, num, va="center", fontsize=7.2, color=INK, **SEMI)
        b.text(2.75, yy, t_, va="center", fontsize=7.0, color=INK)
    b.set_xlim(-0.1, 11.3)
    b.set_ylim(-10.7, 6.3)
    save(fig, "fig2_taxonomy")


# ── Figure 3: interventions (main result) ───────────────────────────────────────────────────────────
def fig3():
    n = len(ORDER)
    fig = plt.figure(figsize=(WIDTH, 0.32 * n + 1.25))
    header(fig, "Pointing at the right output moved the agent; generic prompts and fresh readers did not",
           "Claude Haiku 5.5 replies that followed up the disproving evidence, 13 failure points × 6 samples per "
           "condition (left); unwarranted rework at 3 healthy points × 6 samples (right)")
    t = top(fig)
    a = fig.add_axes([0.255, 0.07, 0.58, t - 0.07])
    b = fig.add_axes([0.875, 0.07, 0.11, t - 0.07])
    base_rate = acts(BASE)[0] / acts(BASE)[1] * 100
    vgrid(a, [0, 25, 50, 75, 100], -0.6, n - 0.4, ["0", "25", "50", "75", "100%"])
    a.plot([base_rate, base_rate], [-0.6, n - 0.4], color=DO, lw=0.8, ls=(0, (2, 2.5)), zorder=0.5)
    vgrid(b, [0, 20], -0.6, n - 0.4, ["0", "20%"])
    for i, c in enumerate(ORDER):
        yy = n - 1 - i
        k, m = acts(c)
        lo, hi = cluster_boot(c)
        answer_row, base, pointer = c == ANSWER, c == BASE, c == POINTER
        col = KNOW if (answer_row or pointer) else (DO if base else GREY_D)
        light = KNOW_L if (answer_row or pointer) else (DO_L if base else "#e9e5de")
        pill(a, lo * 100, hi * 100, yy, light, lw=6)
        dot(a, k / m * 100, yy, col, s=60, marker="D" if answer_row else ("s" if base else "o"))
        a.text(hi * 100 + 2.0, yy, f"{k}/{m}", va="center", fontsize=7.4, color=col if col != GREY_D else MUTED, **SEMI)
        strong = base or answer_row or pointer
        a.text(-0.02, yy, LABEL[c], transform=a.get_yaxis_transform(), ha="right", va="center", fontsize=7.8,
               color=INK if strong else "#3d4452", **(SEMI if strong else {}))
        hk, hn = acts(c, HEALTHM)
        if hn:
            dot(b, hk / hn * 100, yy, DO if hk else GREY_D, s=36)
            b.text(23, yy, f"{hk}/{hn}", va="center", fontsize=7.0, color=DO if hk else MUTED)
        else:
            b.text(0, yy, "not run", va="center", fontsize=6.5, color=FAINT)
    a.text(base_rate + 1.2, n - 0.45, "baseline", ha="left", va="bottom", fontsize=6.6, color=DO)
    a.set_xlim(-2, 105)
    a.set_ylim(-0.6, n - 0.2)
    a.set_yticks([])
    b.set_xlim(-3, 34)
    b.set_ylim(-0.6, n - 0.2)
    b.set_yticks([])
    b.text(0, n - 0.45, "rework", ha="left", va="bottom", fontsize=6.6, color=MUTED, **SEMI)
    save(fig, "fig3_interventions")


# ── Figure 4: per failure point ─────────────────────────────────────────────────────────────────────
def fig4():
    nc, nr = len(ORDER), len(FAILM)
    fig = plt.figure(figsize=(WIDTH, 5.3))
    header(fig, "The pointer and the answer-informed question worked at most points; nothing else did",
           "Samples (of 6) that followed up the disproving evidence, by failure point and condition; "
           "all replies by Claude Haiku 5.5")
    ax = fig.add_axes([0.255, 0.01, 0.74, top(fig, 0.62) - 0.01])
    cmap = mpl.colors.LinearSegmentedColormap.from_list("k", ["#f3f1ec", "#c3d0f2", "#6f8fe0", KNOW, "#132a6e"])
    sx = lambda j: j + (0.35 if ORDER[j] == ANSWER else 0.0)  # noqa: E731
    for i, mo in enumerate(FAILM):
        yy = -i * 1.18
        for j, c in enumerate(ORDER):
            v = sum(ST[c][mo])
            ax.add_patch(FancyBboxPatch((sx(j) + 0.06, yy - 0.46), 0.88, 0.92, boxstyle="round,pad=0,rounding_size=0.14",
                                        facecolor=cmap(v / 6), edgecolor="none"))
            ax.text(sx(j) + 0.5, yy, str(v), ha="center", va="center", fontsize=7.6,
                    color="white" if v >= 3 else (INK if v else FAINT), **(SEMI if v else {}))
        prob, where = POINTS[mo]
        ax.text(-0.15, yy + 0.17, prob, ha="right", va="center", fontsize=7.6, color=INK, **SEMI)
        ax.text(-0.15, yy - 0.27, where, ha="right", va="center", fontsize=6.3, color=MUTED)
    ylast = -(nr - 1) * 1.18
    for j, c in enumerate(ORDER):
        answer_row = c == ANSWER
        ax.text(sx(j) + 0.5, 0.75, SHORT[c], ha="center", va="bottom", fontsize=6.7,
                color=KNOW if answer_row else MUTED, linespacing=1.1, **(SEMI if answer_row else {}))
        k, n = acts(c)
        ax.text(sx(j) + 0.5, ylast - 1.15, f"{k}/{n}", ha="center", va="center", fontsize=7.2,
                color=KNOW if answer_row else (DO if c == BASE else MUTED), **SEMI)
    ax.text(-0.15, ylast - 1.15, "All 13 points", ha="right", va="center", fontsize=7.6, color=INK, **SEMI)
    ax.plot([0.05, nc + 0.3], [ylast - 0.7, ylast - 0.7], color=RULE, lw=0.8)
    ax.set_xlim(-0.05, nc + 0.4)
    ax.set_ylim(ylast - 1.55, 1.75)
    ax.axis("off")
    save(fig, "fig4_points")


# ── Figure 5: reasoning effort on one problem ───────────────────────────────────────────────────────
def fig5():
    fig = plt.figure(figsize=(WIDTH, 3.25))
    header(fig, "On one problem, more reasoning found the defect; at the 13 failure points it did not",
           "Electrical-load time series (our probe set): forks from the turn after the agent found a 28-row gap, "
           "Claude Haiku 5.5 unless stated")
    t = top(fig)
    a = fig.add_axes([0.235, 0.07, 0.30, t - 0.07])
    rows = N.FEEDER_SCHEDULES + [("Claude Sonnet 5.5, high throughout", *N.SONNET_HIGH)]
    names = {"high throughout": "Effort high throughout", "xhigh throughout": "Effort extra-high throughout",
             "max on the first reply only": "Maximum on the first reply only",
             "re-ask an ending reply at max": "Re-ask an ending reply at maximum",
             "max throughout": "Maximum throughout", "high, then max after it": "High, then maximum after it"}
    n = len(rows)
    vgrid(a, [0, 50, 100], -1.0, n - 0.4, ["0", "50", "100%"])
    for i, (name, k, m) in enumerate(rows):
        sonnet = name.startswith("Claude")
        yy = n - 1 - i - (0.35 if sonnet else 0)
        p = k / m * 100
        col = KNOW if "then max" in name else (GOOD if sonnet else GREY_D)
        pill(a, 0, 100, yy, TRACK, lw=7, z=1)
        pill(a, 0, max(p, 0.6), yy, GREY if col == GREY_D else col, lw=7, z=2)
        a.text(104, yy, f"{k}/{m}", va="center", fontsize=7.4, color=col if col != GREY_D else MUTED, **SEMI)
        a.text(-0.03, yy, names.get(name, name), transform=a.get_yaxis_transform(), ha="right", va="center",
               fontsize=7.4, color=INK if col != GREY_D else "#3d4452", **(SEMI if col != GREY_D else {}))
    a.set_xlim(-3, 118)
    a.set_ylim(-1.0, n - 0.3)
    a.set_yticks([])
    a.text(0, n - 0.32, "FORKS GRADED CORRECT BY THE PROBLEM'S GRADER (OF 15 OR 10)", fontsize=5.9, color=FAINT,
           va="bottom", **SEMI)
    b = fig.add_axes([0.745, 0.07, 0.235, t - 0.07])
    meas = [("Split the hour profile\nby period (first reply)", 9, 30, 24, 30),
            ("Named the coincidence\n(first reply)", 13, 30, 30, 30),
            ("Fork graded\ncorrect", 1, 15, 12, 15),
            ("Followed up at the\n13 failure points", 10, 78, 9, 78)]
    nb = len(meas)
    vgrid(b, [0, 50, 100], -0.7, nb - 0.3, ["0", "50", "100%"])
    for i, (lab, hk, hn, mk, mn) in enumerate(meas):
        yy = nb - 1 - i
        last = i == nb - 1
        h, mx = hk / hn * 100, mk / mn * 100
        if not last:
            b.annotate("", xy=(mx, yy), xytext=(h, yy), arrowprops=dict(arrowstyle="-|>", color=KNOW, lw=1.3,
                                                                        shrinkA=5, shrinkB=5, mutation_scale=8))
        dot(b, h, yy, GREY_D, s=44)
        dot(b, mx, yy, GREY_D if last else KNOW, s=44, z=5, marker="D")
        if last:
            b.text(h + 6, yy, "10/78 at high,\n9/78 at maximum", ha="left", va="center", fontsize=6.6, color=DO,
                   linespacing=1.15, **SEMI)
        else:
            b.text(h, yy + 0.3, f"{hk}/{hn}", ha="center", va="bottom", fontsize=6.5, color=MUTED)
            b.text(mx, yy - 0.3, f"{mk}/{mn}", ha="center", va="top", fontsize=6.5, color=KNOW, **SEMI)
        b.text(-0.05, yy, lab, transform=b.get_yaxis_transform(), ha="right", va="center", fontsize=7.0,
               color=DO if last else INK, linespacing=1.15)
    b.set_xlim(-6, 108)
    b.set_ylim(-0.7, nb - 0.3)
    b.set_yticks([])
    dot(b, 22, nb - 0.42, GREY_D, s=26)
    b.text(26, nb - 0.42, "high", fontsize=6.6, color=MUTED, va="center")
    dot(b, 50, nb - 0.42, KNOW, s=24, marker="D")
    b.text(54, nb - 0.42, "maximum", fontsize=6.6, color=KNOW, va="center")
    save(fig, "fig5_effort")


# ── Figure 6: event raster ──────────────────────────────────────────────────────────────────────────
RASTER_NAMES = {"CRISPRi": "CRISPR interference screen", "MVMR": "Mendelian randomization", "admixture": "Admixture dating",
                "carrier": "Carrier-frequency estimation", "Hi-C": "Chromatin-contact loop strength",
                "txr1": "Treatment-effect estimation", "scRNA": "Single-cell expression QTL",
                "structural": "Structural-variant association"}
RUN_NAMES = {"DeepSeek t2": "DeepSeek V4.1 Flash, trial 2", "DeepSeek t3": "DeepSeek V4.1 Flash, trial 3",
             "GPT-6 Astra": "GPT-6 Astra"}


def fig6():
    rows = N.RASTER
    fig = plt.figure(figsize=(WIDTH, 3.75))
    header(fig, "The disproving number was printed with most of the run still ahead",
           "Twelve failed GeneBench-Pro runs, from first step to answer, with the steps at which the agent printed the "
           "disproving number")
    t = top(fig)
    ax = fig.add_axes([0.25, 0.06, 0.72, t - 0.06])
    n = len(rows)
    vgrid(ax, [0, 20, 40, 60, 80, 100], -0.6, n - 0.3, ["step 0", "20", "40", "60", "80", "100"])
    for i, (label, steps, ev, _dis) in enumerate(rows):
        yy = n - 1 - i
        pill(ax, 0, steps, yy, TRACK, lw=5.5, z=1)
        pill(ax, ev[0], steps, yy, DO_L, lw=5.5, z=1.5)
        for e in ev:
            dot(ax, e, yy, KNOW, s=40, z=4)
        ax.text(steps + 2.0, yy, f"{steps}", va="center", fontsize=6.8, color=MUTED)
        prob, run = label.split(", ")
        ax.text(-0.015, yy + 0.12, RASTER_NAMES[prob], transform=ax.get_yaxis_transform(), ha="right", va="center",
                fontsize=7.4, color=INK, **SEMI)
        ax.text(-0.015, yy - 0.27, RUN_NAMES[run], transform=ax.get_yaxis_transform(), ha="right", va="center",
                fontsize=6.3, color=MUTED)
    ax.set_xlim(-2, 118)
    ax.set_ylim(-0.7, n - 0.3)
    ax.set_yticks([])
    lx, ly = 64, n - 1.05
    dot(ax, lx, ly, KNOW, s=40)
    ax.text(lx + 2.2, ly, "disproving number printed", va="center", fontsize=7, color=KNOW)
    pill(ax, lx - 1.2, lx + 1.2, ly - 0.75, DO_L, lw=5.5)
    ax.text(lx + 2.2, ly - 0.75, "run continues after the first print", va="center", fontsize=7, color=MUTED)
    ax.text(lx + 2.2, ly - 1.55, "median 59% of steps still ahead", va="center", fontsize=7.2, color=INK, **SEMI)
    save(fig, "fig6_timing")


# ── Figure 7: predictions in a plan ─────────────────────────────────────────────────────────────────
def fig7():
    fig = plt.figure(figsize=(WIDTH, 2.6))
    header(fig, "Asked to predict a result in a plan, the agent wrote bounds its result could not cross",
           "Target-gene count per replicate, BixBench3 task 1, GPT-6.1 Sol (left); rate-constant ratio, our "
           "reaction-kinetics probe, GPT-6.1 Sol (right)")
    t = top(fig)
    a = fig.add_axes([0.20, 0.13, 0.46, t - 0.13])
    T = N.TASK1
    rows = [("Prediction in plan 1", T["plan prior 1"], GREY, "#5d574d"),
            ("Prediction in plan 2", T["plan prior 2"], GREY, "#5d574d"),
            ("Typical count, asked directly", T["bare recall"], KNOW, KNOW),
            ("The agent's own result", T["agent result"], DO, DO)]
    a.set_xscale("log")
    vgrid(a, [100, 300, 1000, 3000, 10000, 30000], -0.6, len(rows) - 0.4, ["100", "300", "1k", "3k", "10k", "30k"])
    a.xaxis.set_minor_locator(mpl.ticker.NullLocator())
    for i, (name, (lo, hi), fill, tc) in enumerate(rows):
        yy = len(rows) - 1 - i
        pill(a, lo, hi, yy, fill, lw=8)
        a.text(hi * 1.18, yy, f"{lo:,} to {hi:,}", ha="left", va="center", fontsize=6.8, color=tc, **SEMI)
        a.text(-0.02, yy, name, transform=a.get_yaxis_transform(), ha="right", va="center", fontsize=7.6, color=INK)
    a.set_xlim(70, 60000)
    a.set_ylim(-0.6, len(rows) - 0.35)
    a.set_yticks([])
    b = fig.add_axes([0.745, 0.13, 0.245, t - 0.13])
    A = N.ARRHENIUS
    b.set_xscale("log")
    vgrid(b, [1, 10, 100], -0.9, 1.6, ["1×", "10×", "100×"])
    b.xaxis.set_minor_locator(mpl.ticker.NullLocator())
    pill(b, A["bare recall"][0], A["bare recall"][1], 1, KNOW, lw=8)
    b.text(A["bare recall"][1] * 1.35, 1, "1.3 to 1.7× per 5 °C,\nwhen asked directly", va="center",
           fontsize=6.8, color=KNOW, linespacing=1.15, **SEMI)
    dot(b, A["observed"], 0, DO, s=70, marker="D")
    b.text(A["observed"] / 1.4, 0, "87× jump\nin the data", va="center", ha="right", fontsize=6.8, color=DO,
           linespacing=1.15, **SEMI)
    b.text(0.8, -0.62, "In its plan: “magnitude cannot be estimated”", fontsize=6.5, color=MUTED, ha="left",
           va="center", style="italic")
    b.set_xlim(0.75, 250)
    b.set_ylim(-0.9, 1.6)
    b.set_yticks([])
    save(fig, "fig7_predictions")


# ── Appendix figure: multi-turn and early forks ─────────────────────────────────────────────────────
def units(ax, x, y, vals, col, s=62, step=0.47):
    for k, v in enumerate(vals):
        ring(ax, x + k * step, y, col, bool(v), s=s)


def figA1():
    fig = plt.figure(figsize=(WIDTH, 2.95))
    header(fig, "Over six turns a list of questions helped where the evidence was a printed disagreement",
           "Each circle is one fork (Claude Haiku 5.5), filled when the agent followed up the disproving evidence")
    t = top(fig, 0.62)
    MT = D["multi_turn"]
    arms = [(BASE, "Baseline", GREY_D), ("Fresh readers: all questions", "All readers", DO),
            (ANSWER, "Answer-informed", KNOW)]
    mom = [("carrier-frequency/deepseek", "Carrier frequency"), ("single-cell-eqtl/astra", "Single-cell eQTL"),
           ("admixture-dating/astra", "Admixture dating"), ("qtl-multiparent/astra", "QTL, multiparent")]
    a = fig.add_axes([0.01, 0.03, 0.46, t - 0.03])
    a.set_xlim(0, 10)
    a.set_ylim(-0.75, 4.75)
    a.axis("off")
    a.text(0.0, 4.55, "SIX-TURN FORKS FROM A FAILURE POINT", fontsize=6.0, color=FAINT, va="center", **SEMI)
    for j, (_, lab, col) in enumerate(arms):
        a.text(3.4 + j * 2.25, 3.85, lab, ha="left", va="center", fontsize=7.0, color=col, **SEMI)
    for i, (m, lab) in enumerate(mom):
        yy = 3.05 - i * 0.82
        a.text(0.0, yy, lab, va="center", fontsize=7.6, color=INK, **SEMI)
        for j, (arm, _, col) in enumerate(arms):
            units(a, 3.55 + j * 2.25, yy, MT[arm][m], col)
    a.text(0.0, -0.5, "Totals: baseline 5/12, all readers 8/12, answer-informed 11/11", fontsize=6.8, color=MUTED,
           va="center")
    b = fig.add_axes([0.51, 0.03, 0.48, t - 0.03])
    b.set_xlim(0, 10)
    b.set_ylim(-0.75, 4.75)
    b.axis("off")
    b.text(0.0, 4.55, "FORKS FROM THE FIRST LOOK AT THE DATA, CONTINUED TO THE END", fontsize=6.0, color=FAINT,
           va="center", **SEMI)
    E = D["early_list"]
    short = {"Structural-variant association": "Structural variant", "QTL mapping, multiparent cross": "QTL, multiparent",
             "CRISPR interference screen": "CRISPRi screen", "Treatment-effect estimation": "Treatment effect",
             "Carrier-frequency estimation": "Carrier frequency", "Mendelian randomization": "Mendelian rand.",
             "Single-cell expression QTL": "Single-cell eQTL", "Chromatin-contact loop strength": "Chromatin contacts",
             "Admixture dating": "Admixture dating"}
    probs = [(q["key"], short[q["problem"]]) for q in E["problems"]]
    named = {q["key"] for q in E["problems"] if q["list_named_decisive_check"]}
    b.text(3.6, 3.85, "Baseline", fontsize=7.0, color=GREY_D, va="center", **SEMI)
    b.text(5.35, 3.85, "Given a list", fontsize=7.0, color=KNOW, va="center", **SEMI)
    b.text(7.55, 3.85, "List named the\ndecisive check", fontsize=6.5, color=MUTED, va="center", linespacing=1.1)
    for i, (p, lab) in enumerate(probs):
        yy = 3.25 - i * 0.405
        b.text(0.0, yy, lab, va="center", fontsize=7.2, color=INK, **SEMI)
        units(b, 3.75, yy, E[BASE][p], GREY_D, s=44, step=0.40)
        if E["Given a list of checks"][p]:
            units(b, 5.5, yy, E["Given a list of checks"][p], KNOW, s=44, step=0.40)
        else:
            b.text(5.35, yy, "did not run", va="center", fontsize=6.3, color=FAINT)
        if p in named:
            b.text(8.15, yy, "✔", va="center", ha="center", fontsize=7.5, color=KNOW, fontfamily="Segoe UI Symbol")
    b.text(0.0, -0.5, "Totals: baseline 9/18, given a list 9/16", fontsize=6.8, color=MUTED, va="center")
    save(fig, "figA1_multiturn")


if __name__ == "__main__":
    for f in (fig1, fig2, fig3, fig4, fig5, fig6, fig7, figA1):
        f()
