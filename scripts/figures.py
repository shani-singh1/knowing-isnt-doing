"""The paper's figures. Every number comes from data/ or scripts/paper_numbers.py.

    python scripts/figures.py

One palette for the whole paper: one colour for the baseline, one accent for the condition or class a figure is
about, greys for everything else. Meaning is also carried by shape or position, so every figure reads in greyscale.
Text is never smaller than 8 pt at the printed size: figures are drawn at the text width (6.5 in) and included at
\\textwidth. Writes figures/<name>.pdf (vector, fonts embedded) and figures/<name>.png.
"""
import csv
import json
import sys
from collections import Counter
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
RNG = np.random.default_rng(20261020)

INK, MUTED, RULE, TRACK = "#1d2330", "#5d6573", "#e4e2dd", "#eeece7"
GREY, GREY_D, GREY_L = "#b9b4aa", "#7f796e", "#e3dfd8"
BASE_C, BASE_L = "#d9692e", "#f6d2bf"      # the baseline
ACC, ACC_L = "#2348b0", "#c4d1f3"          # the accent: what the figure is about
WIDTH = 6.5
FS = 8.0                                   # smallest text size, pt

mpl.rcParams.update({
    "font.family": "sans-serif", "font.sans-serif": ["Segoe UI", "Arial", "DejaVu Sans"], "font.size": FS,
    "axes.spines.top": False, "axes.spines.right": False, "axes.spines.left": False, "axes.spines.bottom": False,
    "axes.grid": False, "xtick.color": MUTED, "ytick.color": INK, "xtick.labelsize": FS, "ytick.labelsize": FS,
    "xtick.major.size": 0, "ytick.major.size": 0, "xtick.minor.size": 0, "xtick.major.pad": 3,
    "text.color": INK, "figure.facecolor": "white", "savefig.facecolor": "white", "pdf.fonttype": 42,
    "savefig.dpi": 300, "legend.frameon": False,
})
SEMI = {"fontfamily": "Segoe UI Semibold"}


def header(fig, title):
    fig.text(0.0, 1 - 0.05 / fig.get_figheight(), title, fontsize=10, color=INK, va="top", ha="left", **SEMI)


def top(fig, gap=0.40):
    return 1 - gap / fig.get_figheight()


def save(fig, name):
    for ext in ("pdf", "png"):
        fig.savefig(FIG / f"{name}.{ext}", bbox_inches="tight", pad_inches=0.0)
    plt.close(fig)
    print("wrote", name)


def pill(ax, x0, x1, y, color, lw=7.0, z=2):
    ax.plot([x0, x1], [y, y], color=color, lw=lw, solid_capstyle="round", zorder=z)


def dot(ax, x, y, color, s=46, z=4, marker="o", edge="white"):
    ax.scatter([x], [y], s=s, color=color, edgecolors=edge, linewidths=1.0, zorder=z, marker=marker)


def vgrid(ax, xs, ymin, ymax, labels):
    for v in xs:
        ax.plot([v, v], [ymin, ymax], color=RULE, lw=0.7, zorder=0)
    ax.set_xticks(xs, labels)


# ── replay data ─────────────────────────────────────────────────────────────────────────────────────
ST = D["single_turn"]
FAILM = [p["id"] for p in D["failure_points"]]
HEALTHM = D["control_points"]
ORDER = D["conditions"]
BASE, POINTER, WRONG, ANSWER = ("No note (baseline)", "Pointer to the output", "Pointer to another output",
                                "Answer-informed question")
POINTS = {p["id"]: (p["problem"], f"{p['benchmark']}, {p['run_model'].split(',')[0]}") for p in D["failure_points"]}


def acts(c, points=FAILM):
    return sum(sum(ST[c][m]) for m in points), sum(len(ST[c][m]) for m in points)


def cluster_boot(c, reps=20000):
    k = np.array([sum(ST[c][m]) for m in FAILM])
    n = np.array([len(ST[c][m]) for m in FAILM])
    idx = RNG.integers(0, len(FAILM), size=(reps, len(FAILM)))
    return np.percentile(k[idx].sum(1) / n[idx].sum(1), [2.5, 97.5])


