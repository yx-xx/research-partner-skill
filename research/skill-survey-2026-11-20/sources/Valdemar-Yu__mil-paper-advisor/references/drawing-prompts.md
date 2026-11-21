# MIL Drawing Prompts, Vector Blueprints & Matplotlib Code Templates

Use this reference whenever generating **ready-to-run drawing prompts** (for AI image/diagram generators like Gemini Image / Nano Banana / GPT-Image), **editable vector blueprints** (SVG / Draw.io / PPTX), or **publication-grade Matplotlib code** in authentic MIL style (Prophet CVPR'23 & TwigVLM ICCV'25).

---

## 1. The 4-Step MIL Prompt Construction Workflow

Before writing any drawing prompt for a student's paper, ALWAYS run these 4 steps:

1. **Choose Archetype & Column Span**:
   - Page-1 Teaser -> 1-column (`~1:0.9` or `16:10` compact aspect ratio): Archetype 1A (Stacked Comparison) or 1B (Architecture + Mini Bars).
   - Main Method Figure -> Full 2-column width (`~2.4:1` or `16:6.5` wide landscape): Archetype 2A (2-Stage Walkthrough) or 2B (3-Panel Lifecycle).
   - Data Charts -> **NEVER use AI image generation for quantitative bar/line/pie charts!** Always generate clean Matplotlib/Python vector PDF code (Section 4 below) so numbers and axes are 100% exact.
2. **Enforce Information Budget**: Limit every box to 2–5 crisp words. Never dump full sentences inside diagram blocks unless it is a concrete prompt/question example box.
3. **Ground With One Concrete Sample**: Fill in a REAL image scenario, REAL question/prompt, REAL token/candidate/score numbers, and REAL output (`✗` wrong baseline vs `✓` right ours).
4. **Lock Palette & Negative Constraints**: Inject the exact HEX palette (Palette A Botanical Blue-Green OR Palette B Slate-Amber) and the **Anti-AI-Slop Guardrail block** verbatim so the generator outputs crisp CVPR/ICCV vector style instead of glossy sci-fi infographics.

---

## 2. AI Diagram / Illustration Prompt Templates

Adapt the bracketed `[...]` fields directly from the user's paper. Output the final prompt in clean English (best text rendering accuracy in modern image models).

### Template P1A: Page-1 Teaser — Stacked Conceptual Comparison (Prophet Fig. 1 Style)

```text
Create a clean, flat, publication-ready CVPR/ICCV academic vector schematic diagram on a pure solid white background (#FFFFFF), aspect ratio 4:3, designed to fit a single-column Page-1 teaser figure.

Visual Style & Color Lock (MIL Slate-Amber Academic Palette):
- Strict 2D flat vector graphics, clean crisp thin strokes (1.2pt), slightly rounded rectangles (5pt corner radius), clean sans-serif typography (Helvetica/Arial), balanced whitespace.
- Frozen foundation model blocks: dark slate blue (#3B5978) fill with white bold label and a crisp white snowflake icon in the top-left corner.
- Trainable / our proposed module: warm amber-ochre (#E5A967) fill with dark text.
- Heavy competing module: muted terracotta (#C46D3B) fill with white text.
- Auxiliary off-the-shelf module: muted steel blue (#779ECB) fill with white text.
- Highlighted novel intermediate signal: soft pale butter-yellow (#FFF3CD) badge/strip.

Layout (Left Input Column + Right 3-Row Stacked Comparison):
- Left column (28% width): Shared concrete inputs stacked vertically with compact labels:
  (Q) "[CONCRETE SHORT QUESTION, e.g., what fruit comes from these trees?]"
  (V) A crisp small realistic square thumbnail photo of [CONCRETE SCENE]
  (C) Small steel-blue box "[AUX MODULE]" pointing to short text "[CONCRETE INTERMEDIATE TEXT]"
  [Optional (K) if rival uses extra resource]
- Right section (72% width): Three cleanly stacked horizontal pipeline rows separated by subtle horizontal spacing:
  1. Top row titled "[Baseline 1 Name]": minimal arrows feeding C and Q directly into dark slate-blue frozen "[LLM/VLM]" block -> output "A".
  2. Middle row titled "[Baseline 2 Name]": C and Q -> frozen block -> terracotta "[Complex Rival Model]" (also receiving V and K via thin orange arrows) -> output "A".
  3. Bottom row titled "[OurMethod] (ours)" in bold: V and Q -> warm amber "[Our Lightweight Module]" -> soft yellow highlight "[Our Key Signal Name]" -> dark slate-blue frozen "[LLM/VLM]" (with C and Q) -> output "A".

Strict Negative Constraints:
- NO 3D effects, NO glossy gradients, NO drop shadows, NO dark backgrounds, NO glowing neon lines, NO clipart robots/brains, NO decorative icons outside the snowflake/arrow symbols, NO misspelled or gibberish text, NO extra border around the whole image.
```

