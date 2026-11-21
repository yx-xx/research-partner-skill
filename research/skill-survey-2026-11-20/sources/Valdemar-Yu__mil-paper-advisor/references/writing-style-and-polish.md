# MIL Writing Style, Linguistic Fingerprint & Polishing Guide

Distilled from **Prophet (CVPR 2023)** and **TwigVLM (ICCV 2025)**, integrated with the lab's **Anti-Defensive Writing (Press-Release)** principle.

---

## 1. Core MIL Prose Ethos

MIL papers read like **confident, disciplined, crystal-clear engineering science**:
- **Understated Confidence**: Describe our method as `conceptually simple`, `simple yet effective`, `simple and general`, `lightweight`, `easy to deploy`. Let the margins (`+13.1 points`, `96% accuracy at 88.9% pruning`, `154% speedup`) do the shouting.
- **High Information Density, Low Fluff**: Cut throat-clearing filler (`In recent years, with the rapid development of...`, `It is widely acknowledged that...`). Start sentences directly with concrete nouns and actions.
- **Logical Signposting**: Every paragraph has a visible logical role (`Despite ...`, `We ask: ...`, `To this end, ...`, `Interestingly, ...`, `To better understand ..., ...`, `To summarize, ...`). A tired reviewer skimming only topic sentences and bold lead-ins still grasps 100% of the paper.
- **Mechanistic Explanations Everywhere**: Never stop at "A beats B by 2.4%." Always follow with a causal `This is because ...`, `We hypothesize/conjecture that ...`, or `which can be explained by two facts: (i) ..., and (ii) ...`.

---

## 2. MIL Phrasebank & Rhetorical Skeletons