# ── Figure 1: the paper in one picture ──────────────────────────────────────────────────────────────
def fig_teaser():
    fig = plt.figure(figsize=(WIDTH, 2.55))
    header(fig, "The agent had the evidence; pointing at it, without the answer, recovered most of the effect")
    t = top(fig)
    a = fig.add_axes([0.0, 0.04, 0.40, t - 0.06])
    a.set_xlim(0, 100)
    a.set_ylim(0, 100)
    a.axis("off")
    a.add_patch(FancyBboxPatch((0, 0), 100, 100, boxstyle="round,pad=0,rounding_size=2.5", facecolor=TRACK,
                               edgecolor="none"))
    mono = {"fontfamily": "Consolas"}
    a.text(4, 93, "Tool result printed by the agent", fontsize=FS, color=MUTED, va="top", **SEMI)
    a.text(4, 80, "fine-cell reweight partner:", fontsize=FS, color=INK, va="top", **mono)
    a.text(73, 80, "0.2337", fontsize=FS, color=ACC, va="top", **mono, fontweight="bold")
    a.text(4, 70, "partner components check:", fontsize=FS, color=MUTED, va="top", **mono)
    a.text(4, 61, "  AFR0 ... EUR1  (four cells)", fontsize=FS, color=MUTED, va="top", **mono)
    a.text(4, 51, "2x2 partner:", fontsize=FS, color=INK, va="top", **mono)
    a.text(39, 51, "0.1553", fontsize=FS, color=BASE_C, va="top", **mono, fontweight="bold")
    a.text(4, 35, "The agent's next message", fontsize=FS, color=MUTED, va="top", **SEMI)
    a.text(4, 23, "“Everything checks out. Let me write the\nworking ledger and save the result files.”",
           fontsize=FS, color=INK, va="top", linespacing=1.3, style="italic")
    b = fig.add_axes([0.765, 0.08, 0.20, t - 0.16])
    rows = [(BASE, "No note", BASE_C), ("Fresh reader: disagreements", "Best mechanism without the answer", GREY),
            (WRONG, "Pointer to another output", GREY), (POINTER, "Pointer to the disproving output", ACC),
            (ANSWER, "Answer-informed question", INK)]
    n = len(rows)
    vgrid(b, [0, 50, 100], -0.6, n - 0.4, ["0", "50", "100%"])
    for i, (c, lab, col) in enumerate(rows):
        yy = n - 1 - i
        k, m = acts(c)
        pill(b, 0, 100, yy, TRACK, lw=7, z=1)
        pill(b, 0, max(100 * k / m, 0.8), yy, col, lw=7, z=2)
        b.text(104, yy, f"{k}/{m}", va="center", fontsize=FS, color=INK, **SEMI)
        b.text(-0.04, yy, lab, transform=b.get_yaxis_transform(), ha="right", va="center", fontsize=FS, color=INK)
    b.set_xlim(-3, 125)
    b.set_ylim(-0.7, n - 0.3)
    b.set_yticks([])
    fig.text(0.43, t - 0.02, "Replies that followed up the disproving evidence, 13 failure points", ha="left",
             va="top", fontsize=FS, color=MUTED, **SEMI)
    save(fig, "fig1_teaser")


# ── Figure 2: the replay method ─────────────────────────────────────────────────────────────────────
def box(ax, x, y, w, h, title, body, col=INK, fill=TRACK):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=1.0", facecolor=fill,
                                edgecolor="none", zorder=1))
    ax.text(x + 1.2, y + h - 1.6, title, ha="left", va="top", fontsize=FS + 0.5, color=col, **SEMI)
    ax.text(x + 1.2, y + h - 6.4, body, ha="left", va="top", fontsize=FS, color=MUTED, linespacing=1.3)


def arrow(ax, p0, p1):
    ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle="-|>", mutation_scale=9, color=GREY_D, lw=1.0, zorder=2))


def fig1():
    fig = plt.figure(figsize=(WIDTH, 2.15))
    header(fig, "From a failed run to a controlled replay of the step where it failed")
    ax = fig.add_axes([0.0, 0.0, 1.0, top(fig)])
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 35)
    ax.axis("off")
    w, g = 18.4, 2.0
    xs = [i * (w + g) for i in range(5)]
    steps = [
        ("1  Trace", "compare each failed\noutput with the\nreference; find the\nsmallest change that\nremoves the error", INK),
        ("2  Locate", "read the transcript\nback to the step where\nthat change was due;\nnote what the agent\nhad printed and read", INK),
        ("3  Capture", "take the exact model\nrequest sent right\nafter the disproving\noutput: system prompt,\ntools, every message", INK),
        ("4  Change one thing", "append one note,\nor change the effort,\nand sample the next\nturn 6 times with\nClaude Haiku 5.5", ACC),
        ("5  Score", "a judge model reads\nthe turn's text and\ncode, never the\ncondition, against a\ncriterion fixed first", ACC),
    ]
    for x, (t, b, c) in zip(xs, steps):
        box(ax, x, 11, w, 23.5, t, b, col=c)
    for x in xs[:-1]:
        arrow(ax, (x + w + 0.15, 22.5), (x + w + g - 0.15, 22.5))
    ax.text(0, 6.5, "104 failed outputs  →  13 failure points, plus 3 points from passing runs as controls"
            f"  →  {len(ORDER)} conditions × 6 samples per point", fontsize=FS, color=INK, va="center")
    ax.text(0, 1.5, "Steps 1 and 2 are the tracing (Section 3.3); steps 3 to 5 are the replay (Section 3.4).",
            fontsize=FS, color=MUTED, va="center")
    save(fig, "fig2_method")


