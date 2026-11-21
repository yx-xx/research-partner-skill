# MIL Experimental Design & Ablation Strategy

Distilled from **Prophet (CVPR 2023)** and **TwigVLM (ICCV 2025)**.

Every experiment in an MIL paper exists to execute one explicit rhetorical duty: **(1) expose an overlooked bottleneck**, **(2) establish strict fairness**, **(3) prove broad SOTA superiority**, **(4) dissect every design choice mechanistically**, or **(5) reveal *how* and *where* the gain happens**. Never dump miscellaneous logs.

---

## 1. Pre-Method Pilot Study Blueprint (Linking Section 2 to Section 3 & 4)

Use 1–2 cheap, controlled pilot studies in Section 2 whenever your story rests on an empirical bottleneck that prior work overlooked or misattributed (see [argumentation-and-structure.md](./argumentation-and-structure.md) for the 4 Probe Archetypes and Mechanistic Abstraction Leap).

### Pilot Study Execution Checklist
1. **Strict 1-to-1 Alignment with Intro Gaps `(i)` and `(ii)`**:
   - `Study 1` isolates the root cause of Gap `(i)` (e.g., TwigVLM `§2.2`: early-layer attention at $D=2$ is prompt-insensitive, whereas late-layer attention at $D=18$ is sharp -> abstracted as *"closer to prediction head"*).
   - `Study 2` isolates the root cause of Gap `(ii)` (e.g., TwigVLM `§2.3`: decoding dominates latency for $S \ge 32$, and FastV barely speeds up decoding -> abstracted as *"KV-cache dilutes SA + FFN dominates decoding"*).
2. **Decoupled Oracle / Regime Control**:
   - Fix all confounding variables (`K=2`, `R=128`, same base model `LLaVA-1.5-7B`) and sweep ONE diagnostic axis (`D >= K` or `S in [2, 128]`).
   - Add an upfront scope clarification if the probe ignores compute cost (`Notably, directly applying the attention map of a late layer... will inevitably introduce redundant computation, this pilot study only aims to evaluate...`).
3. **Quantitative + Qualitative / Stage-Split Pairing**:
   - Never rely on a bare scalar table for a pilot study.
   - Pair a **trend plot** (accuracy curve vs. depth $D$; decoding time vs. response length $S$) with either **contrastive prompt heatmaps** (1 image + 2 contrasting prompts proving prompt-insensitivity at $D=2$ vs. sensitivity at $D=18$) OR a **stage breakdown bar** (`Prefilling(P)` vs. `Decoding(D)`).
4. **Plant a Testable Hypothesis Paid Off in Section 4**:
   - Every Pilot Study must end with a crisp causal hypothesis (`We hypothesize that...`) AND a downstream verification hook (e.g., Study 1's "closer to prediction head" hypothesis is directly tested at fixed depth `D=K+T` in `Table 4a`; Study 2's long-response gap is directly paid off in `Fig. 6` comparing `TextVQA` vs `MM-Vet`).

---

## 2. Fairness & Control Engineering (Preempting Reviewer Attacks)

MIL papers earn high reviewer trust by anticipating and neutralizing the top 4 fairness objections *before* reviewers can raise them:

1. **Explicit Budget / Equivalent-Cost Alignment Formula**:
   - Define an exact apples-to-apples control equation early in Preliminaries / Implementation Details.
   - *TwigVLM exemplar*: Defines average retained visual tokens $\bar{R} = [M \times K + R \times (L - K)] / L$ (`Eq.(4)`) and updates it for FinalWipe (`Eq.(6)`), then explicitly adjusts $R$ so all methods share the identical pruning ratio $1 - \bar{R}/M$.
2. **Same-Backbone Re-Implementation (`†`)**:
   - When the closest prior paradigm used an older or different stage-1 backbone, re-implement our method on **their exact backbone** in Ablation `(a)` to isolate the paradigm gain cleanly!
   - *Prophet exemplar*: Table 1a re-implements MAVEx's exact `ViLBERT` model (`stage-1 acc. 35.28 vs 35.20`) and proves Prophet's prompting paradigm beats MAVEx's retrieval paradigm by `+4.69` (`44.97 vs 40.28`).
