# Research Partner skill 扩展调研与源码库

调研截至 **2026-11-20（Asia/Shanghai）**。本轮将前期候选扩展到 **30个项目、31份固定分支快照**，保留 **1,870份源码/文档文件，251个 `SKILL.md` 入口文件**。入口数包含分支重复、模板及同名模块，不等于251项独立创新。源码文件约15.7 MiB，另有快照元数据和调研产物。

**主要结论：优先借少量具体机制，保持 research-partner 作为主推进器。** 现有skill已经具备查新、贡献判断、判别实验、诚实报告、预算、结果回写和接续原则。最有增量的是候选独立复测后晋升、运行状态分层、软件资源控制的触发验证、数字来源到稿件的映射、论文与生效配置的一致性、成功/失败条件桥接及对审稿意见的反证。

## 从这里读

| 文件 | 用途 |
|---|---|
| [重点源码阅读笔记](analysis/reading-notes.md) | 逐项可取之处、具体来源、检查器真实范围及不宜照搬的部分 |
| [与现有skill的对照/迁移建议](analysis/adoption-map.md) | 已覆盖/新增/不采用，优先级、候选表述及8个后续行为评测场景 |
| [30项目目录](analysis/catalog.md) | 逐项目分支、创建时间、所选提交时间、下载范围及阅读深度 |
| [逐文件阅读日志](analysis/reading-log.json) | 55份文件的全文/重点段落/目录扫描范围；不能把下载量当阅读量 |
| [全部SKILL入口索引](analysis/skill-index.csv) | 251个入口的名称、说明摘要、路径、commit及是否进入阅读日志 |
| [来源manifest](manifest.json) | 完整commit、来源时间、每个保留文件的SHA256和下载范围 |
| [同名技能比较](analysis/same-name-comparison.json) | Kalaris与K-Dense的4对同名样本；只说明文本重叠，不判定来源谱系和质量 |

## 推荐优先参考的项目与模块

| 项目 | 推荐层面 | 最值得借鉴的部分 |
|---|---|---|
| EvoScientist / EvoSkills | 方法诊断与研究经验 | `experiment-craft` 从工作版本桥接到失败版本；`evo-memory` 有条件记录；图意规格 |
| UCL-ERL / skills | 机器人/AI研究补件 | `experiment-dossier-builder` 跨机器证据交接；`paper-code-consistency-auditor` 核对实际路径与配置 |
| lllllllama / RigorPilot-Skills | 可信复现与长运行 | README-first最小目标，科学含义变更，可比性报告，完成/收证/验收/数值匹配分开 |
| ed20922 / gevolve | 新近实验搜索设计 | 冻结评价、噪声和多次选择、假设轨迹、封存最终测试；明确承认不是沙箱 |
| ray-caster / autoresearch-skill | 具体控制器实现 | 入选后只用新的复测算确认均值；脚本控制保留/回退、越界和重复候选状态 |
| K-Dense-AI / science-superpowers | 科学计算可行性 | 真实规模探测、正确性参照、软件资源限制触发、事前约束审计及其边界 |
| TheSyBuilder / research-skills | 新近想法审计 | 瓶颈不预设解法、朴素机制审计、数据流/小数值dry-run |
| javimarlop / scientific-paper-skill | 小型写作补件 | 数字账本、跨章节一致性；DOI核验仅作身份检查 |
| shack / scientific-writing-review | 写作审查补件 | 审稿意见逐条核原文、排除抽取错误，keep/amend/drop；非科学质量评审替代 |

ARIS、ARS、PaperSpine、research-direction-check、Kalaris等也有值得取用的模块，详见阅读笔记。综合套件不作为整个主skill的直接替代；其重复组织和宿主假设有额外成本。

## “新”具体指什么

下面是本轮保存的仓库创建日/选定分支提交日，均换算为上海时间；它们不等于某个skill的发布日或最后修改日。新仓库可能导入旧代码，旧仓库也可能新增模块。不要把 GitHub `pushed_at` 当成 `main` 分支提交时间。