# ── Figure 2: where failures occur ──────────────────────────────────────────────────────────────────
AGENT = ("default method used without a test", "assumption never checked per unit",
         "disproving number on screen, not acted on")


def fig2():
    rows_ = list(csv.DictReader(open(ROOT / "data" / "failure_classification.csv", encoding="utf-8")))
    c1, c2 = Counter(r["primary_class"] for r in rows_), Counter(r["second_rater_class"] for r in rows_)
    t1, t2 = sum(c1[k] for k in AGENT), sum(c2[k] for k in AGENT)
    fig = plt.figure(figsize=(WIDTH, 2.5))
    header(fig, "Most agent failures were untested defaults and unit-level assumptions")
    t = top(fig)
    a = fig.add_axes([0.375, 0.20, 0.26, t - 0.22])
    names = {"default method used without a test": "Default method, no test of its assumption",
             "assumption never checked per unit": "Assumption checked only in aggregate",
             "disproving number on screen, not acted on": "Disproving number on screen, not acted on"}
    yy = 2
    vgrid(a, [0, 20, 40, 60], -0.6, 2.6, ["0", "20", "40", "60%"])
    for k in AGENT:
        p1, p2 = 100 * c1[k] / t1, 100 * c2[k] / t2
        lo, hi = min(p1, p2), max(p1, p2)
        col, light = (ACC, ACC_L) if k == AGENT[0] else (GREY_D, GREY_L)
        pill(a, lo, hi, yy, light, lw=9)
        dot(a, p1, yy, col, s=40)
        dot(a, p2, yy, col, s=34, marker="D")
        a.text(hi + 2.5, yy, f"{lo:.0f} to {hi:.0f}%", va="center", fontsize=FS, color=col, **SEMI)
        a.text(-0.02, yy, names[k], transform=a.get_yaxis_transform(), ha="right", va="center", fontsize=FS,
               color=INK)
        yy -= 1
    a.set_xlim(-1, 82)
    a.set_ylim(-0.6, 2.6)
    a.set_yticks([])
    fig.text(0.0, 0.0, f"Share of the {min(t1, t2)} to {max(t1, t2)} failures attributable to the agent.\n"
             "Circle: primary classification. Diamond: independent rater.", fontsize=FS, color=MUTED, va="bottom",
             linespacing=1.2)
    b = fig.add_axes([0.665, 0.13, 0.28, t - 0.15])
    b.set_aspect("equal")
    b.axis("off")
    on = AGENT[2]
    gb = [r for r in rows_ if r["benchmark"] == "GeneBench-Pro"]
    n_p = sum(r["primary_class"] == on for r in gb)
    n_c = sum(r["primary_class"] != on and r["contributing_cause"] == on for r in gb)
    cells = ["P"] * n_p + ["C"] * n_c + ["N"] * (len(gb) - n_p - n_c)
    fc = {"P": ACC, "C": ACC_L, "N": "white"}
    ec = {"P": ACC, "C": ACC_L, "N": GREY}
    for i, c in enumerate(cells):
        r, q = divmod(i, 10)
        b.add_patch(FancyBboxPatch((q * 1.12, -r * 1.12), 0.88, 0.88, boxstyle="round,pad=0,rounding_size=0.2",
                                   facecolor=fc[c], edgecolor=ec[c], lw=0.9))
    b.text(0, 1.5, f"{n_p + n_c} of {len(gb)} failed GeneBench-Pro keys:\nthe agent had printed a number\nthat contradicted its answer", fontsize=FS, color=INK, va="bottom", linespacing=1.25)
    for yy, kind, label in ((-7.0, "P", f"{n_p} as the primary cause"), (-8.25, "C", f"{n_c} as a contributing cause"),
                            (-9.5, "N", f"{len(gb) - n_p - n_c} not on screen")):
        b.add_patch(FancyBboxPatch((0, yy - 0.42), 0.84, 0.84, boxstyle="round,pad=0,rounding_size=0.18",
                                   facecolor=fc[kind], edgecolor=ec[kind], lw=0.9))
        b.text(1.4, yy, label, va="center", fontsize=FS, color=INK)
    b.set_xlim(-0.1, 11.3)
    b.set_ylim(-10.2, 5.2)
    save(fig, "fig3_taxonomy")


