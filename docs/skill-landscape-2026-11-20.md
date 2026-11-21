**research-partner 的相近与互补 skill 调研**

> 后续已扩展到30个项目并保存固定源码快照，详见 [扩展调研与源码库](../research/skill-survey-2026-11-20/README.md)。重点阅读、时效纠偏和与当前skill的对照以该目录为准。

调研日期：2026-11-20（Asia/Shanghai）。对象为本仓库 `research-partner/SKILL.md`、阶段 references、当前环境已安装的相关 skill，以及公开项目的 README、具体 SKILL.md、部分契约文件和脚本源码。

**结论：最值得作为整体参照的是 ARIS 和 UCL-ERL/skills；最值得直接补强的是实验档案、论文—代码一致性、严格结果分析和可执行统计工具。** ARS 已经安装，适合按阶段复用；Claude Scholar、Orchestra 和 K-Dense 更适合提供专门模块。建议保留 research-partner 的统筹职责，通过按需加载明确的输入输出接入专门能力。

这里的“推荐”是基于源码与文档的适配判断，以及配套资产是否确实存在的检查，不代表已经在相同课题、相同模型和预算下完成端到端效果对照。GitHub 网页可能滞后于分支内容；已下载文件的字节散列、Git blob SHA 和读取分支记录在相邻的 `skill-landscape-sources-2026-11-20.json` 中。

**先明确当前 skill 的优势和要补的部分。**

当前定位是机器人控制、具身智能及交叉领域的主动研究合作伙伴，涵盖方向取舍、方法探索、真实实验、证据回写、成稿与返修。已有主张—证据表、贡献预判、低成本判别实验、负结果处理、资源边界和收敛原则。因此，“再增加一套科研原则”带来的收益有限；更有价值的是让这些原则落到具体研究资产和可检查的实现上。

| 当前环节 | 已有能力 | 值得补强的资产 |
| --- | --- | --- |
| 选题与查新 | 贡献预判、最近工作对照、反向查新 | 技术机制层面的查重记录、机器人基线与评测场景检查 |
| 方法与实验 | 判别预测、实验矩阵、复现记录 | 远程实验档案、配置与结果索引、运行来源 |
| 结果到论文 | 证据驱动叙事、结果回写 | 表格到原始日志的追踪、独立比较单位检查 |
| 成稿与提交 | 主稿和附件、审稿与返修 | 论文—代码逐项对照、具体会议模板与检查清单 |
| 持续推进 | 状态入口、关键依赖、停止与收敛 | 可复用的小型产物契约，减少跨工具和跨机器的信息损失 |

**定位相近、值得借鉴的项目。**