| 样本 | 仓库创建日 | 所选分支HEAD提交日 | 本轮判断 |
|---|---|---|---|
| TheSyBuilder/research-skills | 2026-11-17 | 2026-11-17 | 新出现，机制审计值得观察 |
| ray-caster/autoresearch-skill | 2026-11-17 | 2026-11-17 | 新出现，确认复测代码可直接研究 |
| ed20922/gevolve | 2026-11-18 | 2026-11-18 | 新出现，统计/访问边界考虑较细 |
| scanady/ds-mlops | 2026-11-19 | 2026-11-20 | 新出现，重点参考搜索与正式验证分层 |
| w1-23/scientific-figure | 2026-11-18 | 2026-11-20 | 新出现，几何引擎仅做定位筛选 |
| research-flow | 2026-11-20 | 2026-11-20 | 新出现，能力发现有用但只是启发式 |
| scientific-paper-skill | 2026-11-20 | 2026-11-20 | 新出现，数字账本小而明确 |
| scientific-writing-review | 2026-11-20 | 2026-11-20 | 新出现，审稿误报复核值得借鉴 |
| paper-easy-reader | 2026-11-20 | 2026-11-20 | 新出现，深读交付设计与结构检查分开看 |
| mil-paper-advisor | 2026-11-20 | 2026-11-20 | 新出现，仅借论证衔接，排除回避不利结果的规则 |
| ARIS | 2026-03-10 | 2026-11-19 | 老项目近期更新；本轮未逐个确认模块修改日 |
| ARS | 2026-02-26 | 2026-11-20 | 上游README为3.24.4，本机适配器为3.22.0；未升级本机 |
| EvoSkills | 2026-01-31 | 2026-11-14 | 近期更新；UTC提交时间为11月13日 |
| PaperSpine | 2026-05-17 | 2026-11-20 | 近期更新；注意当前协议与legacy Runner条款区别 |

另几项时效纠偏：Kalaris最近push为11月19日，但固定main提交为11月17日；Orchestra仓库push为10月11日，固定main提交为6月16日；Claude Scholar的codex分支固定提交为9月23日，main为10月19日，不能默认codex分支更新。完整UTC时间、上海时间和commit见目录/manifest。

## 下载与阅读边界

- **13份为成功下载归档后按类型/大小过滤的文本快照**；不是包含数据、模型、图片和依赖的完整Git克隆。
- **18份为源码子集**：从超时归档中保留完整文件成员，再从固定commit的raw路径补取重点入口、参考和脚本。每份 `SNAPSHOT.json` 明确标记 `selected_sources`，不能当成完整checkout。图像、二进制、大文件和依赖未下载。
- 下载位置是本目录的 [sources](sources)。不安装或激活这些skill。第三方提示词只作为调查材料，不改变本会话权限、宿主政策或研究任务范围。
- 重点文件有全文阅读，也有局部细读和目录筛选，逐项记录在reading-log。没有声称读完251个入口或逐行审计所有大型运行器。
- 本轮做源码分析及产物一致性检查，没有实际运行第三方实验循环、付费模型调用、真实科研实验或端到端性能测试。推荐是设计适配判断，非实测质量排名。
- 原始失败归档已删除；失败与路径探测记录保留在discovery。部分404是猜测路径不存在，并不表示整个项目不可用。CCFA、Research-AI-Orchestrator、ai-auto-research等另外线索在前轮访问时为404，未纳入30个已下载项目或作实质推荐。

## 检索与复核方法

以GitHub原仓库为一手来源，从前轮项目出发，补查近期创建/更新的研究、学术、autoresearch和机器人skill；检索条件包括 `created:>=2026-09-01`、`pushed:>=2026-11-01` 及 `archived:false fork:false`。原始结果、repo元数据、分支解析、下载/补取结果在 [discovery](discovery)。这是有针对性的近期样本调查，不是全生态穷尽目录。

所有保留文件对应固定commit。部分归档下载使用短SHA，其完整SHA由GitHub tar的全局PAX comment取得；快照均保存完整40位SHA。保留LICENSE等可得来源文件；直接搬运代码时仍需依据对应版本和文件的许可，不由仓库目录数量推定许可相同。

采集脚本在 [tools](tools)。本轮自己的检查包括manifest与本地文件SHA256、reading-log路径/哈希、报告内部链接、入口计数和采集脚本语法；结果见 [verification.json](analysis/verification.json)。这些检查验证调查产物完整性，不验证第三方科研效果。

当前主skill保留原样。本轮输出是来源库、阅读记录、对照判断和可审阅迁移方案。