# ── Figure 3: what the model states when asked, against what it did in the run ──────────────────────
def fig3():
    rows = N.PROBES
    fig = plt.figure(figsize=(WIDTH, 0.36 * len(rows) + 0.7))
    header(fig, "Asked directly, each model stated the fact; in the run, the same model used it far less often")
    t = top(fig)
    a = fig.add_axes([0.40, 0.13, 0.50, t - 0.16])
    n = len(rows)
    vgrid(a, [0, 25, 50, 75, 100], -0.6, n - 0.4, ["0", "25", "50", "75", "100%"])
    for i, r in enumerate(rows):
        yy = n - 1 - i
        ka, na = r["asked"]
        kr, nr = r["run"]
        pa, pr = 100 * ka / na, 100 * kr / nr
        pill(a, min(pa, pr), max(pa, pr), yy, GREY_L, lw=3, z=1)
        dot(a, pr, yy, BASE_C, s=52, marker="s")
        dot(a, pa, yy, ACC, s=56)
        a.text(pa + (4 if pa >= pr else -4), yy + 0.02, f"{ka}/{na}", ha="left" if pa >= pr else "right",
               va="center", fontsize=FS, color=ACC, **SEMI)
        a.text(pr + (-4 if pa >= pr else 4), yy + 0.02, f"{kr}/{nr}", ha="right" if pa >= pr else "left",
               va="center", fontsize=FS, color=BASE_C, **SEMI)
        a.text(-0.03, yy + 0.16, r["problem"], transform=a.get_yaxis_transform(), ha="right", va="center",
               fontsize=FS, color=INK, **SEMI)
        a.text(-0.03, yy - 0.2, r["model"], transform=a.get_yaxis_transform(), ha="right", va="center",
               fontsize=FS, color=MUTED)
    a.set_xlim(-12, 112)
    a.set_ylim(-0.6, n - 0.3)
    a.set_yticks([])
    fig.text(0.40, 0.02, "●", fontsize=FS + 1, color=ACC)
    fig.text(0.42, 0.02, "asked directly, outside the task", fontsize=FS, color=MUTED)
    fig.text(0.68, 0.02, "■", fontsize=FS + 1, color=BASE_C)
    fig.text(0.70, 0.02, "in the run or its replay", fontsize=FS, color=MUTED)
    save(fig, "fig4_knowing")


# ── Figure 4: when the disproving number appeared ───────────────────────────────────────────────────
RASTER_NAMES = {"CRISPRi": "CRISPR interference screen", "MVMR": "Mendelian randomization", "admixture": "Admixture dating",
                "carrier": "Carrier-frequency estimation", "Hi-C": "Chromatin-contact loop strength",
                "txr1": "Treatment-effect estimation", "scRNA": "Single-cell expression QTL",
                "structural": "Structural-variant association"}
RUN_NAMES = {"DeepSeek t2": "DeepSeek V4.1 Flash, trial 2", "DeepSeek t3": "DeepSeek V4.1 Flash, trial 3",
             "GPT-6 Astra": "GPT-6 Astra"}


SHORT_PROB = {"CRISPRi": "CRISPR screen", "MVMR": "Mendelian randomization", "admixture": "Admixture dating",
              "carrier": "Carrier frequency", "Hi-C": "Chromatin contacts", "txr1": "Treatment effect",
              "scRNA": "Single-cell eQTL", "structural": "Structural variant"}
SHORT_RUN = {"DeepSeek t2": "DeepSeek trial 2", "DeepSeek t3": "DeepSeek trial 3", "GPT-6 Astra": "GPT-6 Astra"}


