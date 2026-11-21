# ResearchFlow Capability Model

这个模型定义科研流程需要什么能力，而不是要求某个特定 skill 必须存在。实际使用的 skill 由此人当前安装的 skill 清单动态解析。

## 1. 能力槽

| 能力槽 | 主要职责 | 强信号 | 默认候选（仅在可用时） |
|---|---|---|---|
| `scope` | 选题、假设、研究设计、开题 | research question, hypothesis, study design, proposal, 科研选题, 假设, 研究设计 | `scientific-brainstorming`、`nature-proposal-writer`、`academic-research-suite` |
| `search` | 文献发现、检索策略、文献库管理 | literature search, PubMed, OpenAlex, Crossref, arXiv, BibTeX, 文献检索 | `nature-academic-search`、`literature-review`、`citation-management` |
| `acquisition` | 合法获取全文和补充材料 | full text, PDF, download, CNKI, institutional access, 全文下载 | `nature-downloader` |
| `reading` | 精读、全文阅读、论文卡、来源定位 | paper reader, paper card, bilingual, page locator, 精读, 论文卡 | `nature-reader`、`nature-paper-card` |
| `evidence` | 引文核验、claim-to-source、参考文献审计 | citation verification, claim evidence, reference verifier, 引文核验 | `nature-ref-verifier`、`nature-citation` |
| `analysis` | 数据处理、计算、模拟、统计计算 | Python, MATLAB, data analysis, simulation, ML, 数据分析, 仿真 | `scientific-toolkit-skill` 及其子能力 |
| `statistics` | 统计设计、报告和图表统计审查 | experimental unit, replication, effect size, p-value, 统计审查 | `nature-statistics`、`statistical-analysis` |
| `figures` | 数据图、机制图、组合图、投稿图 | figure, plot, visualization, matplotlib, 图表, 论文图 | `scipilot-figure-skill`、`scientific-visualization`、`nature-figure`、`academic-figure-skill` |
| `writing` | 论文、综述、开题、章节写作和改写 | manuscript, thesis, scientific writing, 论文写作, 综述, 开题 | `scientific-writing`、`research-writing-skill`、`nature-writing` |
| `production` | LaTeX/Word 构建、投稿包和格式检查 | LaTeX, submission package, compile, 投稿包 | `paper-spine`、`documents`、PDF/构建工具 |
| `review` | 自审、同行评审、模拟审稿 | peer review, reviewer, critique, 审稿, 评审 | `nature-reviewer`、`peer-review`、ARS reviewer |
| `response` | 审稿回复、返修跟踪、修改位置映射 | rebuttal, response to reviewer, 审稿回复, 返修 | `nature-response` |
| `delivery` | 文档、PPT、表格和最终交付 | docx, pptx, presentation, slides, 汇报, 文档 | `documents`、`presentations`、`pptx`、`spreadsheets`、`office-academic-skill` |
| `orchestration` | 总流程或多阶段编排 | end-to-end, workflow, orchestrator, 总流程 | `paper-spine`、`academic-research-suite`（按路线二选一） |
| `memory` | 长期偏好、项目背景和决策上下文 | profile, preference, project history, 个人档案 | `personal-profile`（可选） |

一个 skill 可以匹配多个能力槽，但一次科研阶段只能占一个主能力槽。例如 `scientific-toolkit-skill` 可匹配 `analysis`，不应同时作为 `writing` 的主技能。

## 2. 路线偏好

路线只改变候选优先级，不要求固定 skill 名称。

### `general`

- `writing`: 优先 `scientific-writing`，其次通用 scientific/manuscript writer；
- `figures`: 优先 `scipilot-figure-skill`，其次 `scientific-visualization`；
- `review`: 优先 `peer-review` 或通用 manuscript reviewer；
- `production`: 优先 `paper-spine`，没有时用通用文档/构建适配器。

### `chinese_thesis`

- `writing`: 优先 `research-writing-skill`；
- `figures`: 优先 `scipilot-figure-skill`；
- `evidence`: 优先 `nature-ref-verifier`；
- `review`: 优先 `nature-reviewer` 或中文论文评审能力。

### `nature`

- `writing`: 优先 `nature-writing`；
- `figures`: 优先 `nature-figure`；
- `evidence`: 优先 `nature-citation` + `nature-ref-verifier`；
- `review`: 优先 `nature-reviewer`；
- 如果 Nature 专用 skill 不存在，回退到通用写作/图表/评审，但必须说明其不是期刊专用检查。

### `systematic_review`

- `orchestration`: 优先 `academic-research-suite`；
- `search`: 优先正式系统综述检索能力；
- `reading`: 优先具备全文和页码定位的 reader；
- `review`: 优先 `peer-review` 或 ARS reviewer；
- 不得同时让 `paper-spine` 作为同一项目的总编排。

