"""Values the figures use that are not per-sample replay outcomes: counts from the reasoning-effort study, transcript
step positions, values printed by the agents, and the probe ranges. Each is documented in the paper where it is used.
"""

# Electrical-load time series (our probe set): Claude Haiku 5.5 forks from the turn after the agent found the gap,
# continued to the end and graded by the problem's grader. (schedule, correct, forks)
FEEDER_SCHEDULES = [
    ("high throughout", 1, 15),
    ("xhigh throughout", 5, 15),
    ("max on the first reply only", 10, 15),
    ("re-ask an ending reply at max", 10, 15),
    ("max throughout", 12, 15),
    ("high, then max after it", 15, 15),
]
SONNET_HIGH = (9, 10)  # Claude Sonnet 5.5, effort high throughout: correct, forks

# Twelve failed GeneBench-Pro runs: (problem, run, number of transcript steps, steps at which the agent printed the
# disproving number, steps at which it dismissed it). Step indices were located by searching each transcript for the
# printed value.
RASTER = [
    ("CRISPRi, DeepSeek t2", 22, [11], [15]),
    ("MVMR, DeepSeek t2", 35, [24], [33]),
    ("admixture, DeepSeek t3", 37, [7, 13, 20], [14]),
    ("carrier, DeepSeek t3", 43, [26, 35], [36]),
    ("Hi-C, DeepSeek t3", 48, [18, 23], [26]),
    ("txr1, DeepSeek t2", 50, [32, 33], []),
    ("carrier, DeepSeek t2", 54, [13, 24, 42], [43]),
    ("CRISPRi, DeepSeek t3", 60, [13, 17], []),
    ("txr1, DeepSeek t3", 87, [40], [59]),
    ("scRNA, DeepSeek t3", 94, [42, 65], [66]),
    ("MVMR, GPT-6 Astra", 102, [31], []),
    ("structural, DeepSeek t2", 107, [19, 21, 86], [76, 87]),
]

# Predictions in plans (BixBench3 task 1, GPT-6.1 Sol) and the reaction-kinetics probe (GPT-6.1 Sol).
TASK1 = {
    "plan prior 1": (1000, 20000),
    "plan prior 2": (100, 20000),
    "bare recall": (2000, 5000),
    "agent result": (3594, 6904),
}
ARRHENIUS = {"bare recall": (1.3, 1.7), "observed": 87.0}

# Knowledge probes: the same model asked directly, outside the task (asked: samples stating the fact), against what it
# did at the corresponding point in its run or in the replay of that point (run: samples or runs using it).
PROBES = [
    {"problem": "Repeated survey", "model": "Claude Haiku 5.5", "asked": (10, 10), "run": (3, 5),
     "asked_what": "a 1 to 5 range check cannot detect a reverse-coded item",
     "run_what": "live runs at the same settings that detected the reversal (the other 2 ran the range check)"},
    {"problem": "Electrical-load series", "model": "Claude Haiku 5.5", "asked": (10, 10), "run": (9, 30),
     "asked_what": "raised the time convention of the timestamps",
     "run_what": "first replies at the decision turn that split the hourly profile by period (replay)"},
    {"problem": "Admixture dating", "model": "Claude Haiku 5.5", "asked": (3, 3), "run": (1, 12),
     "asked_what": "check the chromosomes before pooling",
     "run_what": "baseline replies at the two admixture failure points that compared them (replay)"},
    {"problem": "Carrier frequency", "model": "Claude Haiku 5.5", "asked": (3, 3), "run": (2, 6),
     "asked_what": "a check that moves the estimate by half must be explained first",
     "run_what": "baseline replies at the carrier failure point that did so (replay)"},
    {"problem": "Reaction kinetics", "model": "GPT-6.1 Sol", "asked": (3, 3), "run": (0, 4),
     "asked_what": "a typical rate ratio of 1.3 to 1.7 per 5 degrees",
     "run_what": "runs that revised the units after an 87-fold jump"},
    {"problem": "DamID target calling", "model": "GPT-6.1 Sol", "asked": (3, 3), "run": (0, 3),
     "asked_what": "about 0.15 reads per fragment: the data are sparse",
     "run_what": "plans that combined the read and fragment counts"},
]

# Per-(haplotype, chromosome) ancestry fractions printed by Claude Haiku 5.5 in the forks told to compute them (four
# of the ten forks printed four decimals, the other six the same values to three). DeepSeek V4.1 Flash trial 2
# printed its own table, h1 0.7911, 0.4823, 0.2128, 0.8133 and h2 0.5583, 0.0237, 0.8786, 0.4185, which the paper does
# not use.
POPGEN = {"h1": [0.7934, 0.4882, 0.2107, 0.8154], "h2": [0.5519, 0.0234, 0.8798, 0.4139]}
