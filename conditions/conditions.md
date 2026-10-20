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
