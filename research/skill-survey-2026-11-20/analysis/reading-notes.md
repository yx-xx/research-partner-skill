# 重点源码阅读笔记

调研日期：2026-11-20，Asia/Shanghai。本文基于本目录固定 commit 的源文件，未运行第三方实验循环、模型调用、安装器或评审服务。“可取”指设计值得迁移，不代表其效果已由本轮实测。详细读取范围见 [reading-log.json](reading-log.json)，全部项目见 [catalog.md](catalog.md)。

## 先对齐现有 skill

`research-partner` 已有主动推进、近邻查新、强基线、判别实验、发现/确认分离、运行来源、失败诊断、资源预算、结果回写和接续状态。把别人的相同原则再写一遍，收益不大。本轮优先找三类增量：能执行的判据、可审阅的产物接口、容易被文档掩盖的实现边界。

## 1. EvoSkills：最值得借鉴的是失败诊断，而不是整套门槛

源码：[experiment-craft](../sources/EvoScientist__EvoSkills/skills/experiment-craft/SKILL.md)、[evo-memory](../sources/EvoScientist__EvoSkills/skills/evo-memory/SKILL.md)、[experiment-pipeline](../sources/EvoScientist__EvoSkills/skills/experiment-pipeline/SKILL.md)、[paper-figures](../sources/EvoScientist__EvoSkills/skills/paper-figures/SKILL.md)。前两项和图表入口全文阅读，pipeline 为重点段落阅读。

**最有价值的增量是“桥接成功与失败条件”。** `experiment-craft` 的五步是收集具体失败→找一个能工作的较简单版本→逐步加回复杂性→提出竞争解释与判别检查→只修正被证据支持的问题。现有 skill 已要求最便宜诊断，但可以把“工作版本与失败版本之间，哪项条件首次使它失效”写得更明确。它比笼统的多试几个超参数更能改变下一步行动。日志明确包含下一步动作，也适合现有持续推进方式。

`evo-memory` 分开方向判断和执行策略，并要求记录依据、时间和变更原因。值得保留的是**带条件的经验**：在什么数据、实现、预算下观察到什么，否定的是实现还是假设，何种新证据会重新打开这条路线。不要把方向判为永久无效，也不要让旧失败记录替代新证据。

`experiment-pipeline` 的“复现基线→调好基线→方法→消融”是合理的组织方式，但其 2% 复现偏差、3 次运行/5% 方差、固定尝试配额并非通用科学门槛。现有 skill 已明确没有通用种子数，不能用这些默认值覆盖它；调试同样消耗算力与人工，不应从预算中消失。

**图表文档和检查器要分开判断。** `paper-figures` 先写图意规格，明确字段、单位、尺度、序列、聚合和禁止擅加的元素，这很有用。但 [validate_figure.py](../sources/EvoScientist__EvoSkills/skills/paper-figures/scripts/validate_figure.py) 的 88–179 行主要检查文件、PNG 尺寸、代码中的保存参数和坐标调用、规格字段。它不验证所有数据点是否正确绘出，也不验证图像是否遮挡。入口中偏向只用结构核对的建议不宜照搬；应结合数据语义核对和实际渲染检查，且无需照搬固定 `plot.py/plot.png` 文件名。

## 2. UCL-ERL：与机器人/AI研究最贴合的轻量补件

全文阅读：[experiment-dossier-builder](../sources/UCL-ERL__skills/skills/evaluation/experiment-dossier-builder/SKILL.md)、[paper-code-consistency-auditor](../sources/UCL-ERL__skills/skills/evaluation/paper-code-consistency-auditor/SKILL.md)。参考合同已随文本归档下载，本轮未逐一细读。

**实验 dossier 是远端实验与本地论文之间很清楚的接口。** 它先列实验家族和选取规则，再记录结果值、原始产物、配置/run、指标定义、聚合、不确定性和证据状态，最后给出可写主张、反证和缺失比较。`verified/derived/ambiguous/missing` 区分直接检查、重算和不确定来源，避免仅凭文件名就把一个数写进论文。没有远端文件系统的写作者也应能理解证据。这是对当前状态/交接的具体补充，适合远程 GPU 或机器人实验机，而不必复制整个项目。

