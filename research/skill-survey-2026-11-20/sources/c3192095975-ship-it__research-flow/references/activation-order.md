> 说明：本文件中的具体 skill 名称都是“首选候选”，不是硬依赖。实际执行前必须根据 `capability-model.md` 和当前用户的已安装 skill 清单解析为可用能力；候选不存在时执行降级，不得假设名称必然可用。

# ResearchFlow Activation Order

本文件定义 ResearchFlow 的路线选择、阶段入口、技能优先级、同轮兼容性和测试场景。只有需要详细判断或发生冲突时读取。

## 1. 任务识别

### 进入流程

- 用户要求生成、修改、评估或推进一个具体科研项目。
- 请求需要文献、数据、实验、统计、图表、写作、审稿、回复或投稿材料。
- 请求涉及科研结论、研究主张、研究计划或学术交付物。
- 用户点名科研 skill，并且当前语境是实际项目。

### 不进入流程

- 只问概念、定义、公式解释或学习方法。
- 只做普通代码、工具配置、环境安装或非科研自动化。
- 普通商业数据分析、非科研图表或非科研写作。
- 纯翻译、普通润色，且不涉及研究主张、证据或投稿。
- 用户明确要求只处理一个独立小任务，并确认不需要科研流程。

当处于边界情况时，优先判断是否会产生科研结论或科研交付物，而不是只看是否出现“论文”“数据”“图”这些词。

## 2. 路线选择决策树

```text
是否存在具体科研项目？
  否 -> 不进入 ResearchFlow
  是 -> 是否存在正式系统综述/元分析/ARS 协议？
          是 -> systematic_review
          否 -> 是否明确目标为 Nature/CNS 系列？
                  是 -> nature
                  否 -> 主要交付物是中文论文/学位论文/课程研究？
                          是 -> chinese_thesis
                          否 -> 是否数学建模等竞赛？
                                  是 -> competition
                                  否 -> general
```

默认规则：

- 不确定目标期刊：`general`。
- 中文论文：`chinese_thesis`。
- 明确 Nature/CNS：`nature`。
- 明确系统综述/元分析：`systematic_review`。
- 不因出现 “Nature” 一词就切换路线；必须是实际目标或写作/投稿要求。

## 3. 入口阶段选择

按用户目标和已有工件选择最早的必要阶段：

| 用户请求 | 默认入口 | 前置检查 |
|---|---|---|
| 帮我确定方向/值不值得做 | 0-1 | 研究问题、资源、时间、否证条件 |
| 帮我找文献 | 2 | 关键词、领域、时间范围、来源类型 |
| 读这篇论文/做论文卡 | 2-3 | 来源合法性、全文可读性、输出类型 |
| 核对参考文献 | 4 | 已有引用列表或稿件 |
| 分析这组数据 | 5 | 数据字典、样本单位、许可和缺失信息 |
| 检查统计 | 6 | 统计结果或方法描述 |
| 根据结果做图 | 5-7 | 数据、分析结果、科学问题 |
| 写论文/章节 | 4-8 | 证据账本、结果、目标语言/venue |
| 整理成投稿包 | 9 | 稿件、图、引用、统计审查 |
| 自审/审别人稿 | 10 | 稿件或可审查产物 |
| 回复审稿 | 11 | 审稿意见和修改稿 |
| 做组会/答辩 PPT | 12 | 稿件、图、目标受众 |

如果用户要求跳到较后阶段但缺少前置工件，不直接补造结果；先做缺口审计，再执行最小前置阶段。

## 4. 阶段前置依赖

### 写作

允许进入阶段 8 的最低条件：

- `claim-evidence` 矩阵存在，或用户提供了可核验的等价材料；
- 研究问题、目标语言和目标 venue 已确定；
- 实证论文已有结果表、统计审查或明确的结果边界；
- 不确定内容已标记 `AUTHOR_INPUT_NEEDED`。

不满足时，回退到阶段 4、5 或 6。

### 图表

允许进入阶段 7 的最低条件：

- 数据或结果文件存在；
- 每个 panel 的科学问题已定义；
- 统计信息、误差和样本量可追溯；
- 图表计划没有和正文主张冲突。

不满足时，先做阶段 5/6，不先画“示意结果”。

### 生产