### Template P1B: Page-1 Teaser — Architecture + Dual-Advantage Card (TwigVLM Fig. 1 Style)

```text
Create a clean, flat, publication-ready ICCV/CVPR academic vector overview figure on a pure white background (#FFFFFF), aspect ratio 16:10, split cleanly into two side-by-side panels labeled "(a) [MethodName] architecture." (left 42%) and "(b) Two key advantages of [MethodName]." (right 58%).

Visual Style & Color Lock (MIL Botanical Blue-Green Palette):
- Crisp 2D flat vector diagram, 1.2pt uniform strokes, rounded rectangles (4pt radius), clean Helvetica/Arial sans-serif labels, pure white canvas.
- Frozen Base Model blocks: pale sky-blue fill (#DAEAF6), steel-blue border (#5B8DBE), crisp black text, small blue snowflake icon indicating frozen weights.
- Proposed Learnable Module (Ours): pale sage-green fill (#E2F0D9), leaf-green border (#70AD47), crisp black text, small orange flame icon indicating learnable weights.
- Advantage highlight dashed boxes: top card bordered in muted rose dashed line (#B85A8A); bottom card bordered in leaf-green dashed line (#6AA84F).

Panel (a) Left — Architecture Stack:
- A vertical pale-blue container labeled "base [Model] (deep)" containing stacked horizontal rounded bars from bottom to top: "layer 1", "...", "layer K", "layer K+1", "...", "layer L", "[Model] head", with "[Input 1]" and "[Input 2]" arrows entering the bottom.
- Branching cleanly from right after "layer K" to the right into a vertical pale-green container labeled "learnable [ModuleName] (shallow)" with a small flame icon: stacked rounded bars "[module] layer(s)" -> "[module] head".

Panel (b) Right — Two Stacked Advantage Cards:
- Top dashed rose card titled "Better [Advantage 1, e.g., accuracy retention]":
  - Left side: compact side-by-side visual comparison of [Baseline] (blurred/misaligned focus on concrete photo) vs. "ours" (sharp accurate focus on target region) guided by "[Mechanism 1 Name]".
  - Right side: clean minimal 2-bar chart (no top/right spines, horizontal red dotted reference line at 100%) comparing steel-blue "[Baseline]" bar ([NUM1]) vs. fresh-green "ours" bar ([NUM2], bold).
- Bottom dashed green card titled "Higher [Advantage 2, e.g., generation speed]":
  - Left side: clean mini schematic of "[Mechanism 2 Name]" showing [shallow/fast path] feeding tokens to [deep/target path] with green checkmark chips and one red cross chip.
  - Right side: clean minimal 2-bar chart (no top/right spines, horizontal red dotted reference line) comparing steel-blue "[Baseline]" bar ([NUM3]) vs. fresh-green "ours" bar ([NUM4], bold).

Strict Negative Constraints:
- NO 3D bevels, NO shadows, NO gradients, NO decorative backgrounds, NO extra clutter, NO unreadable micro-text, NO distorted numbers. Every label must be crisp, flat, horizontal, and legible.
```

### Template P2: Full-Width Multi-Stage / Lifecycle Framework Diagram (Prophet Fig. 2 & TwigVLM Fig. 4 Style)