def fig4():
    rows = N.RASTER
    fig = plt.figure(figsize=(WIDTH, 2.8))
    header(fig, "The disproving number was printed with most of the run still ahead")
    t = top(fig)
    ax = fig.add_axes([0.33, 0.06, 0.65, t - 0.08])
    n = len(rows)
    vgrid(ax, [0, 20, 40, 60, 80, 100], -0.6, n - 0.3, ["step 0", "20", "40", "60", "80", "100"])
    for i, (label, steps, ev, _dis) in enumerate(rows):
        yy = n - 1 - i
        pill(ax, 0, steps, yy, TRACK, lw=6, z=1)
        pill(ax, ev[0], steps, yy, GREY_L, lw=6, z=1.5)
        for e in ev:
            dot(ax, e, yy, ACC, s=40, z=4)
        ax.text(steps + 2.0, yy, f"{steps}", va="center", fontsize=FS, color=MUTED)
        prob, run = label.split(", ")
        ax.text(-0.015, yy, f"{SHORT_PROB[prob]}, {SHORT_RUN[run]}", transform=ax.get_yaxis_transform(), ha="right",
                va="center", fontsize=FS, color=INK)
    ax.set_xlim(-2, 118)
    ax.set_ylim(-0.7, n - 0.3)
    ax.set_yticks([])
    lx, ly = 66, n - 1.1
    dot(ax, lx, ly, ACC, s=40)
    ax.text(lx + 2.4, ly, "disproving number printed", va="center", fontsize=FS, color=ACC)
    pill(ax, lx - 1.2, lx + 1.2, ly - 0.8, GREY_L, lw=6)
    ax.text(lx + 2.4, ly - 0.8, "steps after the first print", va="center", fontsize=FS, color=MUTED)
    save(fig, "fig5_timing")


# ── Figure 5: reasoning at the reading turn ─────────────────────────────────────────────────────────
def fig5():
    fig = plt.figure(figsize=(WIDTH, 2.65))
    header(fig, "More reasoning fixed one problem and did not help across the failure points")
    t = top(fig)
    a = fig.add_axes([0.34, 0.10, 0.23, t - 0.14])
    rows = N.FEEDER_SCHEDULES + [("Claude Sonnet 5.5, high throughout", *N.SONNET_HIGH)]
    names = {"high throughout": "High throughout", "xhigh throughout": "Extra-high throughout",
             "max on the first reply only": "Maximum on the first reply only",
             "re-ask an ending reply at max": "Re-ask an ending reply at maximum",
             "max throughout": "Maximum throughout", "high, then max after it": "High, then maximum after it",
             "Claude Sonnet 5.5, high throughout": "Claude Sonnet 5.5, high"}
    n = len(rows)
    vgrid(a, [0, 50, 100], -0.8, n - 0.4, ["0", "50", "100%"])
    for i, (name, k, m) in enumerate(rows):
        yy = n - 1 - i - (0.3 if name.startswith("Claude") else 0)
        col = BASE_C if name == "high throughout" else (ACC if "then max" in name else GREY_D)
        pill(a, 0, 100, yy, TRACK, lw=6, z=1)
        pill(a, 0, max(100 * k / m, 0.8), yy, BASE_C if col == BASE_C else (ACC if col == ACC else GREY), lw=6, z=2)
        a.text(105, yy, f"{k}/{m}", va="center", fontsize=FS, color=col if col != GREY_D else MUTED, **SEMI)
        a.text(-0.04, yy, names[name], transform=a.get_yaxis_transform(), ha="right", va="center", fontsize=FS,
               color=INK)
    a.set_xlim(-3, 122)
    a.set_ylim(-0.9, n - 0.2)
    a.set_yticks([])
    a.text(-0.04, n - 0.05, "Load series: forks graded correct", transform=a.get_yaxis_transform(), ha="right",
           va="bottom", fontsize=FS, color=MUTED, **SEMI)
    b = fig.add_axes([0.78, 0.10, 0.19, t - 0.14])
    E = list(csv.DictReader(open(ROOT / "data" / "reasoning_after_results.csv", encoding="utf-8")))
    groups = [("clean_numeric", "After a clean\nnumeric result"), ("traceback", "After a\ntraceback")]
    vals = [[int(r["reasoning_chars"]) for r in E if r["result"] == g] for g, _ in groups]
    for j, ((g, lab), v) in enumerate(zip(groups, vals)):
        yy = 1 - j
        jit = RNG.uniform(-0.18, 0.18, len(v))
        b.scatter(np.clip(v, 1, None), yy + jit, s=7, color=GREY, zorder=2, linewidths=0)
        med = float(np.median(v))
        b.plot([med, med], [yy - 0.3, yy + 0.3], color=INK, lw=1.6, zorder=3)
        b.text(-0.06, yy, lab, transform=b.get_yaxis_transform(), ha="right", va="center", fontsize=FS, color=INK,
               linespacing=1.15)
        b.text(med, yy + 0.34, f"median {med:,.0f}", ha="center", va="bottom", fontsize=FS, color=INK, **SEMI)
    b.set_xscale("log")
    b.xaxis.set_minor_locator(mpl.ticker.NullLocator())
    vgrid(b, [10, 100, 1000, 10000], -0.5, 1.5, ["10", "100", "1k", "10k"])
    b.set_xlim(5, 20000)
    b.set_ylim(-0.55, 1.75)
    b.set_yticks([])
    b.text(5, 1.72, "Reasoning characters,\nlive runs", fontsize=FS, color=MUTED, va="bottom", linespacing=1.15, **SEMI)
    save(fig, "fig6_reasoning")


