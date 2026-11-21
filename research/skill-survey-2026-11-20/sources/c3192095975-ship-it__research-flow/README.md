# Research Flow

[![Version](https://img.shields.io/badge/version-3.1.0-blue.svg)](VERSION)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Research Flow 是一个跨用户可移植的科研总编排 skill。它不会假定用户安装了某一套固定 skill，而是先发现当前环境中的 skill，再把科研流程映射到可用的“能力槽”。

## 功能

- 自动发现本机安装的 Codex-compatible skills。
- 按能力而不是固定名称选择检索、精读、分析、统计、图表、写作、评审和交付工具。
- 同一阶段只允许一个主 skill，避免多个 skill 互相抢夺任务。
- 支持用户级和项目级 override。
- 检查非标准 skill 格式和外部依赖声明。
- 没有可用科研 skill 时，自动使用内置 baseline 流程。
- 通过阶段质量门和工件交接保持可追溯性。
- 不执行其他 skill 的脚本，也不自动修改其他 skill。

## 文档

- [用户指南](docs/user-guide.md)
- [架构说明](docs/architecture.md)
- [贡献指南](CONTRIBUTING.md)
- [更新记录](CHANGELOG.md)

## 目录结构

```text
research-flow/
├── SKILL.md
├── README.md
├── VERSION
├── CHANGELOG.md
├── LICENSE
├── CONTRIBUTING.md
├── docs/
│   ├── user-guide.md
│   └── architecture.md
├── agents/
│   └── openai.yaml
├── references/
│   ├── capability-model.md
│   ├── adaptation-protocol.md
│   ├── activation-order.md
│   ├── handoff-schemas.md
│   └── baseline-protocol.md
├── scripts/
│   └── discover_skills.py
├── examples/
│   └── research-flow-overrides.yaml
└── tests/
    └── test_discover_skills.py
```

## 安装

从 GitHub 克隆：

```bash
git clone https://github.com/c3192095975-ship-it/research-flow.git
mkdir -p ~/.codex/skills
cp -R research-flow ~/.codex/skills/research-flow
```

也可以把本目录直接放到 Codex 的用户 skill 目录：

```text
~/.codex/skills/research-flow/
```

也可以使用自定义 skill root，并在启动时通过 `RESEARCH_FLOW_SKILL_ROOTS` 或 `--root` 指定。

## 使用

安装后，涉及真实科研项目的请求应先触发 `research-flow`。流程会输出版本化的路线、阶段、主技能和辅助技能状态。

首次任务可以手动运行能力发现：

```bash
python3 scripts/discover_skills.py
```

扫描额外的 skill 目录：

```bash
python3 scripts/discover_skills.py --root "/path/to/skills" --include-plugins
```

## 用户 override

自动能力推断不准确时，可以创建：

```yaml
# ~/.codex/research-flow-overrides.yaml
roles:
  search: my-literature-tool
  reading: my-paper-reader
  analysis: my-analysis-tool
  figures: my-plot-tool
  writing: my-writing-tool
```

支持位置：

```text
./.research-flow/overrides.yaml
./.research-flow-overrides.yaml
~/.codex/research-flow-overrides.yaml
~/.config/research-flow/overrides.yaml
```

也可以通过 `RESEARCH_FLOW_OVERRIDES` 或 `--overrides` 指定。

## 能力发现

`scripts/discover_skills.py` 会读取：

- `SKILL.md` 的 frontmatter；
- `manifest.yaml` 和 `agents/openai.yaml` fallback；
- 目录名、脚本文件名、参考文档标题和 README 摘要；
- 调用策略和外部依赖声明；
- 环境变量是否存在，但不会读取或输出变量值。

输出为 JSON，可用于能力图、缓存和调试。

## 运行测试

```bash
python3 -m unittest discover -s tests -v
```

## 安全边界

- 只读取 skill 元数据，不执行其他 skill。
- 不把本机 skill 清单或科研材料发送到外部服务。
- 不使用 skill 自我修改。
- 依赖 MCP、API、浏览器或凭据的能力会标记为 `unverified` 或 `unavailable`。
- 没有可用科研 skill 时使用 baseline，不编造结果。

## License

MIT。见 [LICENSE](LICENSE)。

## 版本

当前版本：`3.1.0`。
