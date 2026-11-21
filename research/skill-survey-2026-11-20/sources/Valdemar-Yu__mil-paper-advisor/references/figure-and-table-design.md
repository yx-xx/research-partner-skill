# MIL Figure & Table Visual Design System

Distilled from **Prophet (CVPR 2023)** and **TwigVLM (ICCV 2025)**.

MIL visuals are immediately recognizable for their **high semantic density, restrained Morandi pastel fills, concrete embedded examples, zero visual clutter, and paper-wide color lock**.

---

## 1. The Single-Accent Paper-Wide Color Lock Rule

Before drawing Figure 1, choose **ONE** palette below and enforce it across **every figure, chart, AND ablation table** in the entire paper. Never let Figure 1 be green, Figure 4 be orange, and Figure 6 be neon blue!

### Palette A: Botanical Blue-Green (`TwigVLM`, ICCV'25 — Recommended Modern Default)
Ideal for architecture, acceleration, efficiency, multimodal, and modular plug-in papers.

| Semantic Role | Fill HEX | Stroke / Accent HEX | LaTeX / Usage |
| :--- | :--- | :--- | :--- |
| **Frozen / Base Model (Trunk)** | `#DAEAF6` (pale sky blue) | `#5B8DBE` (steel blue) | Base LLM/VLM layers + `[snowflake icon]` |
| **Learnable / Proposed Method (Ours)** | `#E2F0D9` (pale sage green) | `#70AD47` / `#54A85B` (fresh green) | Proposed module + `[flame icon]`; **Ours** bars (`#77C374`); Table default row highlight! |
| **Baseline 1 (Primary Rival)** | `#4C82B6` / `#1E728E` | `#2E5D8A` | Deep teal / steel blue bars & curves |
| **Baseline 2 (Secondary Rival)** | `#9A8AC4` / `#8866AD` | `#6B5496` | Muted lavender-purple bars |
| **Visual Tokens / Input Patches** | `#E7A698` (soft coral) | `#C97B6C` | Retained visual token chips; faded + dashed for pruned |
| **Stage / Card Containers** | `#F4F6F8` / `#F3F9EE` | `#CCCCCC` (1pt dashed/solid) | Subtle grouping background |
| **Status / Highlight Delta** | `#4CAF50` (check) / `#C62828` (red) | — | Green checkmark, red cross, crimson red `RelSpd` % text above bars |
| **Advantage Callout Border (Optional)** | `#FFFFFF` | `#B85A8A` (muted rose) / `#6AA84F` (green) | Dashed callout boxes in Fig. 1(b) |

### Palette B: Slate-Amber Academic (`Prophet`, CVPR'23 — Ideal for Prompting / Agent / Retrieval Pipelines)
Ideal for multi-stage reasoning, LLM prompting, retrieval-augmented, or pipeline-comparison papers.

| Semantic Role | Fill HEX | Stroke / Accent HEX | Usage |
| :--- | :--- | :--- | :--- |
| **Frozen Foundation Model (LLM)** | `#3B5978` / `#46698C` | `#2C435A` | Dark slate blue block + white text + white `[snowflake icon]` |
| **Task / Trainable Model (Ours)** | `#E5A967` / `#EE854A` | `#C7853C` | Warm amber/ochre block & **Ours** bars |
| **Competing Complex Module** | `#C46D3B` | `#9E5329` | Burnt terracotta for heavier rival blocks |
| **Auxiliary / Off-the-Shelf Tool** | `#4A80B5` / `#779ECB` | `#3B6998` | Steel / periwinkle blue (KB, captioner, encoder) |
| **Prompt Head / Novel Heuristic Highlight** | `#FFF3CD` (soft butter yellow) | `#D6B656` | Prompt instructions & heuristic callout strip |
| **In-Context Examples** | `#E2F0D9` (soft mint green) | `#82B366` | Few-shot example cards |
| **Testing Input** | `#EAE6F5` (soft lavender) | `#9673A6` | Query / test input card |
| **Ablation Table Default Row** | `#EAEAEA` (`gray!15`) | — | Clean neutral gray highlight |

