# Research Flow 架构说明

## 1. 设计目标

Research Flow 不是单一科研写作 prompt，而是跨用户、跨 skill 安装环境的编排层。目标是把科研流程从“依赖固定品牌 skill 名称”改为“依赖能力槽”。

## 2. 分层

```text
宿主/用户指令
    ↓
Research Flow 总编排
    ↓
能力发现与能力图
    ↓
路线锁
    ↓
阶段锁
    ↓
唯一主技能 + 可选辅助技能
    ↓
工件和质量门
    ↓
下一阶段
```

## 3. 能力槽

能力槽是稳定接口。skill 是实现。两者分离后，同一台机器可以使用 `nature-*`，另一台机器可以使用独立安装的检索、绘图和写作工具。

```yaml
search:
  selected: any-installed-search-skill
  alternatives: []
  availability: ready
  confidence: high
```

## 4. 发现算法

1. 读取宿主 skill 清单；
2. 扫描项目级和用户级 skill 根目录；
3. 读取 `SKILL.md` frontmatter；
4. fallback 到 `manifest.yaml` 或 `agents/openai.yaml`；
5. 收集目录名、脚本文件名、参考标题、README 摘要；
6. 计算能力候选；
7. 检查调用策略、外部依赖和环境变量；
8. 合并用户 override；
9. 去重和选择优先级；
10. 输出能力图。

## 5. 冲突控制

- 一个阶段一个主技能；
- 一个能力槽一个 selected owner；
- 同一轮最多 3 个 skill；
- 不允许两个总编排 skill 同时控制项目；
- 不允许两套写作或图表体系同时主控；
- 质量门失败不能通过换 skill 绕过。

## 6. 质量门

三个硬门：

1. 方向锁；
2. 证据/结果锁；
3. 提交锁。

其余阶段优先使用自动检查：引用核验、数据清单、统计审查、图表 QA、文档构建和投稿包一致性。

## 7. 降级

- 主能力不可用时，同能力槽寻找替代；
- 没有替代时使用 `references/baseline-protocol.md`；
- 记录 `degraded_roles`；
- 不把已安装伪装成已就绪。

## 8. 扩展方式

新增能力时：

1. 在 `references/capability-model.md` 定义槽；
2. 在 `scripts/discover_skills.py` 增加关键词或结构信号；
3. 在 `references/activation-order.md` 加入阶段依赖；
4. 在 `references/handoff-schemas.md` 加入状态字段；
5. 运行单元测试。

禁止通过硬编码单个人或单台机器的 skill 目录来扩展。
