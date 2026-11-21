# Editing without meaning loss

Treat “AI slop” as shorthand for defects in the manuscript, especially generic claims, unsupported confidence, fake specificity, prose that repeats the outline, and visuals or citations that fail to advance the argument. Diagnose the defect by reading the text and tracing it to evidence. Detector scores, prose statistics, and isolated vocabulary cannot verify authorship. Keep technical terms, precise repetition, or ordinary academic phrasing when they help readers understand the work.

| Symptom | Editorial repair |
| --- | --- |
| Hype or empty framing | Identify the actual object, observed failure, gap, and affected setting |
| Results sound universal | Restore the population, experimental conditions, comparator, and meaningful exceptions |
| Many paragraphs restate the same result | Give each occurrence a distinct function, such as headline, numerical evidence, interpretation, or limitation |
| Related work reads like a citations list | Organize by the distinction that matters to the argument and explain how the closest works differ |
| Precise-sounding but unsupported claims | Check the underlying record. Remove unsupported specifics or mark a concrete author query |
| Placeholder figure or superficial cross-reference | Show a real input/output, mechanism, or measured comparison and explain why it bears on the claim |
| Overly uniform or ornate language | Use concrete subjects and verbs, intentional sentence length, and transitions that express the actual dependency |

## Preserve scientific meaning through an edit

1. Capture the claims in the source passage and their evidence, including citation, dataset or population, sampling unit, model or setting, comparator, direction and magnitude, units, uncertainty, relevant exceptions, and inference type. Include definitions and assumptions that later text depends on. For long work, preserve a compact record by section and compare it across sections before delivering.
2. Revise for the precise meaning and purpose of the passage. Replace vague abstractions with the actual scientific entities. Move material only where readers can still recover its relationship to the claim. For author-voice edits, infer register and terminology from their own writing and retain it where clear.
3. Compare each material claim and condition against the before version and primary artifacts. Check abstract, results, figure captions, and conclusion for consistent effect direction, sample counts, split, model version, units, uncertainty, and limitations. Verify that citations resolve and support the exact attributed claim. Preserve both null results and unfavorable cases. Restore any lost dependency or qualifier.
4. Return clean prose in the requested format. If evidence conflicts, surface the precise discrepancy and do what is supported. Check the target's current acknowledgment or disclosure rules for AI assistance and format the disclosure when relevant.

Illustrative revision with synthetic evidence. “Our framework robustly improves learning in low-data settings” becomes “Across five seeds on the two 1%-label splits, the method improved macro-F1 by 2.1 points over the supervised baseline (95% CI 0.6–3.5). The 10%-label split showed no clear improvement.” Use that level of specificity only when the data support each detail. A statement of no clear improvement is distinct from a finding of equivalence.

## Evidence behind the edit

- A large PubMed study measured vocabulary shifts across a corpus. Its method does not identify particular manuscripts as AI-edited. English-language detector bias has also been measured. [Kobak et al.](https://pmc.ncbi.nlm.nih.gov/articles/PMC12219543/) · [Liang et al.](https://doi.org/10.1016/j.patter.2023.100779)
- LLM-generated summaries have been observed broadening scientific claims. Generated citations can be fabricated and real citations can contain wrong details. Check both claim scope and underlying sources. [Peters and Chin-Yee](https://doi.org/10.1098/rsos.241776) · [Walters and Wilder](https://www.nature.com/articles/s41598-023-41032-5)
- An observational preprint on scientific slop studies grounding, repetition, figure function, and other defects alongside ICLR reviewer ratings. It motivates concrete diagnostics. The design does not establish what causes acceptance. [Oh et al., Table 1 and Appendix D](https://arxiv.org/html/2610.00531v1)