# ── Figure 6: steering at the failure points (main result) ──────────────────────────────────────────
def fig6():
    n = len(ORDER)
    fig = plt.figure(figsize=(WIDTH, 0.23 * n + 0.8))
    header(fig, "Pointing at the disproving output raised follow-up; every other prompt short of the answer did not")
    t = top(fig)
    a = fig.add_axes([0.30, 0.08, 0.53, t - 0.10])
    b = fig.add_axes([0.87, 0.08, 0.13, t - 0.10])
    base_rate = 100 * acts(BASE)[0] / acts(BASE)[1]
    vgrid(a, [0, 25, 50, 75, 100], -0.6, n - 0.4, ["0", "25", "50", "75", "100%"])
    a.plot([base_rate, base_rate], [-0.6, n - 0.4], color=BASE_C, lw=0.8, ls=(0, (2, 2.5)), zorder=0.5)
    vgrid(b, [0, 20], -0.6, n - 0.4, ["0", "20%"])
    for i, c in enumerate(ORDER):
        yy = n - 1 - i
        k, m = acts(c)
        lo, hi = cluster_boot(c)
        col, light, mk = GREY_D, GREY_L, "o"
        if c == BASE:
            col, light, mk = BASE_C, BASE_L, "s"
        elif c == POINTER:
            col, light = ACC, ACC_L
        elif c == ANSWER:
            col, mk = INK, "D"
        pill(a, lo * 100, hi * 100, yy, light, lw=6)
        dot(a, 100 * k / m, yy, col, s=52, marker=mk)
        a.text(hi * 100 + 2.0, yy, f"{k}/{m}", va="center", fontsize=FS, color=col if col != GREY_D else MUTED, **SEMI)
        strong = c in (BASE, POINTER, WRONG, ANSWER)
        a.text(-0.02, yy, c, transform=a.get_yaxis_transform(), ha="right", va="center", fontsize=FS,
               color=INK, **(SEMI if strong else {}))
        hk, hn = acts(c, HEALTHM)
        if hn and c != ANSWER:  # at the control points that arm received the generic reminder; not defined there
            dot(b, 100 * hk / hn, yy, INK if hk else GREY_D, s=32)
            b.text(23, yy, f"{hk}/{hn}", va="center", fontsize=FS, color=INK if hk else MUTED)
    a.text(base_rate + 1.2, n - 0.45, "baseline", ha="left", va="bottom", fontsize=FS, color=BASE_C)
    a.set_xlim(-2, 108)
    a.set_ylim(-0.6, n - 0.15)
    a.set_yticks([])
    b.set_xlim(-3, 38)
    b.set_ylim(-0.6, n - 0.15)
    b.set_yticks([])
    b.text(0, n - 0.45, "rework", ha="left", va="bottom", fontsize=FS, color=MUTED, **SEMI)
    save(fig, "fig7_steering")


