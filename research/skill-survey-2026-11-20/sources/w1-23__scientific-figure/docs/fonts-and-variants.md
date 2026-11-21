# 任务字体预检与双 SVG 交付

两项入口都只增加文件接口，不改 Scene 权威、工程事务或既有 CLI 行为。

## 字体预检

```bash
figure-cli font-probe texts.json --output work/fonts
```

请求（严格字段）：

```json
{"schema_version": "0.1",
 "texts": ["Cell membrane", "H₂O → O₂", "细胞膜"],
 "candidates": ["C:/Windows/Fonts/arial.ttf"],
 "font_size": 14}
```

`texts` 必填，1..200 条、每条 1..20000 字符；全部字符去重后上限 4096。`candidates`、`font_size` 可选；`--font PATH` 可重复追加候选，`--font-size` 覆盖请求值。未知字段直接拒绝。

报告 `font-probe.json` 记录：

- `texts`：`count` 条文字、`unique_characters` 去重字符数（4096 预算按它计算）、`total_characters` 实际总字符数和请求摘要；
- `active_font`：当前渲染实际使用的字体（`font_info`），以及它缺失的字符；
- `selected`：覆盖全部字符的字体；若它不是当前字体，`activation` 明确写出需要由用户设置 `SCIENTIFIC_FIGURE_FONT`，工具不会自动改环境；
- `candidates`：每个 TTF/OTF/TTC 的 SHA256、字节数、逐 face 的家族名、字形数、缺失字符与 `covers_all`；TTC 只有 face 0 可通过环境变量选择；
- `single_font_rendering: true`、`mixed_font_layout: "unsupported"`：不谎称混排回退；
- `status`：`ok` 或 `needs_input`。

`--output` 同时写 `font-probe-sample.png`，用被选字体实际绘制英文、数字、希腊字母、上下标、中文和请求中的文本行。若被选字体不含某条固定样例的字符（例如西文字体没有中文），该行不画，避免乱码方块被误读为预检失败；`sample` 里的 `texts`/`text_lines_drawn` 说明请求文本及实际画出的行数（超长时截断，PNG 本身不提示）。覆盖只证明字形存在，不证明字形形状或度量适合该图。

## 字体预设（只做建议与预检）

```bash
figure-cli font-probe texts.json --profile --output work/fonts
```

`--profile` 默认加载包内 `data/font_profile.json`（名称 `scientific-default`）：

| role | 建议家族 |
|---|---|
| `text.latin` | Times New Roman |
| `text.cjk` | Microsoft YaHei |
| `math.family` | Cambria Math |

`fallback` 固定为 `single_font_only`。`resolve_profile()` 扫描本机字体（TTC 按真实 face 数枚举，能识别 `cambria.ttc` 里的 Cambria Math），报告每个 role 的：

- `available`；
- `matches`：文件路径、face 序号、家族名、SHA-256；
- `sample_missing`：示例字符（`细胞膜线粒体αβγΔ∑∞→`）在该 face 中缺失的字符。

找不到的家族进入 `missing` 列表，**不**用其他字体顶替。报告写明 `rendering: "single_font_only"` 与 `mixed_font_layout: "unsupported"`。

这个预设**只影响报告**：`to_svg`、`render_svg`、`text_bounds` 仍使用 `SCIENTIFIC_FIGURE_FONT` 指向的单一字体。不随包分发任何微软字体；字体授权由使用者自行确认。

## 双 SVG 导出

```bash
figure-cli export-variants work/figure --output deliverables/figure
figure-cli export-variants work/figure --output deliverables/figure --exclude glyph-1,glyph-2
```

读取一个完整工程（`load_project` 校验回执与内容），从同一 Scene 生成：

| 文件 | 内容 |
|---|---|
| `figure.final.svg` | 全部对象，带文字 |
| `figure.graphics.svg` | 去掉文字对象及其标注装饰 |
| `variants.json` | 修订号、被排除对象、被清理空组、两份 SVG 的 SHA256/字节数 |

文字识别规则：`kind == "text"`，或对象 `semantic.layer == "text"`（用于路径描出的文字），或 `semantic.text_decoration == true`（文字底板等装饰），或带 `semantic.label_for`。指向被排除文字的 connector 同步排除；若某个 occlusion 引用被排除对象，导出拒绝而不是猜测。`--exclude` 用于未标记的路径文字。

共有对象在两份 SVG 中保持同一 ID、几何与样式，不重新绘制。`figure.final.svg` 与工程自身的 `figure.svg` 字节一致（同一宿主、同一换行规则），可用于哈希核对；`variants.json` 记录的就是写入文件的 SHA256。未被引用的渐变/clip/mask 可能留在 `defs`，它们是惰性的。导出写入新目录，已存在的目标文件不会被覆盖；工程本身和回执不变。PNG 仍是可选格式。

## 实测：柑橘示例

在 501 个对象的 `examples/citrus-quality` 图上实测（45 个 text 对象、39 条不重复文字、632 个字符、47 个去重字符）：

- `font-probe` 在 64 个本地候选中选中 Arial（`arial.ttf`），缺失字符为空；样例图 `960×1193`，按请求顺序画出全部 39 条文字。
- `export-variants` 生成 456 个对象的 `figure.graphics.svg` 和 501 个对象的 `figure.final.svg`，排除的正好是 45 个文字对象，`pruned_groups` 为空；`figure.final.svg` 与工程自身 `figure.svg` 字节一致（本机 57,945 字节，CRLF）。
- 图形版中文字底板、字母圆圈等未标记 `semantic.text_decoration` 的装饰仍保留；这是刻意行为，需要去掉时由宿主标记或 `--exclude`。

## 安全与边界

- 导出和字体预检都不执行保存的绘图源码，不联网，不安装字体。
- 字体检查不是排版求解器：中文与西文混排、字距优化仍需宿主实际查看样例。
- 双 SVG 不能自动识别所有“文字形状”的路径；未标记的轮廓必须显式 `--exclude`，否则会留在 graphics 版中。