**论文—代码审计检查语义漂移。** 它要求核对实际执行路径、配置继承和启动覆盖值，而不是比较符号名称。对机器人任务尤其有用：坐标系、单位、动作空间、观测字段、控制频率、失败处理，一处漂移就可能改变方法含义。每条差异同时指出论文位置、实现证据、科学影响、应修哪一边及未决点。静态匹配不能证明硬件运行一致，这一边界也值得保留。

两项比“再装一个总流程”更适合直接借鉴。无需强制 dossier 文件夹，按真实跨机器交接需求在已有记录中使用字段即可。

## 3. RigorPilot：过程结束、证据有效、任务通过、数值复现分层

全文阅读：[ai-research-reproduction](../sources/lllllllama__RigorPilot-Skills/skills/ai-research-reproduction/SKILL.md)、[paper-context-resolver](../sources/lllllllama__RigorPilot-Skills/skills/paper-context-resolver/SKILL.md)、[minimal-run-and-audit](../sources/lllllllama__RigorPilot-Skills/skills/minimal-run-and-audit/SKILL.md)、[research-thinking-loop](../sources/lllllllama__RigorPilot-Skills/references/research-thinking-loop.md)；重点阅读 [agent-job](../sources/lllllllama__RigorPilot-Skills/skills/ai-research-reproduction/references/agent-job.md) 和 campaign 核心字段。

主入口 20–28、54–59 行把目标选择、实际运行、输出验证分开。先复现 README 中最小可信目标；论文只用于补数据划分、预处理、评测协议等关键缺口。修改依赖或代码时，要报告是否改变科学含义及与原结果的可比性，不能把“跑通”通过换数据/指标制造出来。

`agent-job` 的保证表非常具体：`lifecycle=completed` 可以包含超时等有效失败；还须分别看 `runtime_status/evidence_valid/accepted`。证据保存完整，不能因此说复现成功。`result-match` 必须有实际预期指标和容差，而不是进程退出码。**状态不明时先查同一任务的身份和证据，不另开目录重跑。** 这能减少昂贵实验重复执行和超时被误报成功。

研究循环将 `current_research` 与新候选分开，一次筛选领先只是候选，经过冻结条件下的复测才可晋升为后续比较参照。直觉也是合法来源，但要与论文、代码、历史运行依据区别标注。

不要照搬其固定 3 种子、调试 3 次、两次不改进即停、全训练再次确认等政策；这些与任务预算和已有授权有关。其 campaign 假定数据集/任务/评价和用户给定 SOTA 表已确定，并不自动证明查新完整。主入口和交接合同已经细读，大型 orchestration/runtime 实现未完整审计或实测。

## 4. gevolve：近期出现、对多轮试验偏差考虑较细

全文阅读：[入口](../sources/ed20922__gevolve/skills/gevolve/SKILL.md)及 [garanties-et-limites](../sources/ed20922__gevolve/skills/gevolve/references/garanties-et-limites.md)。大型 `gevolve.py` 已下载，未逐行审计。

可取的是冻结评价器/数据/指标/规则，区分基准选择、候选搜索和封存最终测试；记录假设轨迹和关闭原因；把多次挑选造成的胜出偏差与一次测量噪声都纳入考虑。最终测试不能成为不断调参的反馈源，也不能把验证诊断泄回候选生成。对当前 skill 的新增价值在于：**比较条件的版本与使用历史应进入候选记录，而不只记录一个分数。**

其保证说明主动承认：不是沙箱，模型可能记得公开数据，同用户 shell 可能改写状态，部分信息隔离仍靠指令。因此“封存”可以作为记录和访问边界设计，不能声称消除了所有污染。

不照搬 5 问式启动、Claude `/goal`、强制子代理和最终测试必须再由用户点名的宿主政策。研究已有授权时不应凭空加确认。该项目很新，设计值得观察，成熟效果仍需后续实际评估。

## 5. ray-caster/autoresearch-skill：本轮最具体的独立确认实现

