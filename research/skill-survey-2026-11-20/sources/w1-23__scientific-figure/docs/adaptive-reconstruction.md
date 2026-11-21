# 自适应 Plan 0.2：使用与能力边界

引擎当前为 0.3.0，Plan 0.2 / Scene 0.1 不变。新增内部证据、像素细带和暗中心线的完整说明及实际失败见 [内部结构恢复](internal-structure.md)。

日期：2026-11-17。此版本实现结构证据、多方法候选、源图比较、分层局部替换与定向修复的最小闭环。科研含义由宿主提供；尚不是通用科学对象识别器。

## 数据与职责

- Scene 继续使用 0.1，保持现有形状、真实文字、组、资源、编辑和导出兼容。
- Plan 新增 0.2；0.1 Plan 原样运行。新操作 `auto_reconstruct` 的输出是一个有稳定 root ID 的可编辑子树。
- `analysis.json` 记录源 SHA-256/尺寸/ROI、坐标变换、背景假设、颜色区域、孔洞/连通域、宿主部件和不确定项。当前自动证据以颜色和可见轮廓为主；开放边界角色、包含/遮挡关系仍标为未知，relations 尚不开放任意输入。
- `candidates.json` 保留实际生成的候选 Scene、审计、失败理由、选择和预算。可提取其中 Scene 通过现有 `draw`/`render` 重新生成。
- `review.json` 将机械结论与视觉/科学核验分开。审计绑定几何、revision、分析和 profile 摘要；其中任一改变都会过期。

## 最小 Plan

先用 `inspect` 获得真实 SHA-256 与尺寸。下面的 `sha256` 是占位符，必须替换，不可直接执行。

```json
{
  "schema_version": "0.2",
  "source": {"sha256": "REPLACE_WITH_REAL_SHA256", "size": [144, 144], "region": [0, 0, 144, 144]},
  "canvas": {"width": 144, "height": 144, "background": "#ffffff"},
  "search_budget": {"max_candidates": 4, "max_renders": 12, "max_seconds": 30},
  "steps": [{
    "step_id": "material",
    "operation": "auto_reconstruct",
    "object": {"id": "material", "kind": "group"},
    "region": [0, 0, 144, 144],
    "parameters": {"colors": 4, "background": "#ffffff"}
  }]
}
```

所有 step 的 region 相对 source.region；分析记录的 region 是原图绝对坐标。当前保持 1 像素=1 场景单位，单个自适应区域不超过 512×512；root ID 不超过 48 字符。

独立编辑需求可通过 parameters.parts 指定，例如 `[{"id":"inner","color":"#2244cc","role":"host_internal","required":true}]`。这是宿主提出的部件与可见色彩证据，不是引擎从颜色推导科研名称。

## 候选与选择

默认尝试三种不同表示：

1. `primitive_fit`：按源前景误差比较轴对齐矩形和椭圆。
2. `flat_contour`：整体自由闭合轮廓及单色填充。
3. `color_layers`：连续主体底色加内部颜色层，保留真实轮廓孔洞，避免相邻色块各自描摹产生裂缝。

`color_layers_fine` 保留为可选的更细颜色分区/保守折线候选。引擎 0.3 默认在有内部证据时加第四种 `region_bands`；`stroke_layers` 为显式或定向修复使用的暗细带/曲线分支候选。这些来自源像素，不把已选候选当作新真值。当前尚无旋转基本形状、任意风格中心线、自动渐变、深分割及纹理重建。

各候选统一 ROI 和合成语义，直接对照源图。路径数量不必一致。分别报告 F（轮廓、源颜色误差）、T（可见连通/孔洞与颜色区域诊断）、E（部件实际可见性编辑效果）、C（绘制节点和段数）。先筛硬约束，再保留 Pareto 候选，在配置允许的颜色误差范围内优先较简洁方案。没有固定全局加权 Q。