```text
Create a clean, flat, wide publication-ready CVPR/ICCV academic system architecture figure on a pure white background (#FFFFFF), wide landscape aspect ratio 12:5 (designed for full two-column page width).

Visual Style & Color Lock:
- Strictly flat 2D vector diagram, Helvetica/Arial sans-serif font, uniform 1.2pt strokes, rounded rectangles (4pt radius), subtle light-gray rounded background containers (#F5F6F8) to group each stage cleanly.
- Palette: [Choose Palette A: frozen base = pale sky-blue #DAEAF6 / border #5B8DBE + snowflake icon; trainable ours = pale sage-green #E2F0D9 / border #70AD47 + flame icon; visual tokens = soft coral chips #E7A698; pruned tokens = faded translucent chips with dashed outline and red X] OR [Choose Palette B: frozen LLM = dark slate blue #46698C + white snowflake; trainable encoder = warm amber #E5A967; prompt head = pale yellow #FFF3CD; in-context examples = pale green #E2F0D9; test input = pale lavender #EAE6F5].
- Dashed arrows (-- ->) strictly denote weight initialization or attention/retrieval guidance; solid thin black arrows (--->) denote forward data flow.

Horizontal Panel Layout ([2 stages left-to-right with bottom labels "Stage-1 Name (§3.2)" and "Stage-2 Name (§3.3)"] OR [3 equal-height panels labeled "(a) Training stage", "(b) Inference stage ([phase 1])", "(c) Inference stage ([phase 2])"]):
- Panel 1: [Exact modules stacked vertically/horizontally, concrete input photo of SCENE + text prompt "CONCRETE PROMPT", explicit weight-init dashed arrows / loss arrow at top].
- Panel 2: [Same concrete photo + prompt at bottom; show exact transformation — e.g., visual token chips passing through layer 1..K, dashed red/green guidance arrow from our module performing selection/pruning, OR concrete latent-space cluster scatter with nearest neighbors and scored candidate list].
- Panel 3 (if 3-panel): [Same concrete photo + prompt; show concrete output token chips generated by fast path "[tok1] [tok2] [wrong_tok]" verified in parallel by deep path with green checkmarks on "[tok1]" "[tok2]", red cross on "[wrong_tok]", and corrected "[right_tok]" with green checkmark].

Strict Negative Constraints:
- NO 3D boxes, NO drop shadows, NO neon glows, NO dark theme, NO placeholder "lorem ipsum" or vague "Module A/B" labels, NO overlapping arrows or text collisions, NO busy textures. Every box text and example token must be clean, horizontal, and immediately readable.
```

---

## 3. Editable Vector Blueprint Prompt (SVG / Draw.io / PPTX Workflow)

For final camera-ready figures where exact LaTeX typography and crisp vector arrows matter most, ask the agent to generate an **editable SVG** (importable into Illustrator / Figma / Inkscape / PowerPoint -> export PDF) using this layout specification:

- **Canvas size**:
  - 1-column figure (CVPR/ICCV `3.25 in` = `234 pt`): design at `650 x 480 px` (`viewBox="0 0 650 480"`), body font `13–15px` (scales cleanly to `7–8pt` in print!).
  - 2-column figure (CVPR/ICCV `6.875 in` = `495 pt`): design at `1400 x 560 px` (`viewBox="0 0 1400 560"`), body font `14–16px` (scales cleanly to `7.5–8.5pt` in print!).
- **SVG Strict Rules**:
  - Define reusable `<defs>` for clean triangular arrowheads (`#arrow-solid`, `#arrow-dashed`, `#arrow-accent`) and consistent CSS classes (`.base-box`, `.ours-box`, `.stage-bg`, `.label-bold`, `.label-sub`).
  - Place explicit `x, y, width, height` on an 8px layout grid so every stacked layer aligns to the pixel.
  - Leave explicit `<rect>` image slots (dashed gray placeholder with dimensions) if the student will drop in real high-res PNG photos/heatmaps in PowerPoint/Illustrator afterwards.

---

## 4. Publication-Grade Matplotlib Style Template (Exact MIL Plot Aesthetics)

Use this Python boilerplate for ALL quantitative charts (Pilot Study curves/bars, Speed comparison dual-label bars, Behavioral breakdown pie+bar). Never ship default Matplotlib aesthetics!