入口主体已读；定点检查 [driver.py](../sources/ray-caster__autoresearch-skill/scripts/driver.py) 的 207–218、567–598、803–857 行。

`confirm()` 明确只用**新的复测**算确认均值，不把因为领先而入选的第一次运行混进去。主循环以确认后的均值更新 best，并对超出可编辑范围的变更、没有变化、重复候选、评价失败、超时等保留不同状态。测量、回退和保留由外部控制器决定，而不是让写方法的模型自报成功；评价器还返回通过标记和细分指标。

这能形成很小的迁移：筛选领先→新运行确认→满足事先判据才晋升；记录搜索次数和预算，保留未确认候选。**固定 `2×样本标准差` 不是普适显著性检验；少量基线运行恰好方差为零也不证明评价确定。** 程序还把部分失败状态归为 `falsified`，不能直接当作科学假设被证伪，应保留代码/测量失败和证据不足。

Windows/PowerShell/`C:\dev`、模型CLI及工作区回退策略带有作者环境假设，不宜整套复制。未执行其 reset、实验和代理调用。本轮确认的是源码确实存在相应分支，不是实测了统计可靠性。

## 6. science-superpowers：先验证可行性及资源限制真的生效

重点读 [establishing-feasibility-first](../sources/K-Dense-AI__science-superpowers/skills/establishing-feasibility-first/SKILL.md)、[preregistering-analysis](../sources/K-Dense-AI__science-superpowers/skills/preregistering-analysis/SKILL.md)，定点读 [prereg.sh](../sources/K-Dense-AI__science-superpowers/skills/preregistering-analysis/prereg.sh)。它是较早的工作流项目，不应包装为11月新 skill。

可行性不是“脚本能启动”。它要求最小真实路径、独立正确性参照、非退化样例、多个实际规模探测和外推范围；失败时先测有依据的明显缓解方式，再判断方向不可行。尤其值得补充的是**软件资源限制要触发验证**：timeout/OOM 等应留下正确终态，而不是只在计划里写一个上限。对机器人现场应使用安全模拟或无风险替代测试，不能为证明限制而试撞硬件边界。

预先写预测、主要分析、停止规则和偏离原因很有价值。但强制用户选择进入/退出可行性阶段、所有工作按完整预注册顺序走，与当前主动研究流不合。探索结果也是有条件的证据，不能笼统说它没有科学信息。

**源码比宣传能保证的更窄。** `prereg.sh` 检查首提交、stamp、冻结版/HEAD/工作树内容、结果路径提交先后和数据 blob 哈希；149–280 行没有逐个比较注册文件的中间历史版本。静态分析可见：当前内容与冻结版一致，不足以证明中途从未改过；提交顺序也不能证明作者在提交前没看过结果，更不是第三方不可篡改的时间戳。可借鉴审计字段和检查顺序，不能复制“通过即证明从未编辑/未看结果”的强保证。此脚本未执行。

## 7. research-direction-check：把“方向是否值得投”做成具体对照

重点阅读 [入口](../sources/lhtrongai__research-direction-check/research-direction-check/SKILL.md)；机器人学习长参考已下载但未深入。

可取的是按 benchmark × 模型家族 × 实测机制及别名做近邻检索，并追到引用和公开投稿池；逐部件比较先前工作到底覆盖了什么。混淆表、结论适用轴、基准数字能否先独立复现，都比抽象新颖性分数实用。阻塞项不止写“证据不足”，还写**什么新证据足以解除它**。向专家交接时也应给具体判断问题。

不要复制其不做合作者、不选主问题、输入缺失就停、固定问答与查找配额等角色限制。当前 skill 的职责正是主动承担这些工作。固定样本量或“有控制就能作因果主张”也不能泛化。

## 8. TheSyBuilder/research-skills：新出现的机制审计

重点阅读 [research-idea-finder](../sources/TheSyBuilder__research-skills/research-idea-finder/SKILL.md) 的原则、瓶颈、机制及 dry run 部分，非全文；作者引述的研究和统计来源未在本轮独立追溯。

