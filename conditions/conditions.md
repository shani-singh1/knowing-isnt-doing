# Conditions at the failure points

Each condition changes one thing in the captured request. Notes are appended after the last tool result as a `[System]` line. Reader questions are produced per sample by a separate Claude Haiku 5.5 call (effort high) and delivered as `[System] A reviewer who read only the task and your last output asks: <question>`; a reader that answers NONE adds nothing. In the reader prompts, `{task}`, `{code}`, `{allcode}` and `{output}` are the task text, the last code cell, all code cells so far, and the last code output.

## No note (baseline)

Nothing changes. Reasoning effort high.

## Maximum reasoning effort

Reasoning effort maximum; output limit 64,000 tokens.

## Generic reminder

> [System] Before you continue: is there anything in what you have computed so far that you have not yet accounted for?

## Self-review prompt

> [System] Before you continue: what is the one question a careful reviewer would ask about the output you just got, before letting you build on it? Ask it, then answer it from the data.

## Fresh reader: open question

```
A data analyst is working on this task:
<task>
{task}
</task>

Their latest step ran this code:
<code>
{code}
</code>

and it printed:
<output>
{output}
</output>

You are a careful reviewer looking over their shoulder. What is the single most important question you would ask about this output before letting them build on it? Ask about something the output itself shows or fails to show. Do not solve the task, do not give numbers they have not computed, and do not ask about formatting or presentation. Reply with the question only, in one or two sentences.
```

## Fresh reader: disagreements

```
A data analyst is working on this task:
<task>
{task}
</task>

Their latest step ran this code:
<code>
{code}
</code>

and it printed:
<output>
{output}
</output>

Look in the output only for evidence that disagrees with itself or with the analysis built on it:
1. two numbers that estimate the same thing and disagree;
2. a test or diagnostic in the output that says the model being used does not fit;
3. a count of units that failed, are empty, or behave differently from the rest;
4. one part of the data (a group, unit, period or source) whose value disagrees with the other parts.
If there is such evidence, ask the analyst one question about the largest disagreement, quoting the numbers as printed. Do not solve the task and do not give numbers that are not in the output. If there is none, reply NONE.
```

## Fresh reader: largest impact

```
A data analyst is working on this task:
<task>
{task}
</task>

Their latest step ran this code:
<code>
{code}
</code>

and it printed:
<output>
{output}
</output>

Work through these steps privately, then write only the final question.
1. Which quantities will the analyst's answer to the task rest on?
2. For each of them, collect the evidence in this output that disagrees with how the analysis treats it:
   - two numbers that estimate the same thing and disagree;
   - a test or diagnostic saying the model being used does not fit;
   - a count of units that failed, are empty, or behave differently from the rest;
   - one part of the data (a group, unit, period or source) whose value disagrees with the others;
   - a quantity pooled over parts it could differ across (groups, units, periods, sources, batches) with no per-part view
     printed.
3. Pick the single item that would change the analyst's ANSWER the most if it turned out the way the evidence points. A
   problem that would leave the answer unchanged does not qualify.
Then ask the analyst one question about that item, quoting the numbers as printed, or naming the per-part breakdown that is
missing. Do not solve the task and do not give numbers that are not in the output. If no item would change the answer, reply
NONE.
```

## Fresh reader: assumptions

```
A data analyst is working on this task:
<task>
{task}
</task>

The code they have run so far, in order:
<code>
{allcode}
</code>

Their latest step printed:
<output>
{output}
</output>

Work privately, then write only the final question.
1. List what this analysis takes as given about the data. Include:
   - which real thing each label, code or identifier stands for;
   - how values are coded, and their units;
   - that a quantity or relationship is the same in every group, unit, period or source it is pooled over;
   - that a field means what its name says;
   - that rows are what they appear to be.
2. Pick the one given that is most likely to be false for data like these AND would change the answer to the task if it were.
3. Ask the analyst for the one observation in their data that would show it is false. Name the computation, for example a
   breakdown by part, a comparison or a count, not a general worry.
Do not solve the task and do not state numbers that are not in the output.
```

## Fresh readers: all questions

The questions returned by the disagreements, assumptions and largest-impact readers, delivered as one numbered list (readers that answered NONE are left out).

