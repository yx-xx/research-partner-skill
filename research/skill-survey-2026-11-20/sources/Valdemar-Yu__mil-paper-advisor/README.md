# MIL Paper Advisor (`mil-paper-advisor`)

An Agent Skill ("电子导师") for **MIL-style** (MILVLG, Hangzhou Dianzi University) top-tier AI/CV academic paper storytelling, LaTeX polishing, hypothesis-closing experimental design, and figure/table prompt engineering — compatible with **Antigravity**, **Claude Code**, and **Codex**.

Distilled from flagship MILVLG publications — **Prophet (CVPR 2023)** and **TwigVLM (ICCV 2025)** — this skill goes far beyond generic Level-1 boilerplate (`Intro / Related / Method / Exp`). Its core focus is the **MIL Story Engine**: threading Level-2 subsections into a tight causal detective chain so the proposed method feels *inevitable*.

```text
[Symptom / 2 Orthogonal Gaps (i), (ii)]
                 │
                 ▼
[Controlled Pre-Study / Pipeline Anatomy]   ("We ask: ...?")
                 │
                 ▼
[Mechanistic Abstraction Leap]              (e.g., "closer to prediction head",
                 │                           "latent answer space")
                 ▼
[One Simple Carrier -> Dual Payoff]         (1 lightweight module / base model
                 │                           solves (i) & (ii) 1-to-1)
                 ▼
[Closed-Loop Hypothesis Verification]       (2x3 Kaiming-style ablation grid +
                                             single-accent visual lock)
```

---

## What It Does (5 Advisor Modes)

The skill uses **progressive disclosure** (`SKILL.md` loads only the needed files under `references/` on demand):

| Mode | Trigger Examples | What You Get |
| :--- | :--- | :--- |
| **1. Story & Subsection Spine** | 设计 story、反推前置 Pilot Study、梳理二级标题因果链 | 5-Question Story Gate diagnosis + 4 reusable Pre-Study probe archetypes + **Subsection-by-Subsection Baton Storyboard** (`Catch -> Do -> Pass`) |
| **2. Draft & MIL Polish** | 润色英文/LaTeX、去 AI 味、反防御性改写 | Sharp Chinese mentor critique + drop-in academic English/LaTeX rewrite using MIL restraint (`conceptually simple`, `We ask:`, `Without bells and whistles`) |
| **3. Experiments & Ablations** | 设计前置探针、公平控制公式、2x3 消融矩阵 | Decoupled probe protocol + fairness control equation + **2x3 six-subtable ablation blueprint** separating hypothesis-closure slots from hyperparameter sweeps |
| **4. Figures, Tables & Prompts** | 设计 Fig. 1 Teaser / 架构图 / 画图 prompt / Matplotlib | Paper-wide **Single-Accent Color Lock** (HEX palettes) + anti-AI-slop diagram prompts + editable SVG specs + publication-grade Matplotlib & LaTeX `booktabs` templates |
| **5. Pre-Submission Audit** | 模拟导师审稿、查孤儿模块、交稿体检 | Audit report flagging orphan subsections, unverified hypotheses, defensive leaks, and figure/table inconsistencies |

---

## Repository Structure

```text
mil-paper-advisor/
├── SKILL.md                                 # Entry point: advisor persona, 5-Question Gate, mode routing
├── agents/
│   └── openai.yaml                          # Codex UI & invocation metadata
├── references/
│   ├── argumentation-and-structure.md       # MIL Story Engine, Mechanistic Abstraction, Subsection Baton Chains
│   ├── writing-style-and-polish.md          # Linguistic fingerprint, phrasebank, anti-defensive rules, LaTeX style
│   ├── experiment-and-ablation.md           # Pilot probes, fairness controls, 2x3 hypothesis-closing ablation grid
│   ├── figure-and-table-design.md           # Single-accent color lock, HEX palettes, figure archetypes, booktabs tables
│   └── drawing-prompts.md                   # AI diagram prompts, editable SVG specs, Matplotlib publication boilerplate
├── LICENSE
└── README.md
```

---

## Install

Clone directly into the skills directory of your coding agent:

### Antigravity (Workspace or Global)

```bash
# Workspace-level (recommended for sharing inside a paper repo)
git clone https://github.com/Valdemar-Yu/mil-paper-advisor.git .agents/skills/mil-paper-advisor
```

### Claude Code

```bash
git clone https://github.com/Valdemar-Yu/mil-paper-advisor.git ~/.claude/skills/mil-paper-advisor
```

### Codex

```bash
git clone https://github.com/Valdemar-Yu/mil-paper-advisor.git ~/.codex/skills/mil-paper-advisor
```

To update an existing installation:

```bash
git -C <path-to-skill>/mil-paper-advisor pull
```

---

## Usage Examples

- **Restructure a draft's story & subsections**
  ```text
  Use mil-paper-advisor (Mode 1) to diagnose this paper draft, design 1–2 pre-studies from our existing diagnostics, and build a Level-2 subsection baton storyboard.
  ```
- **Polish a section in MIL style**
  ```text
  用 mil-paper-advisor 润色这段 Introduction，去掉防御性表达和 Contribution 列表，补上 (i)/(ii) 短板和 We ask 设问。
  ```
- **Plan a 2x3 ablation grid**
  ```text
  用 mil-paper-advisor 帮我设计一个 2x3 六子表消融矩阵，确保前两格直接闭环我们在 Section 2 提出的机理假说。
  ```
- **Generate figure drawing prompts & Matplotlib plots**
  ```text
  用 mil-paper-advisor 给 Fig. 1 Teaser 和 Method 架构图生成 MIL 风格（鼠尾草绿主色）的绘图 Prompt，并给 Pilot Study 生成 300-DPI 矢量 PDF Matplotlib 代码。
  ```

---

## Reference Corpus & Extensibility

Initial methodology and visual design patterns are distilled from two open-access MILVLG papers:
- **Prophet (CVPR 2023)** — Zhenwei Shao, Zhou Yu, Meng Wang, Jun Yu, *Prompting Large Language Models with Answer Heuristics for Knowledge-based Visual Question Answering* ([GitHub](https://github.com/MILVLG/prophet))
- **TwigVLM (ICCV 2025)** — Zhenwei Shao, Mingyang Wang, Zhou Yu, et al., *Growing a Twig to Accelerate Large Vision-Language Models* ([GitHub](https://github.com/MILVLG/twigvlm))

The skill includes a built-in **Style Corpus Extension Protocol** in `SKILL.md`: feed additional MIL or target-lab papers to extract only net-new storytelling patterns, probe archetypes, or visual layouts without bloating the entrypoint.

---

## License

MIT. See [LICENSE](LICENSE).