默认 profile 是未完成跨域标定的工程起点：`min_iou=0.88`、`max_color_mae=0.10`、`min_region_iou=0.48`、`max_paths=128`、`max_segments=2400`、`appearance_slack=0.012`；0.3 另增 `min_internal_coverage=0.72`。这些不是科学出版标准。Plan 可显式设置 adaptive_profile；保留集不得用于调参。

颜色量化的窄边缘色带保留诊断，但没有可分辨内部区域时不作为独立材料分区硬约束。宿主指定的 required 部件无论是否细小，都另做实际隐藏测试：检查改变的可见区域是否对应源部件颜色，防止只给大组挂部件名称冒充独立编辑。此检查不能证明科学对象完整，也不等于全套编辑器往返验证。

搜索预算跨步骤共享；包含比较渲染与部件隐藏测试，最多按预算执行候选。时间在原子构建/渲染之间检查，不是强制杀进程超时。工程最终 PNG/对照图生成不计入搜索渲染数。复杂素材可能超过预算并返回 needs_input/needs_review；不会嵌入源图凑结果。

## 局部结构编辑

原来的 0.1 `set` 补丁继续可用。0.2 原子补丁支持 `set`、`replace_subtree`、`add_subtree`、`remove_subtree`、`reorder`。

```json
{
  "schema_version": "0.2",
  "base_revision": 0,
  "operations": [{
    "op": "replace_subtree",
    "id": "material",
    "objects": [
      {"id":"material","kind":"group"},
      {"id":"body_new","kind":"ellipse","parent":"material","geometry":{"cx":60,"cy":60,"rx":40,"ry":30},"style":{"fill":"#229966"}}
    ],
    "id_map": {"old_child":"body_new"}
  }]
}
```

替换 root 保留原 parent/transform/style（除非明确给出允许的属性），记录新旧 ID。连接线若引用将删除的子对象，必须给 id_map，否则整个事务拒绝。添加或删除后的悬空引用、循环及非法几何同样导致回滚。一个补丁只递增一次 revision；失败不修改原 Scene。完整自动科学拆合、重挂父级、全图重新识别后的身份匹配尚未实现。

## 定向修复

新增命令：

```bash
conda run -n ScientificFigure_skill figure-cli repair outputs/adaptive-v02-delivery/repair-before --source outputs/adaptive-v02-delivery/repair-reference.png --object material --request outputs/adaptive-v02-delivery/repair-request.json --output work/repaired
```

request.action 支持 `restore_internal_regions`、`restore_internal_boundaries`、`restore_topology`、`reduce_fragmentation`，以及按目标实际失败原因选路的 `auto`，可给 parts、max_rounds（1–3）及共享 budget。修复要求对象已有源绑定的自适应步骤；auto 没有发现可处理的已验证失败时停止，不凭空改图。

执行顺序是目标失败检查→适用候选→目标改善检查→revision 子树替换→整图复评→提交。恢复内部结构必须改善缺失部件/区域或源颜色损失；恢复拓扑必须修复相应可见拓扑；减少碎片必须实际减少节点或段数。无改善、引用不能迁移、重复状态或上下文不合格时保留原工程，不增加 revision，repair_status=needs_review。不能把一次成功命令等同修复通过。

## 复现与交付

```bash
conda run -n ScientificFigure_skill python -I scripts/benchmark_adaptive.py --output-root work/adaptive-demo
```

此脚本使用打包的两个 CC BY 4.0 开发输入，生成源栅格、0.1 基线、不同候选、最终工程、一次受控遗漏修复、内部图层改色及独立导出。算法只接收栅格；参考 SVG 路径没有导入重建 Scene。加入 `--include-user-reference` 可跑本机已有截图局部；源码包不分发该截图。

当前开发素材和 provenance 见 `benchmarks/manifest.json`。两组公开来源不是 48 张保留测试集；专家视觉和科学核验仍未执行。实际结果、退化与未完成项见 `docs/adaptive-validation.md`。