## Pointer to the output

One note per failure point. It names the printed output by the agent's own label and says nothing about it.

- **Admixture dating (GeneBench-Pro, DeepSeek V4.1 Flash run):** [System] Before you continue, look again at the per-chrom A fraction lines in the output you just got.
- **Admixture dating (GeneBench-Pro, GPT-6 Astra run):** [System] Before you continue, look again at the per-chromosome results in the output you just got.
- **Chromatin-contact loop strength (GeneBench-Pro, DeepSeek V4.1 Flash run):** [System] Before you continue, look again at the neighborhood raw counts in the output you just got.
- **Mendelian randomization, residual LD (GeneBench-Pro, DeepSeek V4.1 Flash run):** [System] Before you continue, look again at the perm p result in the output you just got.
- **Mendelian randomization, heterogeneity (GeneBench-Pro, GPT-6 Astra run):** [System] Before you continue, look again at generalized_IVW_Q in the output you just got.
- **QTL mapping, multiparent cross (GeneBench-Pro, GPT-6 Astra run):** [System] Before you continue, look again at heldout_concordance in the output you just got.
- **Carrier-frequency estimation (GeneBench-Pro, DeepSeek V4.1 Flash run):** [System] Before you continue, look again at the fine-cell reweight partner line in the output you just got.
- **RNA-seq read counting (BixBench3 task 12):** [System] Before you continue, look again at all_zero_loci in the output you just got.
- **Treatment-effect estimation (GeneBench-Pro, DeepSeek V4.1 Flash run):** [System] Before you continue, look again at the add act line in the output you just got.
- **Structural-variant association (GeneBench-Pro, DeepSeek V4.1 Flash run):** [System] Before you continue, look again at the + clinic_stratum & stream line in the output you just got.
- **Gene Ontology summary (BixBench3 task 16):** [System] Before you continue, look again at root_only_genes in the output you just got.
- **Single-cell expression QTL (GeneBench-Pro, GPT-6 Astra run):** [System] Before you continue, look again at rho_pooled_by_g in the output you just got.
- **CRISPR interference screen (GeneBench-Pro, GPT-6 Astra run):** [System] Before you continue, look again at the guide_gc_frac correlations in the output you just got.

## Answer-informed question

One note per failure point, written from the tracing with knowledge of the error. A measuring device for an upper bound, not an intervention. The control points receive the generic reminder under this condition.

- **Admixture dating (GeneBench-Pro, DeepSeek V4.1 Flash run):** [System] Before you continue: is each haplotype's ancestry-A fraction consistent from one chromosome to the next, or does one chromosome disagree with the others?
- **Admixture dating (GeneBench-Pro, GPT-6 Astra run):** [System] Before you continue: is each haplotype's ancestry-A fraction consistent from one chromosome to the next, or does one chromosome disagree with the others?
- **Chromatin-contact loop strength (GeneBench-Pro, DeepSeek V4.1 Flash run):** [System] Before you continue: are there other pixels near the target that are high in case but not in control, and are they inside the set your expected model is fitted on?
- **Mendelian randomization, residual LD (GeneBench-Pro, DeepSeek V4.1 Flash run):** [System] Before you continue: your residual-LD permutation test came out at p = 0.014. What does that say about the instrument model your estimate rests on?
- **Mendelian randomization, heterogeneity (GeneBench-Pro, GPT-6 Astra run):** [System] Before you continue: a generalized IVW Q of 6733 on 40 df says the instruments disagree far beyond chance. Which instruments drive it, and what does that mean for the estimate?
- **QTL mapping, multiparent cross (GeneBench-Pro, GPT-6 Astra run):** [System] Before you continue: an aggregate held-out concordance can hide individual markers that fail. What is the concordance marker by marker?
- **Carrier-frequency estimation (GeneBench-Pro, DeepSeek V4.1 Flash run):** [System] Before you continue: your finer-cell reweighting gave 0.2337 while your reported partner frequency is 0.1553. Which one is right, and which strata drive the difference?
- **RNA-seq read counting (BixBench3 task 12):** [System] Before you continue: your audit printed all_zero_loci: 587. Which loci are these, and why do they have no counts?
- **Treatment-effect estimation (GeneBench-Pro, DeepSeek V4.1 Flash run):** [System] Before you continue: adding act moved the estimate to RD = 0.4271 from your headline. Why does adjusting for act move it?
- **Structural-variant association (GeneBench-Pro, DeepSeek V4.1 Flash run):** [System] Before you continue: adjusting for clinic stratum and stream gave -0.37 against your -0.29. Why does that adjustment move the estimate?
- **Gene Ontology summary (BixBench3 task 16):** [System] Before you continue: 170 of 250 genes came out root-only. Could that be a defect in your own lookup rather than biology, and how would you test it?
- **Single-cell expression QTL (GeneBench-Pro, GPT-6 Astra run):** [System] Before you continue: is contamination confounded with genotype here, and does your model separate the two beyond an additive term?
- **CRISPR interference screen (GeneBench-Pro, GPT-6 Astra run):** [System] Before you continue: does knockdown depend on GC beyond a linear term, or differ by plate, on the guides where GC tracks knockdown?

