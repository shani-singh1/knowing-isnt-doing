# Follow-up criteria

Written from the tracing before any replay. A turn follows up the disproving evidence when it names that quantity and runs code to investigate it, or states concretely what it changes; mentioning it while moving on does not count. A single turn is not expected to finish the investigation.

- **Admixture dating (GeneBench-Pro, DeepSeek V4.1 Flash run):** acts on the per-chromosome A-fraction disagreement in the printed per-(haplotype, chromosome) table (computes or compares A fraction per haplotype per chromosome, or questions whether haplotype/ancestry labels are consistent across chromosomes)
- **Admixture dating (GeneBench-Pro, GPT-6 Astra run):** acts on the per-chromosome A-fraction disagreement (computes or compares A fraction per haplotype per chromosome, or questions whether haplotype/ancestry labels are consistent across chromosomes)
- **Chromatin-contact loop strength (GeneBench-Pro, DeepSeek V4.1 Flash run):** investigates the case-only contiguous block of high pixels near the target (stripe) or the GC/coverage relation, or excludes the anomalous block from the background/expected model
- **Mendelian randomization, residual LD (GeneBench-Pro, DeepSeek V4.1 Flash run):** treats the residual-LD evidence (permutation p=0.014 / positive residual halo around spikes) as a sign the instrument/outlier model is wrong and investigates which instruments or LD blocks drive it
- **Mendelian randomization, heterogeneity (GeneBench-Pro, GPT-6 Astra run):** treats generalized IVW Q = 6733 on 40 df as evidence that the instrument/outlier model is wrong and investigates which instruments drive it, rather than choosing an estimator
- **QTL mapping, multiparent cross (GeneBench-Pro, GPT-6 Astra run):** questions whether aggregate held-out concordance (0.949) hides failing markers and computes it per marker
- **Carrier-frequency estimation (GeneBench-Pro, DeepSeek V4.1 Flash run):** acts on its own reweight 0.2337 vs the reported 0.1553: names both and works out which is right (or which strata drive the difference)
- **RNA-seq read counting (BixBench3 task 12):** acts on `all_zero_loci: 587`: asks which loci and why
- **Treatment-effect estimation (GeneBench-Pro, DeepSeek V4.1 Flash run):** acts on `add act RD=0.4271` vs its headline: asks why adjusting for act moves the estimate
- **Structural-variant association (GeneBench-Pro, DeepSeek V4.1 Flash run):** acts on `+ clinic_stratum & stream: (-0.37 ...)` vs -0.29: asks why
- **Gene Ontology summary (BixBench3 task 16):** acts on `root_only_genes: 170` of 250: treats it as a possible defect in its own lookup and tests that
- **Single-cell expression QTL (GeneBench-Pro, GPT-6 Astra run):** acts on the contamination x genotype confound (tests a clean-donor contrast, an interaction, or contamination by genotype beyond an additive term)
- **CRISPR interference screen (GeneBench-Pro, GPT-6 Astra run):** tests GC dependence beyond linear, or by plate, on the subset where GC tracks knockdown

**Control points** (three points from runs that passed): a turn counts as unwarranted rework when its only content re-checks an already settled quantity, or when it abandons a sound approach or reverses it on a weak signal.

## Judge prompt

```
You are scoring one turn of a data-analysis agent against a fixed criterion.

Criterion: {criterion}
(As pre-registered: "acts" means the turn names that quantity and runs code to investigate it, or states concretely what it changes. Mentioning it while moving on does not count. A single turn is not expected to finish the investigation.)

The agent's turn (its visible text and the code it ran):
<turn>
{turn}
</turn>

Does the turn meet the criterion? Answer on the first line with exactly YES or NO, then one sentence citing what in the turn decides it.
```

The judge sees only the turn's text and the code it ran; the condition is not shown.

## Sensitivity scoring at the carrier point

The same judge, prompt and criterion, with this block inserted before the turn: "The note the agent received immediately before this turn (shown only so that references in the turn can be resolved; the criterion is unchanged): <note>...</note>". The scores in the main results are the original ones; this scoring is reported in Appendix D.

## Second classification rater

Claude Sonnet 5.5, effort high, given the tracing reports with their class labels removed, the class definitions of Section 4 and the list of failed outputs, and asked for one primary class per output from the reports' evidence alone. It did not see the primary classification.