```python
import matplotlib.pyplot as plt
import numpy as np

# === MIL Publication Style (TwigVLM ICCV'25 / Prophet CVPR'23) ===
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Helvetica", "Arial", "DejaVu Sans"],
    "font.size": 9,
    "axes.titlesize": 9.5,
    "axes.labelsize": 9,
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
    "legend.fontsize": 8,
    "axes.linewidth": 0.8,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.edgecolor": "#333333",
    "pdf.fonttype": 42,       # Embed TrueType fonts for clean CVPR/ICCV PDF
    "ps.fonttype": 42,
    "figure.dpi": 300,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.03,
})

# Locked MIL Palettes
MIL_GREEN_PALETTE = {
    "base_line": "#666666",
    "baseline1": "#4C82B6",   # Steel blue (e.g., FastV)
    "baseline2": "#9A8AC4",   # Muted purple (e.g., VisionZip)
    "ours":      "#77C374",   # Fresh sage green (TwigVLM)
    "delta_red": "#C62828",   # Crimson red for RelSpd / delta labels
    "curve":     "#2E75B6",   # Clean blue line plot
}

MIL_PROPHET_PALETTE = {
    "base_bar":  "#4E7FA8",   # Steel blue (MCAN)
    "ours_bar":  "#EE854A",   # Warm orange (Prophet)
    "pie_easy":  "#9AC786",   # Sage green (keep top-1)
    "pie_mid":   "#3B5B7A",   # Dark slate blue (in top 2-K)
    "pie_hard":  "#DBA942",   # Warm amber gold (beyond top-K)
}

def plot_mil_dual_annotated_bars(
    ax, groups, methods_vals, methods_rel, base_val, title, ylabel,
    colors=None, show_legend=False
):
    """TwigVLM Fig. 6 style: grouped bars + horizontal base dotted line +
    stacked black absolute value & crimson red relative percentage labels."""
    if colors is None:
        colors = [
            MIL_GREEN_PALETTE["baseline1"],
            MIL_GREEN_PALETTE["baseline2"],
            MIL_GREEN_PALETTE["ours"],
        ]
    n_groups = len(groups)
    n_methods = len(methods_vals)
    x = np.arange(n_groups)
    width = 0.24

    ax.axhline(base_val, color=MIL_GREEN_PALETTE["base_line"],
               linestyle=":", linewidth=1.1, zorder=1, label="Base Model")

    for i, (name, vals) in enumerate(methods_vals.items()):
        offset = (i - (n_methods - 1) / 2) * width
        bars = ax.bar(x + offset, vals, width=width * 0.92,
                      color=colors[i], edgecolor="none", zorder=2, label=name)
        rels = methods_rel[name]
        for bar, v, r in zip(bars, vals, rels):
            ax.text(bar.get_x() + bar.get_width() / 2, v + 1.8, f"{v:.1f}",
                    ha="center", va="bottom", fontsize=6.8, color="#222222")
            ax.text(bar.get_x() + bar.get_width() / 2, v + 0.2, f"{r}%",
                    ha="center", va="bottom", fontsize=6.6,
                    color=MIL_GREEN_PALETTE["delta_red"])

    ax.set_title(title, pad=6)
    ax.set_ylabel(ylabel)
    ax.set_xticks(x)
    ax.set_xticklabels(groups)
    if show_legend:
        ax.legend(frameon=False, ncol=n_methods + 1,
                  loc="upper center", bbox_to_anchor=(0.5, -0.18))
```

### Quick Chart Polish Checklist Before Exporting PDF
- [ ] Export directly to vector `.pdf` (`plt.savefig("fig_speed.pdf")`), NEVER low-res `.jpg` or blurry `.png`.
- [ ] Figure aspect ratio matches exact LaTeX column width (`figsize=(3.3, 2.1)` for 1-column; `figsize=(6.8, 2.3)` for 2-column) so font sizes match body text without ugly scaling!
- [ ] Accent color for `ours` matches Figure 1, Framework Figure, and Ablation Table highlight!
- [ ] Top/right spines removed; no background tint; no overlapping bar annotations.