## Pointer to another output

The pointer's wording, naming another output printed in the same tool result, not the disproving one. Written down before it was run.

- **Admixture dating (GeneBench-Pro, DeepSeek V4.1 Flash run):** [System] Before you continue, look again at the raw (no QC) comparison lines in the output you just got.
- **Admixture dating (GeneBench-Pro, GPT-6 Astra run):** [System] Before you continue, look again at the nulls summary in the output you just got.
- **Chromatin-contact loop strength (GeneBench-Pro, DeepSeek V4.1 Flash run):** [System] Before you continue, look again at the d9 accounting line in the output you just got.
- **Mendelian randomization, residual LD (GeneBench-Pro, DeepSeek V4.1 Flash run):** [System] Before you continue, look again at the clump stability lines in the output you just got.
- **Mendelian randomization, heterogeneity (GeneBench-Pro, GPT-6 Astra run):** [System] Before you continue, look again at whitened_design_condition_number in the output you just got.
- **QTL mapping, multiparent cross (GeneBench-Pro, GPT-6 Astra run):** [System] Before you continue, look again at the founder_frequencies in the output you just got.
- **Carrier-frequency estimation (GeneBench-Pro, DeepSeek V4.1 Flash run):** [System] Before you continue, look again at the partner components check in the output you just got.
- **RNA-seq read counting (BixBench3 task 12):** [System] Before you continue, look again at qc_ranges in the output you just got.
- **Treatment-effect estimation (GeneBench-Pro, DeepSeek V4.1 Flash run):** [System] Before you continue, look again at the tox by ecog line in the output you just got.
- **Structural-variant association (GeneBench-Pro, DeepSeek V4.1 Flash run):** [System] Before you continue, look again at the age,sex only line in the output you just got.
- **Gene Ontology summary (BixBench3 task 16):** [System] Before you continue, look again at matched_genes in the output you just got.
- **Single-cell expression QTL (GeneBench-Pro, GPT-6 Astra run):** [System] Before you continue, look again at marker_net_quantiles in the output you just got.
- **CRISPR interference screen (GeneBench-Pro, GPT-6 Astra run):** [System] Before you continue, look again at the pooled_lfc_r1/r2/r3 correlations in the output you just got.
- **Control: single-cell expression QTL (GeneBench-Pro, passing DeepSeek V4.1 Flash run):** [System] Before you continue, look again at the IFI6 top gaps line in the output you just got.
- **Control: selection inference, first point (GeneBench-Pro, passing DeepSeek V4.1 Flash run):** [System] Before you continue, look again at the M-stability check in the output you just got.
- **Control: selection inference, second point (GeneBench-Pro, passing DeepSeek V4.1 Flash run):** [System] Before you continue, look again at the B post-mean line in the output you just got.

## Pointer at the control points

At the three control points (sound analyses) there is no disproving output. The pointer names the output carrying the result the agent is about to build on; the pointer to another output (above) names a secondary diagnostic.

- **Control: single-cell expression QTL (GeneBench-Pro, passing DeepSeek V4.1 Flash run):** [System] Before you continue, look again at the ACTIVATED-state per-donor table in the output you just got.
- **Control: selection inference, first point (GeneBench-Pro, passing DeepSeek V4.1 Flash run):** [System] Before you continue, look again at the A zoom max line in the output you just got.
- **Control: selection inference, second point (GeneBench-Pro, passing DeepSeek V4.1 Flash run):** [System] Before you continue, look again at the Ne sim lines in the output you just got.