允许进入阶段 9 的最低条件：

- 可编辑稿件存在；
- 图、表、参考文献和补充材料版本一致；
- claim-evidence 和引用核验已通过；
- 统计审查和图表 QA 已完成，或有明确豁免。

不满足时，不在 `paper-spine` 里重新发明上游内容。

### 评审

允许进入阶段 10 的最低条件：

- 稿件或研究产物已冻结到可审查版本；
- 稿件位置、图表和证据可定位；
- 评审者没有被作者的完整思路和辩护理由过度锚定。

### 回复

允许进入阶段 11 的最低条件：

- 有编辑决定或审稿意见；
- 有对应修改稿或明确的待修改状态；
- 已知 decision type：minor、major、revise-and-resubmit 或 unclear。

### 4.1 阶段执行合同

| 阶段 | 主技能 | 必要输入 | 最低输出 | 通过条件 |
|---|---|---|---|---|
| 0 立项 | `research-flow` 自身 | 用户请求或已有材料 | 问题、目标、语言/venue、截止时间、约束、数据/伦理边界 | 范围明确，未解决决策被列出 |
| 1 定向 | `scientific-brainstorming` | 阶段 0 | 问题、候选假设、否证条件、成功/失败标准、最小验证 | 核心假设可检验，范围有边界 |
| 2 检索 | `nature-academic-search` | 阶段 1 或明确检索问题 | 检索式、来源、日期、数量、去重、纳入/排除标准 | 检索可复现，覆盖反对证据 |
| 3 精读 | `nature-downloader` 后 `nature-reader`/`nature-paper-card` | 阶段 2 或来源包 | 合法全文、来源映射、阅读笔记、页码/章节定位 | 关键来源已打开，定位可复核 |
| 4 证据 | `nature-ref-verifier`；Nature 路线可加 `nature-citation` | 阶段 3 | claim-evidence 矩阵、引文核验报告、未解决来源 | 每条核心主张有证据或明确缺口 |
| 5 分析 | `scientific-toolkit-skill`；实验型加 `nature-experiment-log` | 明确数据或实验材料 | 数据清单、代码、命令、结果、不确定性和环境 | 结果可复现，独立单位和样本量明确 |
| 6 统计 | `nature-statistics` | 阶段 5 或已有统计结果 | 统计审查、图表统计对齐、作者问题 | 设计、分析单位、检验和主张一致 |
| 7 图表 | `scipilot-figure-skill`；Nature 路线用 `nature-figure` | 阶段 5，必要时阶段 6 | 图表计划、source data、图片、QA 报告 | 每个 panel 有科学问题，图和证据一致 |
| 8 写作 | `scientific-writing` / `research-writing-skill` / `nature-writing` | 阶段 4；实证工作另需 5/6 | 初稿、claim register、未解决占位符 | 每条事实主张对应证据或 `AUTHOR_INPUT_NEEDED` |
| 9 生产 | `paper-spine` 的生产、构建、审计、投稿方法 | 阶段 7 和 8 | 可构建稿件、图表、引用、投稿包 | 构建、编号、图注、引用和包一致性通过 |
| 10 评审 | 自审用 `nature-reviewer`；审别人用 `peer-review` | 阶段 9 或可审查稿件 | P0/P1/P2 审稿报告、证据定位、作者待确认项 | 无未解决 P0，重大问题有依据 |
| 11 回复 | `nature-response` | 审稿意见和修改稿 | 评论跟踪表、回复信、修改稿、位置映射 | 每条意见和修改可追溯，包一致 |
| 12 交付 | `documents` / `presentations` / `pptx` / `office-academic-skill` 三选一 | 阶段 9/10/11 | 最终文件、声明、数据/代码可用性信息 | 作者确认、伦理/披露、最终审计完成 |

## 5. 技能优先级

在同一科研任务中，执行优先级为：

1. 用户当前明确指令；
2. 全局 `AGENTS.md` 的科研触发和安全边界；
3. `research-flow` 的路线和阶段规则；
4. 当前路线 owner；
5. 当前阶段主技能；
6. 辅助技能；
7. 输出适配器。

发生冲突时：