# ── Figure 7: pointer and wrong pointer, per failure point ──────────────────────────────────────────
def fig7():
    cols = [BASE, WRONG, POINTER, ANSWER]
    short = {BASE: "Baseline", WRONG: "Other\noutput", POINTER: "Pointer", ANSWER: "Answer-\ninformed"}
    fig = plt.figure(figsize=(WIDTH, 3.45))
    header(fig, "The pointer's effect came from naming the disproving output, at almost every point")
    ax = fig.add_axes([0.46, 0.0, 0.53, top(fig, 0.36)])
    nr = len(FAILM)
    for i, mo in enumerate(FAILM):
        yy = -i
        for j, c in enumerate(cols):
            v = sum(ST[c][mo])
            col = BASE_C if c == BASE else (ACC if c == POINTER else GREY_D)
            pill(ax, j * 1.5, j * 1.5 + 1.0, yy, TRACK, lw=6, z=1)
            if v:
                pill(ax, j * 1.5, j * 1.5 + v / 6, yy, col if c != ANSWER else INK, lw=6, z=2)
            ax.text(j * 1.5 + 1.12, yy, str(v), va="center", fontsize=FS, color=INK if v else MUTED)
        prob, where = POINTS[mo]
        ax.text(-0.2, yy, f"{prob.replace(' (', ', ').rstrip(')')}, {where.split(', ')[-1]}", ha="right", va="center",
                fontsize=FS, color=INK)
    for j, c in enumerate(cols):
        k, n = acts(c)
        ax.text(j * 1.5, 0.75, short[c], ha="left", va="bottom", fontsize=FS, color=INK, linespacing=1.1, **SEMI)
        ax.text(j * 1.5, -nr - 0.15, f"{k}/{n}", ha="left", va="center", fontsize=FS, color=INK, **SEMI)
    ax.text(-0.2, -nr - 0.15, "All 13 points", ha="right", va="center", fontsize=FS, color=INK, **SEMI)
    ax.plot([0, 5.9], [-nr + 0.4, -nr + 0.4], color=RULE, lw=0.8)
    ax.set_xlim(-0.1, 6.1)
    ax.set_ylim(-nr - 0.6, 1.7)
    ax.axis("off")
    save(fig, "fig8_points")


# ── Figure 8: predictions written in a plan ─────────────────────────────────────────────────────────
def fig8():
    fig = plt.figure(figsize=(WIDTH, 1.95))
    header(fig, "Asked for a prediction in its plan, the agent wrote a range its result could not leave")
    t = top(fig)
    a = fig.add_axes([0.27, 0.16, 0.42, t - 0.20])
    T = N.TASK1
    rows = [("Prediction, plan 1", T["plan prior 1"], GREY, MUTED),
            ("Prediction, plan 2", T["plan prior 2"], GREY, MUTED),
            ("Typical value, asked directly", T["bare recall"], ACC, ACC),
            ("The agent's result", T["agent result"], BASE_C, BASE_C)]
    a.set_xscale("log")
    vgrid(a, [100, 1000, 10000], -0.6, len(rows) - 0.4, ["100", "1,000", "10,000"])
    a.xaxis.set_minor_locator(mpl.ticker.NullLocator())
    for i, (name, (lo, hi), fill, tc) in enumerate(rows):
        yy = len(rows) - 1 - i
        pill(a, lo, hi, yy, fill, lw=7)
        a.text(hi * 1.2, yy, f"{lo:,} to {hi:,}", ha="left", va="center", fontsize=FS, color=tc, **SEMI)
        a.text(-0.02, yy, name, transform=a.get_yaxis_transform(), ha="right", va="center", fontsize=FS, color=INK)
    a.set_xlim(70, 150000)
    a.set_ylim(-0.6, len(rows) - 0.35)
    a.set_yticks([])
    a.text(70, -1.25, "Target genes per replicate (log scale)", fontsize=FS, color=MUTED, va="center")
    b = fig.add_axes([0.78, 0.16, 0.21, t - 0.20])
    A = N.ARRHENIUS
    b.set_xscale("log")
    vgrid(b, [1, 10, 100], -0.8, 1.6, ["1×", "10×", "100×"])
    b.xaxis.set_minor_locator(mpl.ticker.NullLocator())
    pill(b, A["bare recall"][0], A["bare recall"][1], 1, ACC, lw=7)
    b.text(A["bare recall"][1] * 1.4, 1, "asked directly", va="center", fontsize=FS, color=ACC, **SEMI)
    dot(b, A["observed"], 0, BASE_C, s=60, marker="D")
    b.text(A["observed"] / 1.45, 0, "in the data", va="center", ha="right", fontsize=FS, color=BASE_C, **SEMI)
    b.set_xlim(0.75, 400)
    b.set_ylim(-0.8, 1.6)
    b.set_yticks([])
    b.text(0.75, -1.25, "Rate ratio per 5 °C (log scale)", fontsize=FS, color=MUTED, va="center")
    save(fig, "fig9_predictions")


# ── Appendix figure: multi-turn and early forks ─────────────────────────────────────────────────────
def ring(ax, x, y, color, filled, s=58):
    ax.scatter([x], [y], s=s, facecolors=color if filled else "white", edgecolors=color, linewidths=1.2, zorder=4)