---

## 2. Universal MIL Visual Grammar

1. **Flat Vector Cleanliness**: Crisp rounded rectangles (`corner radius 4–6pt`), consistent stroke weight (`1.0–1.5pt`), pure white canvas (`#FFFFFF`). **ZERO** 3D extrusions, glossy gradients, heavy drop shadows, neon colors, or decorative clipart.
2. **Standard Iconography**:
   - Frozen weights: clean crisp **snowflake icon** inside or at corner of block.
   - Trainable weights: clean crisp **flame icon** at corner of block.
   - Correct / Accepted / Verified: clean **green circle checkmark**.
   - Wrong / Pruned / Rejected: clean **red circle cross** or faded translucent chip with dashed border.
   - Weight copy / initialization / attention guidance: **dashed arrow** (`-- ->`).
   - Primary data / forward flow: **solid thin arrow** (`--->`, clean triangular arrowhead).
3. **Typography**: Sans-serif (`Helvetica` or `Arial`), consistent font hierarchy across all figures (`8–10pt` equivalent at final column width — never microscopic text!). Mathematical symbols italicized to match LaTeX (`K`, `T`, `L`, `R`, `D`, `S`).
4. **Concrete Sample Grounding (Mandatory for Teaser & Framework Figures)**:
   - Always route **one real, memorable image + question/prompt + concrete tokens/candidates/scores** through the diagram (`what fills the balloons? -> air(0.28), helium(0.07) -> helium`; `what is unusual about this image? -> man is holding [X] -> ironing [check]`).
   - Keep the **same sample** consistent across sub-panels `(a)`, `(b)`, `(c)` when showing a lifecycle!
5. **Chart Anti-Chartjunk Rules (Matplotlib / Plots)**:
   - Remove top and right axes spines (`ax.spines['top'].set_visible(False)`).
   - Pure white background, NO heavy gray plot fill, NO dense gridlines (at most subtle horizontal baseline dotted reference line for Base Model / Prefilling).
   - Direct data labels on bars or pie slices rather than forcing readers to trace values across to the y-axis!
   - Share legends cleanly at bottom/top outside bars so legends never collide with data.

---

## 3. Archetype Blueprints for Every MIL Figure

### Figure 1: Page-1 Top-Right Teaser (Strictly 1-Column Width!)
Placed at top-right of Page 1 beside Abstract/Intro. Choose one of two MIL archetypes:

- **Archetype 1A — Stacked Conceptual Comparison (`Prophet` Fig. 1)**:
  - *Left strip (~30% width)*: Shared multimodal inputs stacked vertically with symbol labels `(Q)`, `(K)`, `(V)` (real photo thumbnail), `(C)` (off-the-shelf model -> text).
  - *Right stack (~70% width)*: 3 horizontal pipeline rows separated by subtle horizontal whitespace:
    - Row 1: `Baseline A` (simple naive pipeline)
    - Row 2: `Baseline B / C` (complex rival pipeline with extra heavy paths)
    - Row 3: **`MethodName (ours)`** (bold header, clean unified flow, key innovation highlighted in soft yellow/green).
  - *Caption formula*: `Figure 1. Conceptual comparisons of [N] [task] frameworks... While [Baselines] ..., we argue that ... In contrast, our [Name] ...`