| 项目 | 与本 skill 的关系 | 最值得看的部分 | 采用判断 |
| --- | --- | --- | --- |
| [ARIS / Auto-claude-code-research-in-sleep](https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep) | 很高：自主研究，从选题、实验、审查到论文 | `idea-discovery-robot`、`research-refine`、`result-to-claim` | 作为主动研究闭环的重点参照，选择性吸收 |
| [UCL-ERL/skills](https://github.com/UCL-ERL/skills) | 很高：明确面向 Robotics & AI | `rai-research-flow`、`experiment-dossier-builder`、`paper-code-consistency-auditor` | 最贴近领域与实际研究资产，优先借鉴 |
| [Academic Research Skills / ARS](https://github.com/Imbad0202/academic-research-skills) | 很高：调研、实验、写作、审查、返修完整套件 | 按阶段加载的工作流、引用与返修核验、实验规划 | 当前环境已有 Codex 适配版，优先复用现有安装 |
| [Claude Scholar](https://github.com/Galaxy-Dawn/claude-scholar/tree/codex) | 高：研究生命周期工作流和知识管理 | `results-analysis`、`citation-verification`、研究与写作分工 | 使用其 Codex 分支，按模块接入 |
| [Orchestra AI Research Skills](https://github.com/Orchestra-Research/AI-Research-SKILLs) | 中高：AI/ML 研究技术库，兼有创意与写作 | `ml-paper-writing`、研究创意模块、机器人策略实现指南 | 适合作为专门能力库 |
| [K-Dense Scientific Agent Skills](https://github.com/K-Dense-AI/scientific-agent-skills) | 中：跨学科工具库，提供实验与分析模块 | `paper-lookup`、`experimental-design`、`statistical-analysis`、`scientific-visualization` | 适合补足有脚本和明确产物的技术环节 |

ARIS 的机器人选题流程明确检查 MDP/POMDP 定义、观测与动作空间、控制和 RL 基线、仿真及真实实验差距；`research-refine` 则将审查、补实验与再审查连接起来。这些都贴近 research-partner 的定位。需要保留自己的取舍：其部分流程指定模型、评分阈值，并偏好某些现代技术路线，不能把这些约定直接当作研究成立或值得投稿的科学判据。[机器人选题源码](https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep/blob/main/skills/idea-discovery-robot/SKILL.md)、[研究改进源码](https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep/blob/main/skills/research-refine/SKILL.md)。

UCL 最值得学的是研究资产之间的衔接。`experiment-dossier-builder` 把方法状态、实验设计、结果账本、失败、来源和待写论文主张放进便携档案；`paper-code-consistency-auditor` 检查稿件与实现、配置、数据处理和评测代码的差异。已检查的这两个目录各有 SKILL.md 和配套 contract，主要提供流程与产物规范，并非现成的自动审计程序。[实验档案](https://github.com/UCL-ERL/skills/blob/main/skills/evaluation/experiment-dossier-builder/SKILL.md)、[论文—代码审计](https://github.com/UCL-ERL/skills/blob/main/skills/evaluation/paper-code-consistency-auditor/SKILL.md)。

ARS 在当前环境的适配版为 3.22.0，本地 manifest 记录了上游来源与固定提交。它与当前 skill 的覆盖范围高度重叠，适合在确实需要细致文献流程、写作、审稿或返修核验时加载对应模块；将两个完整统筹流程同时铺开，会增加重复状态和管理成本。这个判断基于当前本地安装，不能据此断言所有上游功能都已完成 Codex 实跑验证。

Claude Scholar 值得重点看 Codex 分支中的 `results-analysis`。它要求先验证配置、日志和比较单位，分别处理独立 seed、配对任务、重复测量、单次运行及样本不足，再生成分析报告、统计附录、图目录与实际图。它还将统计分析与 Results 正文写作分开，适合补强“真实结果到论文叙事”的接口。接入时可复用这种证据边界，产物数量仍服从当前任务。[结果分析源码](https://github.com/Galaxy-Dawn/claude-scholar/blob/codex/skills/results-analysis/SKILL.md)。

**具体值得用的模块，按对本仓库的增益排序。**

| 优先级 | Skill 与来源 | 能补上什么 | 建议使用方式 |
| --- | --- | --- | --- |
| P0 | UCL `experiment-dossier-builder` | 将服务器上的配置、日志、结果、图表、失败和缺失项带回研究主线 | 实验形成重要阶段结果或切换机器时使用，复用已有状态入口 |
| P0 | UCL `paper-code-consistency-auditor` | 找出稿件写法与实际实现、默认参数、数据处理和评测之间的差异 | 核心结果进入主稿后，以及重要实现修改后使用 |
| P0 | Claude Scholar `results-analysis` | 明确独立比较单位、可用统计与支持范围，形成真实分析产物 | 产生可比较实验数据后使用，交给写作环节的内容是结果与限制 |
| P0 | K-Dense `statistical-analysis` | 估计目标、统计假设、效应量、置信区间、敏感性分析 | 遇到具体统计问题时使用；不能仅按样本量机械选检验 |
| P1 | K-Dense `experimental-design` | 随机化、分块、配对、因子设计，以及生成设计的脚本 | 实验开始前使用，具体因子映射到任务、环境、seed、算法和预算 |
| P1 | ARIS `result-to-claim` | 把实验产物转成有来源、有边界的主张，检查文字与数值是否有依据 | 有结果但论点尚未收敛时使用，接入已有主张—证据表 |
| P1 | Orchestra `ml-paper-writing` | 从研究仓库组织论文、写作指南、引用流程、会议模板和检查单 | 核心证据可写后加载；目标场所当年的模板另行核验 |
| P1 | K-Dense `scientific-visualization` | 真实数据绘图、误差和缺失值表达、无障碍、导出与来源记录 | 生成论文图时加载，图的设计围绕论点和数据结构 |
| P1 | UCL `evidence-matrix-builder` | 将论文卡片整理成可追踪的比较矩阵和空缺图 | 相近论文较多、需要比较适用条件和证据时使用 |
| P2 | Orchestra `creative-thinking-for-research` | 为尚未形成机制的问题增加不同的构造视角 | 明确遇到方法构造瓶颈时使用，随后仍要做查新和判别实验 |
| 已有 | K-Dense `paper-lookup` | 18 个学术 API 的检索、元数据、全文入口与来源记录 | 当前已安装，且 research-partner 已明确接入，优先用好 |
| 已有 | Orchestra `brainstorming-research-ideas` | 结构化生成和比较研究方向 | 当前已安装，适合作为按需的创意辅助 |

其中，`statistical-analysis` 不只是统计术语清单：目录中确有 `scripts/assumption_checks.py`；`experimental-design` 有 `scripts/randomization.py` 和 `scripts/doe_designs.py`；`scientific-visualization` 的 `scripts/image_metadata.py` 也已取回检查。这里核验的是工具与源码存在，没有据此宣称它们已在本项目数据上运行通过。[统计分析](https://github.com/K-Dense-AI/scientific-agent-skills/blob/main/skills/statistical-analysis/SKILL.md)、[实验设计](https://github.com/K-Dense-AI/scientific-agent-skills/blob/main/skills/experimental-design/SKILL.md)、[科学绘图](https://github.com/K-Dense-AI/scientific-agent-skills/blob/main/skills/scientific-visualization/SKILL.md)。

ARIS 的 `result-to-claim` 有可检查的 `tools/evidence_check.py`，先核验引用文件与数值是否存在，再交给语义审查。其源码明确区分“证据存在”和“证据支持主张”。这条边界很适合保留：文件存在、引用存在和数字匹配都不能独自证明科学结论成立。[主张审计](https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep/blob/main/skills/result-to-claim/SKILL.md)、[证据预检查脚本](https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep/blob/main/tools/evidence_check.py)。

**机器人和具身智能项目可以再按具体路线选择实现 skill。**

Orchestra 的 `18-multimodal/` 中已核查到以下条目，适用于课题已经选定相应平台的情况；它们不应反过来决定选题。

| 源码目录 | SKILL.md 中的实际 name | 对应任务 |
| --- | --- | --- |
| `openpi/` | `fine-tuning-serving-openpi` | OpenPI 模型的数据适配、微调、归一化统计、推理服务 |
| `openvla-oft/` | `fine-tuning-openvla-oft` | OpenVLA-OFT 的动作头、LoRA 微调、LIBERO/ALOHA 评测 |
| `cosmos-policy/` | `evaluating-cosmos-policy` | Cosmos Policy 的 LIBERO/RoboCasa 评测、无头渲染与推理剖析 |

这些条目有具体工程步骤，也依赖相应平台、版本、数据和算力。它们是路线确定后的实施指南；执行时需对照对应官方实现的当前版本。[OpenPI](https://github.com/Orchestra-Research/AI-Research-SKILLs/blob/main/18-multimodal/openpi/SKILL.md)、[OpenVLA-OFT](https://github.com/Orchestra-Research/AI-Research-SKILLs/blob/main/18-multimodal/openvla-oft/SKILL.md)、[Cosmos Policy](https://github.com/Orchestra-Research/AI-Research-SKILLs/blob/main/18-multimodal/cosmos-policy/SKILL.md)。

**当前已安装模块的复用边界。**

- `academic-research-suite`：保留现有适配版；选择当前阶段的工作流，避免重复维护整套项目状态。
- `paper-lookup`：继续承担实际检索；元数据可追溯和正文支持主张仍是两件事。
- `brainstorming-research-ideas`：用于需要拓展候选时，最终取舍仍由 research-partner 按证据与资源组织。
- `hypothesis-generation`：本地安装含假设记录、操作化、预测—竞争解释矩阵、因果措辞和证据表检查脚本，值得借用。但其 SKILL.md 明文禁止自动对科学假设评分、排序、选择、接受或拒绝；这与本 skill 主动比较、推荐和推进候选路线的职责存在潜在冲突。不能将整个流程默认加载后又假定两者完全兼容，应先限定模块用途和行为边界。

本地核查入口：`/home/pc108/.codex/skills/academic-research-suite/SKILL.md`、对应 `manifest.json`，以及 `/home/pc108/.codex/skills/{paper-lookup,brainstorming-research-ideas,hypothesis-generation}/SKILL.md`。

**另查到但不列为首批接入的候选。**

[TheSyBuilder/research-skills](https://github.com/TheSyBuilder/research-skills) 的 `research-idea-finder` 强调机制层面查重、可证伪预测、小型执行检查和明确的停止结果，适合补强“泛泛调研之后仍不知道创新在哪里”的阶段；它主要解决选题，不覆盖完整研究交付。[对应源码](https://github.com/TheSyBuilder/research-skills/blob/main/research-idea-finder/SKILL.md)。

[VincenzoImp/academic-research-skills](https://github.com/VincenzoImp/academic-research-skills) 将文献阅读、贡献实现、打包与投稿分成技能；检查到的 `develop-contribution` 依赖自身贡献目录与报告规范，对已有目录体系的项目需要适配，首批收益低于上面的实验档案和一致性审计。[对应源码](https://github.com/VincenzoImp/academic-research-skills/blob/main/skills/develop-contribution/SKILL.md)。

[Orchestra 的 autoresearch 模块](https://github.com/Orchestra-Research/AI-Research-SKILLs/blob/main/0-autoresearch-skill/SKILL.md) 适合有固定评价脚本和明确预算的局部实验循环。对本 skill，它更适合作为某项方法探索的执行模式；完整研究贡献还需要问题价值、查新、外部有效性和稿件证据的判断。

同一库中的 `research-manager` 名称较宽泛，源码定位主要是把当前对话结构化为研究记录；`rigor-reviewer` 面向该结构化研究表示的审计。它们有用，但不能仅凭名字把它们视作可直接替代研究统筹的完整代理。[research-manager](https://github.com/Orchestra-Research/AI-Research-SKILLs/blob/main/22-agent-native-research-artifact/research-manager/SKILL.md)、[rigor-reviewer](https://github.com/Orchestra-Research/AI-Research-SKILLs/blob/main/22-agent-native-research-artifact/rigor-reviewer/SKILL.md)。

**建议对本 skill 的下一轮增强只集中在三个接口。**

1. **实验产物到研究状态。** 借鉴 UCL 的 dossier contract，给出实验配置、代码版本、数据、结果索引、失败与待验证项的简洁约定，复用当前唯一状态入口。
2. **研究状态到可信主张。** 借鉴 Claude Scholar 的比较单位检查，以及 ARIS 的结果到主张映射；已有主张—证据表增加直接来源、适用条件和仍未排除的解释。
3. **可信主张到一致稿件。** 增加 UCL 的论文—代码对照步骤，按需调用统计分析、绘图和论文写作专门模块。

调用专门模块时，应传递当前要解决的问题、真实输入位置、产物和完成条件，再将结果合并回已有项目文件。这样可以增强实际执行能力，也能保留当前 skill 主动推进、按证据修正和及时收敛的核心定位。