def figA1():
    fig = plt.figure(figsize=(WIDTH, 2.9))
    header(fig, "Over six turns, all readers' questions helped where the evidence was a printed disagreement")
    t = top(fig)
    MT = D["multi_turn"]
    arms = [(BASE, "Baseline", BASE_C), ("Fresh readers: all questions", "All readers", GREY_D),
            (ANSWER, "Answer-informed", INK)]
    mom = [("carrier-frequency/deepseek", "Carrier frequency"), ("single-cell-eqtl/astra", "Single-cell eQTL"),
           ("admixture-dating/astra", "Admixture dating"), ("qtl-multiparent/astra", "QTL, multiparent")]
    a = fig.add_axes([0.0, 0.02, 0.47, t - 0.03])
    a.set_xlim(0, 10)
    a.set_ylim(-0.8, 4.6)
    a.axis("off")
    for j, (_, lab, col) in enumerate(arms):
        a.text(3.3 + j * 2.3, 3.9, lab, ha="left", va="center", fontsize=FS, color=col, **SEMI)
    for i, (m, lab) in enumerate(mom):
        yy = 3.1 - i * 0.85
        a.text(0.0, yy, lab, va="center", fontsize=FS, color=INK, **SEMI)
        for j, (arm, _, col) in enumerate(arms):
            for k, v in enumerate(MT[arm][m]):
                ring(a, 3.45 + j * 2.3 + k * 0.5, yy, col, bool(v))
    tot = "; ".join(f"{lab.lower()} {sum(sum(v) for v in MT[arm].values())}/{sum(len(v) for v in MT[arm].values())}"
                    for arm, lab, _ in arms)
    a.text(0.0, -0.55, "Six-turn forks. Totals:\n" + tot, fontsize=FS, color=MUTED, va="center", linespacing=1.2)
    b = fig.add_axes([0.52, 0.02, 0.48, t - 0.03])
    b.set_xlim(0, 10)
    b.set_ylim(-0.8, 4.6)
    b.axis("off")
    E = D["early_list"]
    short = {"Structural-variant association": "Structural variant", "QTL mapping, multiparent cross": "QTL, multiparent",
             "CRISPR interference screen": "CRISPRi screen", "Treatment-effect estimation": "Treatment effect",
             "Carrier-frequency estimation": "Carrier frequency", "Mendelian randomization": "Mendelian rand.",
             "Single-cell expression QTL": "Single-cell eQTL", "Chromatin-contact loop strength": "Chromatin contacts",
             "Admixture dating": "Admixture dating"}
    named = {q["key"] for q in E["problems"] if q["list_named_decisive_check"]}
    b.text(3.7, 3.95, "Baseline", fontsize=FS, color=BASE_C, va="center", **SEMI)
    b.text(5.5, 3.95, "Given a list", fontsize=FS, color=GREY_D, va="center", **SEMI)
    b.text(7.9, 3.95, "Named the\ncheck", fontsize=FS, color=MUTED, va="center", linespacing=1.05)
    for i, q in enumerate(E["problems"]):
        p = q["key"]
        yy = 3.3 - i * 0.405
        b.text(0.0, yy, short[q["problem"]], va="center", fontsize=FS, color=INK)
        for k, v in enumerate(E[BASE][p]):
            ring(b, 3.85 + k * 0.42, yy, BASE_C, bool(v), s=40)
        if E["Given a list of checks"][p]:
            for k, v in enumerate(E["Given a list of checks"][p]):
                ring(b, 5.65 + k * 0.42, yy, GREY_D, bool(v), s=40)
        else:
            b.text(5.5, yy, "did not run", va="center", fontsize=FS, color=MUTED)
        if p in named:
            b.text(8.35, yy, "yes", va="center", ha="center", fontsize=FS, color=INK)
    tb = sum(sum(v) for v in E[BASE].values()), sum(len(v) for v in E[BASE].values())
    tl = (sum(sum(v) for v in E["Given a list of checks"].values()),
          sum(len(v) for v in E["Given a list of checks"].values()))
    b.text(0.0, -0.55, f"Forks continued to the end. Totals:\nbaseline {tb[0]}/{tb[1]}; given a list {tl[0]}/{tl[1]}",
           fontsize=FS, color=MUTED, va="center", linespacing=1.2)
    save(fig, "figA1_multiturn")


if __name__ == "__main__":
    for f in (fig_teaser, fig1, fig2, fig3, fig4, fig5, fig6, fig7, fig8, figA1):
        f()