- **Archetype 1B — Architecture + Dual-Advantage Quantitative Proof (`TwigVLM` Fig. 1)**:
  - *Left half `(a) [Name] architecture` (~42% width)*: Compact vertical block stack showing frozen base model (pale blue + snowflake) with our learnable lightweight module (pale green + flame) branching/attaching cleanly.
  - *Right half `(b) Two key advantages of [Name]` (~58% width)*: Two stacked dashed-border cards corresponding 1-to-1 to Intro `(i)` and `(ii)`! Each card pairs a **tiny schematic visual on the left** (e.g., attention overlay or speculative tokens) with a **ultra-compact 2-bar chart on the far right** (`Baseline` vs. `ours`, red dotted base-model line, bold exact numbers!).
  - *Caption formula*: `Figure 1. Our [Name] overview. (a) ... (b) Compared to ..., [Name] not only achieves [Adv 1] but also yields [Adv 2]. [Exact control setting note].`

### Main Framework Figure (Page 3 or 4 — Full 2-Column Width!)
- **Archetype 2A — Left-to-Right Two-Stage Concrete Walkthrough (`Prophet` Fig. 2)**:
  - Two subtle light-gray rounded stage panels with **explicit section pointers in bottom labels**: `Stage-1 Name (§3.2)` | `Stage-2 Name (§3.3)`.
  - Shows training + test concrete samples -> encoder -> geometric/latent space diagram -> exact formatted prompt boxes (color-coded by role) -> frozen/target model -> final concrete answer.
- **Archetype 2B — Three-Panel Lifecycle (`TwigVLM` Fig. 4)**:
  - Three equal-height panels side-by-side: `(a) Training stage` | `(b) Inference stage (Stage 1 / Prefilling)` | `(c) Inference stage (Stage 2 / Decoding)`.
  - Visual tokens shown as neat rows of small colored chips; weight init shown as dashed transfers; concrete real image & text tokens sit at bottom of each panel.
  - *Caption formula*: Bold summary title + `(a) ... (b) ... (c) ...` mirroring the three panels.

### Diagnostic & Result Figures
- **Pilot Study Hybrid (`TwigVLM` Fig. 2 — 1-column)**: Top 55% = 1 real image + 2 contrasting text prompts + 2×2 visual heatmap/token-selection overlays (`D=2` vs `D=18`); Bottom 45% = crisp single-curve line plot (`RelAcc` vs `D`, dashed upper bound).
- **Pilot Study Timing Pair (`TwigVLM` Fig. 3 — 1-column)**: Two side-by-side compact bar charts `(a)` sequential single-hue bar ramp with dotted `Prefilling` reference line, `(b)` 2-group paired comparison bar chart (`Prefilling(P)` vs `Decoding(D)`).
- **Behavioral Breakdown Pair (`Prophet` Fig. 3 — 1-column)**: `(a)` clean 3-slice pie chart with direct rounded-pill percentage labels on slices (zero legend box!) + `(b)` 3-category paired bar chart (`Base` vs `Ours`) proving huge jump on the hardest slice.
- **Qualitative Matrix (`TwigVLM` Fig. 5 — 1-column)**: Compact 2-row × 4-column image grid (`image, prompt | Rival 1 | Rival 2 | Ours`), each cell showing visual overlay + `A: pred [X / check]` directly below.
- **Multi-Panel Benchmark Bars (`TwigVLM` Fig. 6 — 1-column)**: Two side-by-side bar charts (`Short Regime` vs `Long Regime`), shared bottom legend, dashed base-model line, dual stacked bar labels (`black absolute value` over `crimson red relative %`).

---

## 4. LaTeX Table Blueprints (MIL / Kaiming-He Booktabs Style)

### Blueprint 1: 2x3 Six-Subtable Ablation Grid (`booktabs` + `subcaption` + `colortbl`)
- **Rules**: ZERO vertical lines (`|`). Only `\toprule`, `\midrule`, `\bottomrule`. Every subtable has a **bold title + 1-sentence conclusion caption**. Highlight the default setting row in every subtable using the paper's locked color (`\definecolor{mildefault}{HTML}{E2F0D9}` or `{gray}{.9}`).

