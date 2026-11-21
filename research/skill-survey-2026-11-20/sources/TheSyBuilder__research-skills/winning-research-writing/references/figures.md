# Scientific figures

## Choose the figure by the reader's question

| Reader's question | First design to consider | Information that earns the space |
| --- | --- | --- |
| Why is the existing approach insufficient? | A concrete failure case next to its comparison or a diagnostic plot | Matched conditions, visible difference, and its relevance |
| What does the method do differently? | A before-and-after mechanism diagram with the same input | Different operation, stage boundaries, and the corresponding symbols or steps |
| How does a claim trade off against resources? | Curves or points on matched axes, with a Pareto frontier if appropriate | Real budgets, axis units, comparison protocol, and supported operating points |
| Which conditions flip the result? | Small multiples, interval estimates, paired points, or a heatmap | The unit of analysis, uncertainty, and a readable scale shared where comparisons require it |
| Where does the theorem apply? | An assumption or parameter regime diagram, worked example, or small counterexample | Exact boundary, labeled assumptions, and distinct implications on each side |
| How was the resource constructed? | Dataset lineage or study-flow diagram paired with real records | Counts at key transitions, filters, labeling steps, and exclusion reasons |
| What are the main outcomes or exact comparisons? | A compact table with grouped columns | Units, direction, denominator, variability, and comparable settings |
| What evidence supports an interpretation? | A joint display or curated case panel | Sampling context, appropriate attribution, and disagreements alongside typical cases |

## Plan, draw, and verify

- Design the first figure around the most important orientation problem. A short conceptual contrast can work when the reader must first understand the mechanism. Lead with a finding when the phenomenon is the contribution and the panel can be interpreted with a compact caption. A precise theorem or table can take this role in a figure-free paper.
- Size each panel at final column width. Make labels and directional encodings legible in grayscale as well as color. Use direct labels where they reduce legend lookups. Share axes when readers should compare magnitudes and state transformations. Use units and cell sizes or sample counts whenever they determine interpretation. Explain uncertainty intervals and their computation in the caption or a clear methods reference.
- Put the takeaway and experimental or formal conditions in the caption. Define abbreviations and marks, name the reference or baseline, state the uncertainty and independent sample unit when applicable, and explain which panel supports which part of the claim. Number the panels in reading order. Keep comparison budgets and figure values consistent with the manuscript.
- Draft schematic boxes and arrows as editable vector or native diagram objects. For real measurements, generate plots from verified data with a standard plotting library and preserve source for reruns. Use mock layouts only when clearly labeled as plans. A reproduction or adaptation of an existing figure needs appropriate credit and any required permission. Check the actual rendered figure and its caption together.

For production examples and layout guidance, see [MIT Communication Lab figure design](https://mitcommlab.mit.edu/be/commkit/figure-design/) and [Rougier et al. on scientific figures](https://doi.org/10.1371/journal.pcbi.1013505). Use [Conference evidence](conference-evidence.md) to inspect figures from papers with comparable contribution types.