它把“问题”写成在哪种条件下失败、为何现有路径无法产生所需能力，避免题目一开始就预设解法。**朴素机制审计**要求先说最直接版本为什么不行：前提在这里不成立、早已有效、或存在有出处的领域误解。之后用数据流、小数值走查、边界输入和朴素对照暴露未定义量、循环依赖、无效组件及失效的负对照。这适合在昂贵实现前排除书面方案的结构错误。

可以把预算和原有判别标准保留为版本化约束，不能为保住方案偷偷降低要求。但结果会改变合理计划，不能把“保护字段绝不调整”理解为永远不能修订；修订需留下依据并区别前后方案。固定论文数/候选数/搜索轮数，以及“只能按几种开篇主张写”的格式不宜搬入。小例子只能检验相应结构，不证明真实任务收益。

## 9. scientific-paper-skill：非常小，但数字账本是直接增量

全文阅读 [scientific-paper/SKILL.md](../sources/javimarlop__scientific-paper-skill/scientific-paper/SKILL.md) 和 [check_dois.py](../sources/javimarlop__scientific-paper-skill/scientific-paper/scripts/check_dois.py)。

`NUMBERS.md` 的价值是让正文数字对应到可重算的源结果，并跨摘要、正文、表、图注和结论核对。提纲还写明各节要表达的主张、证据与读者应得结论。对当前 skill 可以更进一步：让数字来源包含聚合脚本、单位、分母、条件和呈现位置，复用现有结果/证据表，无需再强制一个新文件。

DOI 检查采用 Crossref→DataCite 备用，返回元数据供比对，但不能证明文献支持引用句；DataCite 处理里固定返回的 `retracted=False` 也不是撤稿审计。生态学场景及每阶段等待作者批准的流程不必沿用。它是2026-11-20出现的新样本，简单设计易借鉴，不能把新上线当成效果保证。

## 10. PaperSpine：把结果真正送入下游成稿

主体重点阅读 [入口](../sources/WUBING2023__PaperSpine/dist/claude/skills/paper-spine/SKILL.md)，以及 [scientific-evidence-ledger](../sources/WUBING2023__PaperSpine/dist/claude/skills/paper-spine/references/scientific-evidence-ledger.md) 和 [results-validation](../sources/WUBING2023__PaperSpine/dist/claude/skills/paper-spine/references/results-validation.md) 的相关部分。

可取的不是复杂服务，而是交付一致性：运行生成了真实分析/图表，就要进入正在维护的稿件与结果记录；read标记或哈希不等于知识保留；编译成功不等于页面可读；独立审查要读当前产物且如实说明是否执行。科学准备、编辑完整、技术可编译、投稿条件要分别判断。

`results-validation` 要求每个重要结果段有科学目的、实际证据和解释边界；描述性、负结果和样本可用性都可成为合理结果。对门控方法，它还检查准入、执行、后续评价的时间和条件分母是否混同。这些比“每个结果必须支持新贡献”更准确。

**同一仓库也有新旧协议差异。** `results-validation` 39行起明确后续 C/S/N/M/O/R 表格是 legacy Runner 兼容，不要求当前宿主另建表或等许可。不要把另一篇 ledger 的机器格式全部升级成当前 skill 的强制流程。其服务、Web配置入口、自更新、凭据和运行时体量也不适合作为轻量主skill的默认依赖。

## 11. research-flow：借能力接口，别再造一个总指挥

入口前段、[capability-model](../sources/c3192095975-ship-it__research-flow/references/capability-model.md) 及 [discover_skills.py](../sources/c3192095975-ship-it__research-flow/scripts/discover_skills.py) 的检测逻辑已读，非整套全文。

可借鉴的是按 search/reading/evidence/analysis/figures 等能力槽选补件，区分已安装与可用，同一责任保留一个主要负责者，以产物而非重复对话交接，缺失时有基线降级。

**脚本330–360、388–437行显示能力发现是启发式。** 名称/说明匹配关键词加分；发现缺环境变量判 unavailable，MCP和其他声明依赖判 unverified；没有检测到声明依赖就判 ready。这不是服务连通、包导入或真实运行探测，也没从完整语义中证明能力。应把输出当候选目录，再对当前任务必要依赖作窄检查。