### `competition`

- `orchestration`: 优先 `cumcm-live-workflow`；
- `analysis`: 优先科学计算能力；
- `figures`: 优先科学计算和绘图能力；
- 不加载通用期刊写作流程，除非用户要求把竞赛成果转成论文。

## 3. 选择规则

对某个能力槽，按以下顺序选择：

1. 用户明确点名的 skill；
2. 当前路线专用候选；
3. 能力匹配分数高且职责单一的 skill；
4. 语言和交付物匹配；
5. 有可用脚本/本地检查器的 skill；
6. 允许隐式调用的 skill；
7. 依赖已满足的 skill；
8. 用户长期偏好；
9. 路径优先级更高的本地安装；
10. 仍然无法决定时，只问一个最关键的问题。

路径优先级建议：

```text
项目级 skill
> 用户 CODEX_HOME skill
> 用户 ~/.codex skill
> ~/.agents skill
> 插件缓存或系统级 skill
```

同名 skill 出现多次时，选择最高优先级的版本，并在能力图中保留其他路径作为 alternates。

## 4. 缺失与降级

| 缺失能力 | 最低降级 |
|---|---|
| `scope` | 使用内置研究 brief 和假设检查 |
| `search` | 使用宿主搜索 + 可复现检索日志 |
| `reading` | 使用 PDF/文本读取 + 来源定位表 |
| `evidence` | 使用 claim-evidence 矩阵 + 手工核验 |
| `analysis` | 使用标准 Python/MATLAB 基础能力 |
| `statistics` | 使用内置统计审查清单 |
| `figures` | 使用 Matplotlib/基础可视化 |
| `writing` | 使用通用科学写作模板 |
| `production` | 使用 Markdown/Word/LaTeX 基础构建 |
| `review` | 使用结构化评审清单，不得冒充外部审稿人 |
| `response` | 使用评论跟踪表 + 修改位置表 |
| `delivery` | 输出 Markdown 或纯文本，并说明格式限制 |

降级必须记录在 `capability_map.degraded_roles` 中，不能静默降低质量。

## 5. 能力图示例

```yaml
route: chinese_thesis
modifiers: [lab]
phase: figures
resolved_at: 2026-11-20T00:00:00Z
skills:
  search:
    selected: nature-academic-search
    alternatives: [literature-review]
    confidence: high
    availability: available
  reading:
    selected: nature-reader
    alternatives: [nature-paper-card]
    confidence: high
    availability: available
  analysis:
    selected: scientific-toolkit-skill
    confidence: high
    availability: available
  figures:
    selected: scipilot-figure-skill
    alternatives: [scientific-visualization]
    confidence: high
    availability: available
  writing:
    selected: research-writing-skill
    confidence: high
    availability: available
unresolved_roles: []
degraded_roles: []
```

## 6. 冲突规则

- 一个能力槽只能有一个 selected owner。
- 同一轮不能有两个同类 owner。
- `paper-spine` 和 `academic-research-suite` 不能同时是同一项目的 orchestration owner。
- Nature 路线内不能同时让 Nature 专用和通用 skill 主写/主图。
- `review` 能力只能有一个正式审稿 owner；自审和同行评审不能伪装成两个独立审稿人。
- `humanizer-zh-academic` 只能进入 `writing` 的最终风格修饰，不是 `review` 或证据能力。
- `personal-profile` 只进入 `memory`，不控制科研阶段。

## 7. 可用性状态与 override

每个能力槽记录：

```yaml
selected:
alternatives: []
availability: ready | likely | unverified | unavailable
confidence: high | medium | low
reason:
override_source:
```

状态含义：

- `ready`: 未发现外部依赖问题。
- `likely`: 声明的依赖看起来存在，但没有执行真实调用。
- `unverified`: 声明了 MCP/API/浏览器等外部依赖，发现阶段没有验证服务。
- `unavailable`: 必要环境变量、命令或本地文件缺失。

用户 override 的优先级高于自动推断，但低于用户当前明确指令和安全边界。

```yaml
# ~/.codex/research-flow-overrides.yaml
roles:
  search: my-literature-tool
  figures: my-plot-tool
  writing: my-thesis-writer
```

如果 override 指定的 skill 不存在或不可用，标记 `unavailable`，不要静默回退到另一个同名品牌。

## 8. 非标准格式

支持识别：

- `SKILL.md`：标准格式；
- `manifest.yaml`：manifest fallback；
- `agents/openai.yaml`：metadata fallback。

非标准格式只用于建立候选能力，不自动执行它的脚本。低置信度或缺少描述时，优先使用 override 或 baseline。