3. **Transparent Base / Stage-1 Reference Reporting**:
   - Always report the unpruned base model (`Upper Bound, 100%` in muted gray, TwigVLM Tables 1–3) OR the standalone Stage-1 model (`stage-1 acc.` column in Prophet Table 1a/b + inline 3-column mini-table in §4.2 showing `31.5 -> 35.6 -> 53.0`).
   - Why? Reviewers immediately ask: *"Is the gain just from a stronger base model / engineering trick?"* Showing the exact marginal delta (`+7.80`, `+9.69`, `RelAcc 96.0%`) shuts that objection down completely.
4. **Data Contamination Hygiene & Practicality Disclosure**:
   - Explicitly state contamination prevention (e.g., Prophet §4.2 removing OK-VQA test images from VQAv2/VG pretraining).
   - Explicitly annotate subtle protocol differences in SOTA tables (`*` = v1.0 split, `†` = queries GPT-3 during training, `‡` = finetuned variant) rather than hiding them.
   - Report real **wall-clock efficiency & hardware reproducibility** (`single RTX 3090`, `10% training time`, real `tok/s` across both prefilling and decoding — never hide behind FLOPs alone!).

---

## 3. Main Results Matrix Design

Design the main comparison tables so they prove **strength + generality + practical edge**:

1. **Group Baselines by Paradigm or Operating Regime**:
   - *Paradigm grouping (`Prophet` Table 2)*:
     - `methods with external knowledge bases`
     - `methods with multimodal pretraining` (includes 80B giant Flamingo)
     - `methods with GPT-3 API` -> **`Prophet (ours)`** at bottom!
   - *Regime grouping (`TwigVLM` Tables 1 & 2)*:
     - `Upper Bound (100%)` in muted gray
     - `Retain Averaged 192 Tokens (↓ 66.7%)`
     - `Retain Averaged 128 Tokens (↓ 77.8%)`
     - `Retain Averaged 64 Tokens (↓ 88.9%)` — proving our advantage *widens* under extreme compression!
2. **Prove Breadth Across Axes (Pick 2–3 That Match Your Task)**:
   - **Multi-backbone / Multi-resolution**: Standard image (`LLaVA-1.5-7B`, 576 tokens) + High-res image (`LLaVA-NeXT-7B`, 2,880 tokens) + pointer to newer family (`Qwen2.5-VL`) in supplementary.
   - **Cross-modality / Cross-task transfer**: Video understanding (`Video-LLaVA-7B`, 4 VideoQA benchmarks) OR second benchmark with both Direct-Answer (DA) and Multiple-Choice (MC) + a lightweight task-adapted variant (`Prophet-MC`: `57.3 -> 73.6`!).
   - **Dual-metric regime separation**: When speed depends on workload, test BOTH regimes explicitly (TwigVLM Fig. 6: short responses `TextVQA \bar{S}=4` where we match/slightly beat baselines, AND long responses `MM-Vet \bar{S}=72` where our SSD shines `~154% vs ~104%`!).

---

## 4. The Signature MIL 2x3 Six-Subtable Ablation Grid (Hypothesis Closure + Sweeps)

Both Prophet (Table 1) and TwigVLM (Table 4) use an iconic **2-row × 3-column (6-subtable) ablation matrix** spanning full page width. Crucially, MIL ablations are **NOT 6 hyperparameter-tuning tables**: the **top row `(a)–(c)` (plus key strategy slots)** primarily performs **Hypothesis Closure** — directly proving the mechanistic conjectures made in Section 2/3 — while the remaining slots map out capacity saturation and component trade-offs:

| Slot | Layer & Diagnostic Duty | Prophet (Table 1) Exemplar | TwigVLM (Table 4) Exemplar |
| :--- | :--- | :--- | :--- |
| **(a)** | **Hypothesis / Paradigm Closure #1** (Controlled apples-to-apples test of the core scientific hypothesis) | Prompting vs. retrieval on identical `ViLBERT` (`44.97 vs 40.28`) — proves Stage-2 prompting paradigm beats retrieval | Attention source at *identical depth* `D=K+T`: backbone (`86.2%`) vs. twig (`96.0%`) — directly closes `§2.2`'s *"distance to prediction head"* hypothesis! |
| **(b)** | **Synergy / Scaling Closure #2** (Proves dual mechanisms complement each other OR scales cleanly across backbones) | VQA backbone capability across 4 visual features (`Bottom-Up -> CLIP-RN50x64`), revealing diminishing returns | Acceleration strategies: Pruning only (`104.3%`) vs. SSD only (`146.7%`) vs. TTP+SSD synergy (`153.6%`) — directly closes `§2.2 + §2.3` complementarity! |
| **(c)** | **Core Design / Init / Diagnostic Metric** | `#candidates K` (`0, 1, 5, 10`) paired with intermediate `hit rate` (`K=1` acc > hit rate proves LLM error correction!) | Twig block initialization (`random` vs. `layers[L-T:L]` vs. `layers[K:K+T]`) — closes `§3.1` init design on BOTH RelAcc & RelSpd |
| **(d)** | **Conjecture / Depth Verification** | Example selection strategy (`rand`, `ques+img`, `fused`, `fused+ques+img`, `answer logits`) + `hit rate` — directly closes `§3.2`'s *latent answer space* conjecture! | Number of twig layers `T in {1, 2, 3, 4}` revealing saturation + linear overhead trade-off |
| **(e)** | **Key Hyperparameter Trade-Off / Boundary Proof** | `#examples N x #queries T` (`T=1` vs `T=5`, including `N=0` collapse below Stage-1 proving few-shot activation!) | Pruning position `K in {0, 1, 2, 3}` under *fixed* `\bar{R}=64` showing optimal `(K, R)` balance |
| **(f)** | **Fine-Grained Component / Add-on Leave-One-Out** | Prompt contents (`default`, `w/o head`, `w/o scores`, `w/o captions`, `default+tags`) | `FinalWipe` strategy (`x` vs `✓` at `K_f in {20, 24, 28}`) showing accuracy-speed sweet spot |

### Strict MIL Ablation Rules
1. **Lock ONE Default Setting Across All 6 Subtables** (e.g., `K=10, N=16, T=5` or `T=3, K=2, K_f=24, \bar{R}=64`) and highlight that identical row in every subtable using the paper's signature tint (`gray` or `green`)!
   - *Tip*: If your final Main Results bump one compute-scaling knob slightly higher (e.g., `N=16` in ablations -> `N=20` in Main Results for Prophet), state that cleanly in 1 opening sentence of Main Results (`We use most of the default settings..., except that N is set to 20.`).
2. **Include a Counter-Intuitive Boundary Point**: e.g., `N=0` in Prophet Table 1e drops *below* Stage-1 (`49.97 vs 53.04`) while `N=1` jumps to `56.75` — proving few-shot activation is necessary; `K=1` gives accuracy > hit rate (`56.04 vs 53.04`) — proving LLM error correction!
3. **Include a Diagnostic Intermediate Metric When Possible**: e.g., `hit rate` alongside `accuracy` (Prophet 1c/1d), or `stage-1 acc.` alongside `accuracy (+delta)` (Prophet 1a/1b), or `RelAcc` alongside `RelSpd` (TwigVLM 4c–4f). Intermediate metrics make causal claims airtight.
4. **3-Step Ablation Discussion Formula (1 Bold-Lead Paragraph per Subtable)**:
   - **Setup** (1 sentence): What variants are compared and how control is maintained.
   - **Contrast** (1–2 sentences): Key numbers from subtable (default vs. critical extremes).
   - **Mechanism & Choice** (1–2 sentences): *Why* it happens (saturation, diminishing returns, noisy signal, distance to prediction head, KV-cache/FFN ratio) and why the default is optimal.

---

## 5. Deep Behavioral & Qualitative Proof (Closing the Loop)

Go one level deeper than aggregate accuracy by adding **one** of these two MIL signature analyses:

1. **Behavioral Partition Analysis (`Prophet` Fig. 3)** — *Best for reasoning / refinement / hybrid models*:
   - Partition all test samples into 3 mutually exclusive behavioral buckets relative to the base model (e.g., `keep top-1` 68.1%, `in top 2-K` 21.8%, `beyond top-K` 10.1%).
   - Plot `(a) behavior distribution` (pie) + `(b) per-type accuracy` (base vs. ours paired bar) to prove the method preserves easy cases AND unlocks massive gains on the hardest cases (`12% -> 42%`).
2. **Targeted Failure-Case Visual Comparison (`TwigVLM` Fig. 5)** — *Best for vision / token / attention / grounding models*:
   - Pick 2 crisp contrasting failure types (e.g., fine-grained OCR/small detail + spatial relation).
   - Show a compact grid: `Image + Prompt | Baseline 1 | Baseline 2 | Ours`, overlaying attention/selected tokens and placing the predicted answer + `✗`/`✓` directly underneath each panel.
   - Point readers to supplementary material for additional cases (`More examples are provided in the supplementary.`).