不照搬“所有科研都从我进入”、锁路线、最多3项技能和阶段只能单向进入等统筹限制。现有 `research-partner` 已经是主推进器，宜使用一张轻量任务交接，不再套第二层总流程。

## 12. Kalaris：重点看补件，别把同名大目录全算新增

重点读 [experimental-design](../sources/KalarisLabs__research-agent-skills/skills/experimental-design/SKILL.md)、[fulltext-acquisition](../sources/KalarisLabs__research-agent-skills/skills/fulltext-acquisition/SKILL.md)、[citation-verification](../sources/KalarisLabs__research-agent-skills/skills/citation-verification/SKILL.md)、[reproducibility-statement](../sources/KalarisLabs__research-agent-skills/skills/reproducibility-statement/SKILL.md)、[autoresearch](../sources/KalarisLabs__research-agent-skills/skills/autoresearch/SKILL.md) 的相关段落。引用核验脚本只扫描了函数/状态分支；全文匹配脚本未成功取得，不能声称其实际匹配算法已审计。

全文获取将 included记录、缺失工作单、inbox、文件身份核对和 not-retrieved 分开；文件名暗示、正文证实、冲突、不可读等状态很实用。引用核验同时检查标识/标题/作者/年份，网络失败不能写成假文献。复现声明强调先有实际资源，再写可用性陈述。实验设计可作为伪重复、分块、交互效应等专题的按需补件；不能把随机化一句话等同于所有因果假设自动满足。

同名比较仅限本地同时存在的4对：`paper-lookup` 正文字符序列比约0.94，另三项约0.75–0.80；无一逐字相同。方法和结果见 [same-name-comparison.json](same-name-comparison.json)。这说明明显重叠，不能据此断言来源谱系、谁复制谁或哪个效果更好，也不能把它们计作四项独立创新。

`autoresearch` 要求先启动连续运行机制，含宿主 `/loop`/heartbeat 假设，不宜并入当前主skill。上游仓库最近push与 main 提交日期也不同，见目录；它不是11月新建仓库。

## 13. ARIS：便宜证据预检在前，昂贵判断在后

重点读 [experiment-bridge](../sources/wanshuiyin__Auto-claude-code-research-in-sleep/skills/experiment-bridge/SKILL.md) 前90行、[result-to-claim](../sources/wanshuiyin__Auto-claude-code-research-in-sleep/skills/result-to-claim/SKILL.md) 前100行，以及 [evidence_check.py](../sources/wanshuiyin__Auto-claude-code-research-in-sleep/tools/evidence_check.py) 的数字匹配函数和索引。其他新模块只作目录定位，未全面审计。

研究合同→实验计划/追踪→实施→sanity→结果→主张的接口很明确。可取的增量是先用确定性检查发现来源路径丢失或引用数根本不存在，再投入昂贵的模型评审。真实审查后端的身份、完成情况、作用范围要记录，无法调用就明确 unavailable。

但数字预检通过只说明给定来源里出现某个值或文本。它不会自动核对这个数对应哪一行、哪个条件和分母，也不证明支持结论。警告后跳过的预检不能被报成已通过。默认跨模型、自动部署GPU、固定并发数和具体模型ID不应写死进当前skill；一轮复核也不是客观真理。当前快照在11月19日更新，不能把整仓更新等同于上述每一项都是那天新增。

## 14. ARS：最新版本有细致修补，但不要自动叠加套件

本机安装适配器仍是 **3.22.0**；本轮快照 [README](../sources/Imbad0202__academic-research-skills/README.md) 显示 **3.24.4**，版本说明日期11月19日，所选分支提交11月20日。重点看了版本/定位及 [academic-pipeline](../sources/Imbad0202__academic-research-skills/academic-pipeline/SKILL.md) 的入口和审计条款，未宣称审完全部 agent、脚本或更新差异。

值得借鉴的是审计对象、分母、采样范围、未知状态和判据要显式；低于共识门槛的单审稿人发现不能被静默抹掉，也不能升格成独立共识。更新说明明确区分提示词规则、stub/模拟测试和真实宿主/模型校准，这种诚实报告值得保留。

