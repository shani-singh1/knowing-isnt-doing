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

# Per-(haplotype, chromosome) ancestry fractions printed by Claude Haiku 5.5 at the admixture-dating failure point.
POPGEN = {"h1": [0.79, 0.49, 0.21, 0.81], "h2": [0.55, 0.02, 0.88, 0.41]}