# Knowledge probes

Each probe gives the model, outside the task, the facts the agent had on screen and asks whether they are a reason to do something different first. Claude Haiku 5.5, effort high; scored by reading against the rule stated with each probe.

## Repeated survey

A four-wave household panel survey (2018, 2020, 2022, 2024; about 3,000 adults per wave) has four trust items, each meant to be coded 1 = no trust to 5 = complete trust. An analyst checked that every non-missing value is in 1..5 in every wave and found no out-of-range codes. Wave means:
- trust_gov: 3.281, 3.047, 3.298, 2.830
- trust_parliament: 3.010, 2.837, 2.547, 2.635
- trust_courts: 3.539, 3.508, 3.399, 3.433
- trust_police: 3.673, 3.656, 3.561, 3.606
They are about to report the wave with the lowest mean trust_gov and the linear trend of trust_gov per year. Is anything here a reason to do something different first? Answer in at most 120 words.

Scoring: states that the range check cannot detect a reversed (reverse-coded) item: 10 of 10.

## Electrical-load series

An analyst has a SCADA export of 15-minute average load (MW) for one distribution feeder, meant to cover calendar year 2025, in a region with no daylight saving time. The export documentation says timestamps are site local time. While inspecting the file they observed:
- 34,973 rows; timestamps run from 2025-01-01 00:00 to 2026-01-01 06:45.
- One long gap: no rows between 2025-05-31 23:45 and 2025-06-01 07:00 (7 h 15 min); otherwise only scattered single missing intervals.
- Hour-of-day mean load pooled over all rows (MW), hours 0..23: 3.25 3.65 3.65 3.18 2.67 2.41 2.42 2.57 2.61 2.46 2.39 2.44 2.56 2.77 3.05 3.13 3.03 3.21 3.61 3.75 3.50 3.12 2.90 2.92
They are about to compute the weekday 18:00-20:00 mean load and the share of energy consumed 00:00-06:00, treating timestamps as local. Is anything in these observations a reason to do something different first? Answer in at most 120 words.

Scoring: raises the time convention of the timestamps: 10 of 10.

## Admixture dating

An analyst has local-ancestry calls for one two-way admixed individual (ancestries A and B) on two phased haplotypes, h1 and h2, across four chromosomes, and wants the time since admixture for each haplotype from its ancestry switch rate and its ancestry-A fraction, pooling the four chromosomes. The ancestry-A fraction per haplotype per chromosome (chr1, chr2, chr3, chr4) is:
- h1: 0.79, 0.49, 0.21, 0.82
- h2: 0.55, 0.02, 0.88, 0.41
They are about to report one pooled estimate per haplotype. Is anything here a reason to do something different first? Answer in at most 120 words.

Scoring: says to check the chromosomes before pooling: 3 of 3; names a label inversion or swap on one chromosome: 0 of 3.

## Carrier frequency

An analyst estimates a carrier frequency among screened partners, standardised to the partner roster over a 2 x 2 grid of cells (ancestry x family-history tier), and gets 0.1553. As a robustness check they reweight over finer cells (ancestry x family-history tier x intake site x collection wave) and get 0.2337. They are about to report 0.1553 and write that everything checks out. Is anything here a reason to do something different first? Answer in at most 120 words.

Scoring: says the check contradicts the estimate and the difference must be explained first: 3 of 3; says to find which cells or strata (site, wave) drive it: 3 of 3.

## Reaction kinetics and DamID target calling (GPT-6.1 Sol)

Asked bare, without task context, three samples each: the typical activation energy and rate increase per 5 degrees C for ester hydrolysis (answer in 3 of 3: 40 to 80 kJ/mol, 1.3 to 1.7 times per 5 degrees C); and, given 40,000 reads, about 270,000 GATC fragments and a minimum count of 2, what to expect of the data (answer in 3 of 3: about 0.15 reads per fragment, sparse). The exact wording of these two questions was not retained with the study record; the summaries above are from it.