其“每阶段用户确认”和人类主导选题角色与当前skill的主动推进目标不同。适合按需借返修/引用/评审模块，不建议把整个pipeline叠在主skill外。本轮没有升级本机安装，也没有验证作者提到的新模型或论文的外部效能。

## 15. 写作小工具：借论证衔接，也复核审稿意见

- [Norman的 evidence-driven-writing](../sources/Norman-bury__research-writing-skill/skills/evidence-driven-writing/SKILL.md) 已全文阅读。段落应说明角色、主张、证据、过渡和应避免的内容；压缩不能删除条件与限制。这适合现有写作薄弱段落的局部修复，没必要每次强制生成三类新文件。
- [mil-paper-advisor](../sources/Valdemar-Yu__mil-paper-advisor/SKILL.md) 已全文阅读。可取的是诊断性试验→问题→机制→方法→判别实验的衔接，每个方法组件应接上游障碍和下游证据。但其“不要主动暴露弱点/不利指标”等修辞要求与科学诚实冲突，应明确排除。参考长文尚未细读，不能把实验室风格当通用标准。
- [scientific-writing-review](../sources/shack__scientific-writing-review/skills/scientific-writing-review/SKILL.md) 重点读入口范围与127–153行，全文读 [verifier-brief](../sources/shack__scientific-writing-review/skills/scientific-writing-review/references/verifier-brief.md)。先查意见引用是否真实、是否只是PDF抽取错、修改是否保留always/only/at most等限定，再 keep/amend/drop。**审稿意见本身也应被反证。** 它明确只做写作编辑，不判断科学质量，不能作为科研审查替代。固定每页笔记、并行读者数量和规则集不必照搬；本轮也没有因阅读第三方提示词而启动子代理。

## 16. 阅读、作图和运行的专题候选

- [paper-easy-reader](../sources/YufanDu-bjtu__paper-easy-reader/SKILL.md) 入口全文已读，[check_reader.py](../sources/YufanDu-bjtu__paper-easy-reader/scripts/check_reader.py) 重点读结构解析和main。原文—译文—解释分开，图表公式有来源位置与缺失标记，值得用于深读。但检查器输入只有导出的HTML，核对锚点、句对、对象和内嵌资源等；没有独立原论文清单输入，不能由其通过推断全文/图表无遗漏。renderer已下载未细读。
- [codex-autoresearch](../sources/leo-lilinxiao__codex-autoresearch/SKILL.md) 入口全文已读：控制器负责评价、回退、事件、停止状态；查询状态本身不能启动试验。控制器代码已下载未审计，宿主 Goal/前后台政策要适配。
- [ds-mlops的 dsflow-autoresearch](../sources/scanady__ds-mlops/.agents/skills/dsflow-autoresearch/SKILL.md) 前段重点阅读：内部搜索split与正式validation/test分开，预算要有轮数/时长/检查点。重审批、强制跑满、数据科学全阶段流程不适合直接套入。
- [scientific-figure](../sources/w1-23__scientific-figure/SKILL.md) 只做定位/工作流筛选：可编辑部件、稳定ID、当前版本绑定的视觉判断值得后续专题研究。工程正确、视觉效果和科学审查分开；庞大几何/渲染引擎本轮未审计。

## 17. 其余候选与调查停止点

Claude Scholar、Orchestra、K-Dense scientific-agent-skills 的定位与目录延续前轮调研，本轮取得固定版本后主要用于能力覆盖、分支时效及重叠比较。VincenzoImp、meiyou666、dahliasan、OneSkills、DeepMind science-skills、scientific-writer 等做了仓库定位/入口或目录筛选，没有把“下载了很多入口”说成“逐个读完”。DeepMind的领域模型、OneSkills平台与HPC资源、scientific-writer应用的直接适配价值有限，品牌和数量不足以让它们进入优先迁移名单。

截至本轮已足够覆盖同类总流程、实验循环、复现、记忆、写作、评审、阅读和图表。再扩充大目录的边际收益低于把上面少数机制落到现有skill。具体最小迁移及新增行为评测见 [adoption-map.md](adoption-map.md)。