- 用户明确要求只调用某个 skill：先做兼容性提示，再按用户要求执行，除非会违反安全或证据边界。
- 当前项目状态与用户当前请求冲突：以当前请求为准，并记录变更。
- 两个领域 skill 功能重叠：选择更具体、更接近当前阶段的一个。
- 两个 skill 都能完成任务但输出格式不同：按目标交付物选择，不按模型偏好选择。
- 无法判断：保留在 ResearchFlow 层，问一个最关键的问题。

## 6. 同轮兼容规则

### 允许的组合

- `research-flow` + `nature-academic-search` + `nature-downloader`
- `research-flow` + `scientific-toolkit-skill` + `nature-statistics`
- `research-flow` + `scipilot-figure-skill` + `scientific-visualization`
- `research-flow` + `scientific-writing` + `stss`
- `research-flow` + `nature-response` + 修改稿一致性检查
- `research-flow` + `paper-spine` + 文档构建/引用审计

### 禁止的组合

- `paper-spine` + `academic-research-suite` 同时总控
- `scientific-writing` + `research-writing-skill` 同时主写
- `scientific-writing` + `nature-writing` 同时主写
- `scipilot-figure-skill` + `nature-figure` 同时设计同一组图
- `nature-reviewer` + `peer-review` 同一轮冒充两个独立审稿人
- `daily-paper-zotero` + `nature-literature-pipeline` 同时订阅
- 两个展示 skill 同时决定同一份 PPT 的叙事和版式

## 7. 常见场景示例

### 场景 1：帮我查某方向文献

```text
ResearchFlow：路线=general；阶段=2；主技能=nature-academic-search；辅助技能=nature-downloader（仅在需要全文时）
```

不启动写作、图表或评审 skill。

### 场景 2：把这篇论文写成综述

```text
ResearchFlow：路线=chinese_thesis 或 general；阶段=3；主技能=nature-reader；后续=4->8
```

如果用户没有提供检索来源，不能直接进入写作；先补齐来源和证据账本。

### 场景 3：根据数据画图

```text
ResearchFlow：路线=general；阶段=5；主技能=scientific-toolkit-skill；后续=6->7
```

如果数据已有且只做描述图，可以明确跳过 6，但不能跳过数据检查和 source data。

### 场景 4：审这篇论文

```text
ResearchFlow：路线=general；阶段=10；主技能=peer-review
```

如果是作者自审，改为 `nature-reviewer`；两者只能选一个。

### 场景 5：回复审稿意见

```text
ResearchFlow：路线=chinese_thesis 或 general；阶段=11；主技能=nature-response
```

必须先有审稿意见和修改稿，不能凭空生成修改位置。

### 场景 6：帮我做一个普通 Python 脚本

不进入 ResearchFlow；使用普通代码协作流程。

### 场景 7：解释一下 p 值是什么

不进入 ResearchFlow；这是概念问答，不是科研项目阶段。

## 8. 冲突测试清单

每次修改 ResearchFlow 后，至少验证：

1. 文献检索请求是否只启动检索主技能。
2. 论文写作请求是否先检查证据，而不是直接写作。
3. 数据图请求是否先检查数据和分析结果。
4. 自审请求是否选择 `nature-reviewer` 而不是 `peer-review`。
5. 审别人稿请求是否选择 `peer-review`。
6. 目标 Nature 的请求是否锁定 `nature` 路线。
7. 普通脚本请求是否不触发 ResearchFlow。
8. 概念问答是否不触发 ResearchFlow。
9. 同时提到写作和图表时，是否只先执行当前阶段主技能。
10. 缺少前置工件时，是否输出明确缺口而不是编造结果。

## 9. 降级映射

主技能不可用时，先报告缺失，再选择同职责下最接近的已安装 skill，并说明替代边界：

- `nature-figure` 缺失 -> 当前路线 figure owner + `scientific-visualization` 导出；
- `nature-citation` 缺失 -> `nature-ref-verifier` + `nature-academic-search`；
- `paper-spine` 缺失 -> 当前 writing owner + 文档构建 + 手工投稿包审计；
- `nature-response` 缺失 -> 手工评论跟踪表 + 修改稿一致性检查；
- `academic-research-suite` 缺失 -> `nature-academic-search`、`nature-reader`、`scientific-writing` 和 `peer-review` 组成最小正式综述流程。

降级不能跳过证据门、统计门、图表 source data 检查或最终人工确认。