```latex
\definecolor{mildefault}{HTML}{E2F0D9} % Match Palette A green (or gray!15 for Palette B)
\newcommand{\defaultrow}{\rowcolor{mildefault}}

\begin{table*}[t]
\centering
\scriptsize
\setlength{\tabcolsep}{4pt}
% Row 1
\begin{subtable}[t]{0.31\linewidth}
  \centering
  \begin{tabular}{lc}
    \toprule
    variant & RelAcc (\%) \\
    \midrule
    (a) baseline A & 82.3 \\
    (b) baseline B & 86.2 \\
    \defaultrow (c) ours (default) & \textbf{96.0} \\
    \bottomrule
  \end{tabular}
  \caption{\textbf{Core mechanism.} Bold takeaway sentence explaining why (c) wins.}
  \label{tab:abl_a}
\end{subtable}\hfill
\begin{subtable}[t]{0.31\linewidth}
  \centering
  % ... subtable (b) ...
  \caption{\textbf{Component synergy.} Bold takeaway sentence.}
  \label{tab:abl_b}
\end{subtable}\hfill
\begin{subtable}[t]{0.31\linewidth}
  \centering
  % ... subtable (c) ...
  \caption{\textbf{Initialization / Design.} Bold takeaway sentence.}
  \label{tab:abl_c}
\end{subtable}

\vspace{6pt}
% Row 2: subtables (d), (e), (f) identically structured
\caption{\textbf{Ablation experiments for [Name].} Taking [Base] as the reference model,
[Metric 1] is evaluated on [Datasets] and [Metric 2] is evaluated on [Dataset].
In each table, the best result is bolded and the result with the default setting
([params]) is marked in \colorbox{mildefault}{green}.}
\label{tab:ablation}
\end{table*}
```

### Blueprint 2: Grouped Main Results Table (`Upper Bound` + Shaded Regime Headers)
```latex
\definecolor{bandgray}{gray}{0.92}
\definecolor{downgreen}{HTML}{4E9A4E}

\begin{table}[t]
\centering
\scriptsize
\setlength{\tabcolsep}{3.5pt}
\begin{tabular}{l|cccccc|c}
\toprule
\textbf{Method} & \textbf{Bench1} & \textbf{Bench2} & \textbf{Bench3} & \textbf{Bench4} & \textbf{Bench5} & \textbf{Bench6} & \textbf{RelAcc} \\
\midrule
\rowcolor{bandgray}
\multicolumn{8}{c}{\textit{Upper Bound, 576 Tokens (100\%)}} \\
\textcolor{gray}{Base-Model-7B} & \textcolor{gray}{61.9} & \textcolor{gray}{64.7} & \textcolor{gray}{1862} & \textcolor{gray}{58.2} & \textcolor{gray}{69.5} & \textcolor{gray}{78.5} & \textcolor{gray}{100\%} \\
\midrule
\rowcolor{bandgray}
\multicolumn{8}{c}{\textit{Retain Averaged 64 Tokens (\textcolor{downgreen}{$\downarrow$ 88.9\%})}} \\
Baseline A [8]  & 44.1 & 45.9 & 1218 & 50.7 & 70.0 & 52.0 & 77.0\% \\
Baseline B [51] & 55.1 & 60.1 & 1690 & 55.5 & 69.0 & 72.4 & 93.3\% \\
\textbf{[Name] (ours)} & \textbf{58.8} & 60.4 & \textbf{1760} & 55.8 & \textbf{70.0} & \textbf{75.6} & \textbf{96.0\%} \\
\bottomrule
\end{tabular}
\caption{\textbf{Performance comparisons on [Base].} All methods share the same base model. The best result in each regime is bolded.}
\label{tab:main}
\end{table}
```
*(Note: For pure Kaiming-style minimal tables like Prophet Table 2, omit even the vertical column separator `|` around Method/RelAcc; use vertical separators sparingly only when separating Method / Metric columns from an overall summary column like `RelAcc`, matching TwigVLM Tables 1–3.)*
