# Research Flow 用户指南

## 1. 它解决什么问题

科研任务经常会同时命中多个 skill：文献检索、论文写作、数据分析、科研绘图、统计审查、审稿回复。直接让这些 skill 自由触发会导致：

- 同一个检索被重复执行；
- 多套写作或绘图风格同时修改同一份文件；
- `paper-spine` 和 `academic-research-suite` 争夺总流程；
- 写作 skill 自己审自己；
- 没有证据的结果被提前写成论文；
- 不同用户安装的 skill 名称不同，固定流程无法复用。

Research Flow 是科研任务的编排层。它先发现当前用户安装了哪些 skill，再把科研流程映射到可用能力，并强制同一阶段只有一个主技能。

## 2. 安装

### Codex

把仓库目录复制到：

```text
~/.codex/skills/research-flow/
```

目录结构应保持：

```text
research-flow/
├── SKILL.md
├── agents/openai.yaml
├── references/
├── scripts/
└── examples/
```

安装后，新开一个科研对话，或在当前会话中重新加载 skill。

### 其他兼容环境

只要环境支持读取 `SKILL.md` 和相对资源文件，就可以复制整个目录。若 skill 目录不同，可通过环境变量或发现脚本指定：

```bash
python3 scripts/discover_skills.py --root "/path/to/skills"
```

## 3. 自动触发

真实科研任务会优先进入 Research Flow，例如：

- 选题、研究设计、假设；
- 文献检索或管理；
- 论文精读；
- 科研数据分析；
- 统计审查；
- 科研图表；
- 论文、综述、开题、报告写作；
- 自审、同行评审、审稿回复；
- 投稿包和科研汇报。

一般概念问答、普通编程、普通业务数据分析和非科研写作不会触发。

## 4. 第一次运行

第一次科研任务会做四件事：

1. 读取宿主提供的 skill 清单；
2. 必要时运行 `scripts/discover_skills.py`；
3. 检查非标准格式、依赖和用户 override；
4. 建立能力图，锁定路线和入口阶段。

开始时会显示：

```text
ResearchFlow：路线=…；阶段=…；主技能=…；辅助技能=…；能力源=…；可用性=…
```

## 5. 能力和路线

核心能力槽：

```text
scope
search
acquisition
reading
evidence
analysis
statistics
figures
writing
production
review
response
delivery
orchestration
memory
```

主要路线：

- `general`：通用英文论文和报告；
- `chinese_thesis`：中文论文、毕业论文、课程研究；
- `nature`：明确目标为 Nature/CNS 系列；
- `systematic_review`：系统综述、元分析、ARS 流程；
- `competition`：数学建模等竞赛。

路线只定义偏好，不要求某个固定 skill 必须存在。

## 6. 阶段入口

完整阶段：

```text
0 立项 -> 1 定向 -> 2 检索 -> 3 精读 -> 4 证据
-> 5 分析 -> 6 统计 -> 7 图表 -> 8 写作
-> 9 生产 -> 10 评审 -> 11 回复 -> 12 交付
```

可以从中间进入：

- 单篇论文精读：2 -> 3 -> 4；
- 只做数据分析：5，必要时 6；
- 已有数据只做图：5 -> 6（如需要）-> 7；
- 已有证据只写论文：4 -> 8；
- 已有完整稿件：9；
- 只审稿：10；
- 只回复审稿：11；
- 只做科研汇报：12。

进入后置阶段前必须检查前置工件。

## 7. 用户 override

如果自动推断不准确，可以创建：

```text
~/.codex/research-flow-overrides.yaml
```

示例：

```yaml
roles:
  search: my-literature-tool
  reading: my-paper-reader
  analysis: my-analysis-tool
  figures: my-plot-tool
  writing: my-writing-tool
```

也支持项目级 override：

```text
./.research-flow/overrides.yaml
./.research-flow-overrides.yaml
```

override 只决定能力槽，不修改任何 skill 源文件。指定的 skill 不存在或不可用时，流程会标记 `unavailable`。

## 8. 依赖和可用性

发现脚本会读取声明中的 MCP/API/浏览器/环境变量依赖，并标记：

- `ready`：未发现依赖问题；
- `likely`：依赖看起来存在，但没有真实调用；
- `unverified`：声明了外部依赖，发现阶段未验证；
- `unavailable`：必要环境变量、命令或文件缺失。

它不会读取或输出环境变量的值。

## 9. 非标准 skill

除了标准 `SKILL.md`，脚本也支持：

- `manifest.yaml` fallback；
- `agents/openai.yaml` metadata fallback。

非标准格式只用于能力识别，不会被当作已完整验证的执行环境。

## 10. 没有科研 skill 时

使用内置 baseline：

```text
references/baseline-protocol.md
```

baseline 提供：

- 研究 brief；
- 可复现检索日志；
- 来源定位表；
- claim-evidence 矩阵；
- 数据分析清单；
- 统计审查；
- 图表 source data 和 QA；
- 通用论文结构；
- 结构化评审和回复跟踪。

## 11. 故障排查

### 没有自动触发

- 确认目录是 `~/.codex/skills/research-flow`；
- 新开一个对话；
- 确认任务属于真实科研项目。

### 判断能力错误

- 查看 discover 输出中的 `capabilities`；
- 添加 override；
- 检查 skill 描述是否足够具体；
- 检查脚本文件名和参考文档标题是否能表达能力。

### 依赖显示 unavailable

- 检查缺失的环境变量；
- 检查 MCP/API 配置；
- 不要在没有权限时假装外部服务可用。

### 同名 skill

默认优先级：

```text
项目级 > CODEX_HOME > ~/.codex > ~/.agents > 系统/插件
```

## 12. 卸载

删除对应 skill 目录即可。Research Flow 不会修改其他 skill，也不会在用户目录留下必要运行数据。

## 13. 安全边界

- 只读取 skill 元数据；
- 不执行其他 skill 的脚本；
- 不自动修改 skill；
- 不把清单或项目材料发送给外部服务；
- 外部依赖必须明确标记可用性。