Use these as **structural templates** (adapt wording naturally to the paper's domain; never copy full sentences verbatim):

### A. Opening & Tension Pivot
- `[Domain] has been of growing interest / has demonstrated remarkable capabilities in ..., yet [core bottleneck] poses great challenges for ...`
- `Despite the success/promising results achieved by these methods, they still suffer from [the following] two major shortcomings: (i) ...; and (ii) ...`
- `In this situation, the task of ... is introduced to ... We focus on ... in this paper.`

### B. The Signature MIL Pivot (`We ask:`)
- `We ask: *Is it possible to [core unification/insight]?*`
- `We ask: *Whether [phenomenon A] provides more informative signals to facilitate [goal B]?*`
- `We ask: *Can these methods also facilitate [overlooked regime], especially when [practical condition]?*`

### C. Introducing & Elevating the Method
- `In this paper / To this end, we present **[Name]**—a conceptually simple [and general] framework designed to ...`
- `Specifically, we introduce [Component A] and [Component B] to overcome the limitations in (i) and (ii), respectively.`
- `Compared with most existing [baseline family], our [Name] not only achieves **better [Metric 1]** by employing [Strategy 1], but also yields **higher [Metric 2]** by utilizing [Strategy 2].`
- `Interestingly, [two seemingly separate benefits] can be simultaneously obtained from [one simple source].`
- `To summarize, [Name] is easy to deploy and enables holistic [goal] with [key guarantee].`

### D. Claiming Results & Practicality Edge
- `Without bells and whistles, [Name] surpasses/preserves ...`
- `It outperforms all the compared methods by a distinct margin.`
- `We can see that [Name] consistently and significantly outperforms all its counterparts under different [regimes].`
- `Notably, [Name] achieves near-perfect performance preservation (more than 99.0%) when ...`
- `Moreover, [Name] is friendly to most researchers, as our results can be reproduced using [modest hardware].`
- `Compared to [complex baseline], our [Name] is much simpler and more effective.`
- `It is worth noting that [Mechanism B] produces exactly the same response as [Target], which means the accuracy is only affected by [Mechanism A].`

### E. Analytical & Ablation Transitions
- `To better understand this improvement, we conduct a statistical/visual analysis of ...`
- `From the results in Table X / Figure Y, we can see that: (i) ...; (ii) ...; and (iii) ...`
- `The results lead to the following observations: First, ... Second, ... Third, ... Finally, ...`
- `We conjecture / hypothesize that this is because ... This observation also verifies our hypothesis above.`
- `These observations can be explained by two factors: (i) ... obtains diminishing returns, which finally saturates at ...; and (ii) ... involves linearly increasing computation ...`
- `As a by-product, we verify that ...`
- `In a word, [Name] acts like a real [metaphor] that adaptively ...`

### F. Related Work & Conclusion Sign-Off
- `Following this paradigm, subsequent studies have introduced ... Meanwhile, there is another line of studies that ... However, ...`
- `Extensive ablations, comparative experiments, and comprehensive analyses on [datasets] show the superiority of [Name] over all existing state-of-the-art methods.`
- `We hope [that] our work [will/may] serve as a solid baseline to inspire future research on [domain] [and beyond].`

---

## 3. Anti-Defensive Writing & De-Slopping Diagnostics

When polishing student drafts, hunt down and eliminate these **6 recurring failure patterns**:

| Anti-Pattern | Typical Student / AI-Slop Draft | MIL-Style Rewrite | Why It Wins |
| :--- | :--- | :--- | :--- |
| **1. Defensive Apology** | "Unfortunately, our method slightly underperforms Baseline X on Dataset C by 0.4% and still incurs minor extra latency." | "Across six benchmarks, our method achieves the highest overall RelAcc (96.0% vs. 95.2%), while preserving near-lossless accuracy at high pruning ratios and delivering 154% speedup on long-response generation." | Leads with the verified dominant axis; never hands reviewers a knife over a 0.4% single-cell fluctuation. |
| **2. Work-Log Narration** | "We first tried using raw logits, which did not work well, so we then experimented with cosine similarity on fused features and found it improved accuracy." | "Since the fused features are linearly projected for answer prediction, we conjecture they lie in a latent answer space... As verified in Table 1d, our fused-feature strategy outperforms answer-logit selection (60.84% vs. 60.40%), as logits lose input visual-textual context." | Presents the final logical insight first, then treats the failed alternative as a clean ablation control. |
| **3. AI-Slop Hype** | "We delve into this intricate challenge and propose a revolutionary, meticulously designed framework that leverages the immense power of VLMs." | "To address the limitations above, we present TwigVLM—a simple and general architecture by appending a lightweight twig block upon an early layer of the base VLM." | Concrete physical action replaces empty buzzwords; builds immediate reviewer trust. |
| **4. Contribution Bullet Dump** | "Our main contributions can be summarized as follows: (1) We identify two problems... (2) We propose X... (3) Extensive experiments show..." | *(Delete bullets)* End Intro with the `We ask:` -> 1-to-1 mechanism paragraph -> `Without bells and whistles, ...` results & broader significance paragraph. | Eliminates repetition of Abstract/Intro, saves 12–18 lines on Page 2, sharpens rhetorical finish. |
| **5. Number-Reciting Ablation** | "When T=1, accuracy is 93.9 and speed is 154.1. When T=2, accuracy is 95.2 and speed is 152.6. When T=3, accuracy is 96.0 and speed is 153.6. When T=4, accuracy drops to 95.8." | "A single twig layer (T=1) yields the highest speed but lowest accuracy. Increasing T to 3 raises accuracy to 96.0% with negligible speed loss, whereas T=4 degrades both metrics due to diminishing token-selection returns and linearly growing twig overhead while SSD acceptance saturates." | Compresses raw numbers into trajectory + mechanism + default-choice justification. |
| **6. Hostile / Weak Related Work** | "Method A is bad because it ignores decoding. Method B is worse because it needs a small VLM." | "Although the above methods effectively accelerate the prefilling stage, their speedup in the decoding stage remains limited. ... However, both methods require a pre-existing high-capable small model with the same vocabulary, which severely restricts the choice of VLMs." | Respectful, surgical, structural critique — makes our contribution look necessary rather than adversarial. |

### Banned Words / Expressions Check
Flag and replace during polishing:
- **AI-slop hype**: `delve`, `tapestry`, `unprecedented`, `revolutionary`, `game-changing`, `paradigm shift`, `meticulously`, `seamlessly harness`, `leverage the immense power of`, `intricate interplay`, `pivotal role`, `holistic landscape`.
- **Self-weakening hedges** (unless strictly required for factual scope): `unfortunately`, `regrettably`, `merely`, `only achieves a modest`, `falls short`, `suffers from severe limitations` (about *our* method), `remains far behind`.

---

## 4. LaTeX & Typographic Micro-Conventions (MIL House Style)

Enforce these crisp details when outputting or polishing LaTeX:
1. **Cross-references**:
   - Sections: `§\ref{sec:...}` (renders as `§3.2`, `§2.3`, `§4.2`).
   - Equations: `Eq.(\ref{eq:...})` (renders as `Eq.(3)`).
   - Figures & Tables: always capitalized `Figure~\ref{fig:...}`, `Table~\ref{tab:...}`, `Table~\ref{tab:ablation}a`.
2. **Inline Paragraph Sub-headers**:
   - Use `\paragraph{Title.}` or `\noindent\textbf{Title.}` (followed immediately by prose on the same line) for Related Work topics, Method components (`\textbf{Answer candidates.}`), and every Ablation subtable discussion (`\textbf{Pruning position.}`). Avoid wasting vertical space on `\subsubsection`.
3. **Tight Parameter Formatting in Prose**:
   - `K=10`, `N=16`, `T=5`, `D=18`, `S=32`, `\bar{R}=64`, `K_f=24` (compact spacing inside prose for clean line breaks).
4. **Emphasis Discipline**:
   - **Bold**: Method name at first appearance in Intro, key dual-advantage phrases in Abstract (`\textbf{better accuracy retention}`, `\textbf{higher generation speed}`), inline paragraph headers, and best numbers in tables.
   - *Italic*: The `We ask: *...*` question, newly coined terms at definition (`*answer candidates*`, `*latent answer space*`, `*prefilling*` and `*decoding*`, `*FinalWipe*`), and subtle contrast emphasis (`by adding *one* line of code`, `*single* token`, `*fine-grained* semantics`).
5. **Strategic Footnotes** (high-value micro-details that would clutter prose):
   - Notation simplification: `For notational simplicity, we omit the visual encoder and prediction head...`
   - Devastating compute contrast: `Flamingo-80B is trained on 1,536 TPUv4 for 15 days which is unaffordable for most researchers, but Prophet uses one RTX-3090...`
   - Edge-case metric definition: rounding rules, rare probability edge cases, metric intuition (`The token acceptance rate measures...`).
6. **Prompt / Code Templates in Method** (Prophet-style):
   - Put exact prompt templates inside a crisp single-rule `\fbox` / `tcolorbox` with substituted variables highlighted in blue (`\textcolor{blue}{c}`) and explicit `\n` line breaks so the reader sees exact implementation transparency.
