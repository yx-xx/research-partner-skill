# Engine 0.8：Recipe、FigurePlan 与可编辑图组

宿主负责对象、科学含义、必要结构与未知项；工具负责确定性构造。没有新增模型 API、训练、GPU服务或GUI。Scene 是当前几何、文字、样式、层级和关系的唯一权威。FigurePlan 是生成输入快照，用户编辑后的 Scene 不反向恢复参数。协议版本独立：Engine0.8、Scene0.3、FigurePlan0.1、composition-plan0.2，旧协议仍严格读取。

## 选择构造方法

1. 先明确尺寸、可编辑部件、来源与科学未知；读原图或完整文字任务。
2. 按实际结构和画风选择方法：适合时复用合法素材、已有局部绘图函数或Recipe，也可以直接写自由构造程序。不能为了匹配目录把复杂对象画得更粗略。选择Recipe/Registry资源时再检查参数、许可、固定版本、文件SHA及改动。
3. 用Builder和普通Python/JS程序按需构造；程序通过宿主正常工具显式运行。direct Scene和FigurePlan均可选，不必先套Recipe。`program`接收预生成、摘要绑定的Scene，不执行源码。
4. 编译、读实际预览、按ID修改，再记录当前绑定的视觉审核。科学审核单独记录。机械通过不等于结构科学正确。
5. 保存完整工程，组合用 Bundle；按需输出局部SVG/PNG。完整工程保留 live 关系，静态选中导出烘焙关系影响。

```bash
figure-cli recipe list
```

```bash
figure-cli recipe describe cell_symbol
```

```bash
figure-cli recipe build cell_symbol --instance cell --params cell-params.json --output work/cell
```

`recipe build` 是方便的单素材入口；需要模板更新与意图闭包时，使用 FigurePlan。Recipe 所有坐标在局部空间；`recipe build` 自动设置留白viewBox以完整显示单素材的负坐标，保留原部件坐标。Builder/FigurePlan程序仍由宿主明确选择画布和transform。完整参数说明来自 `describe`，不是自然语言自动选参。

## FigurePlan 编译与安全更新

顶层必填 `schema_version:0.1, id, task_type, purpose, canvas, modules, relations, review_spec`。ObjectSpec 必填 `id, role, construction`；支持 recipe、direct、asset、program、unresolved。module 和对象 transform 可组合，Recipe root 位于对象包装组内。`editable_parts` 是必须存在的局部部件键；未知部件、未知来源、摘要不符或未明确构造直接失败。

```bash
figure-cli plan validate figure-plan.json
```

```bash
figure-cli plan compile figure-plan.json --output work/figure
```

```bash
figure-cli plan compile figure-plan.json --fragments host-fragments.json --candidate --output work/candidate
```

生成工程包含 `figure-plan.json` 与 `generation.json`，都受 receipt 与生成输入摘要绑定。candidate 严格只含 `scene.json` 和 `generation-input.json`；预览由 diff 另行生成。加载、diff、accept、Bundle均不执行保存源码。

```bash
figure-cli template candidate work/figure --updates selected-update.json --output work/template-candidate
```

`selected-update.json` 示例：`{"cellA":{"params":{"rx":72}}}`。只选择要更新的实例；可显式更新 params、version、transform、style_bindings。未安装版本不能伪装升级，Recipe源码变了但未明确迁移也会拒绝。当前仅固定1.0.0库；跨版本部件迁移不在用户当前范围内。

```bash
figure-cli generation diff work/figure --candidate work/template-candidate --output work/template-diff
```

查看 merged 预览与 conflicts 后执行：

```bash
figure-cli generation accept work/figure --candidate work/template-diff --base-revision 1
```

B=旧纯生成、U=当前用户Scene、C=新纯候选。用户单独改色、位置、文字保留；同字段异改保U并报告冲突。派生几何依赖也参与：改过文字后重算依赖旧文字的节点尺寸需冲突复核。Recipe明确声明的局部依赖坐标框架允许共同父级整体变换保留；没有该声明的旧生成记录继续使用保守世界依赖。成功基线更新为C，不能把用户改色写成新纯基线。

## 关系与端口

- `execute`：connects/points_to生成连接线；points_to默认箭头。显式 occludes 需要可计算的 over/under 部件以及 frame/region/gap。behind/in_front_of仅支持同父级对象的绘制顺序。contains/belongs_to执行必须显式 `params:{"reparent":true}`，含义是保留局部坐标重挂，可能改变世界位置。
- `check`：aligned_with/contains复用现有布局检查，支持 aligned_left、aligned_top、same_width、same_height、contains、left_of、above及显式tolerance。其他 check 返回needs_review。
- `semantic`：保存宿主断言，不执行几何。repeats/mirrors/magnifies等若要求execute，当前返回needs_input；宿主应给明确构造/自由程序，或保持语义声明。

Scene0.3对象可保存最多32个命名局部 `anchors`。连接器引用 `port:name`，经父级仿射动态解析；旧left/right/top/bottom/center仍是世界bbox锚点。`builder.anchor()`仍仅程序辅助，不等同持久端口。修改端口可用Patch0.4整体对象记录。

## 样式、文字和证据

Scene0.3支持真 radial_gradient 与数字列表 stroke_dasharray/stroke_dashoffset。SVG导入默认仍严格0.2；新特性必须显式 `--scene-version 0.3`。不支持CSS、脚本、外链、位图、filter/use；dasharray="none"尚不支持，需显式去除该继承来源或重构片段。遮挡操作数不接受虚线作为连续中心线。

FigurePlan可含既有 style_profile 与显式 token_bindings。`color_semantics` 保护科学颜色与含义，编译冲突返回needs_input，不能为统一风格覆盖。当前用户改色由 `plan review` 报告，不从输入快照悄悄恢复颜色。

```bash
figure-cli text measure measure-request.json
```

```bash
figure-cli text wrap wrap-request.json
```

请求分别为 `{"text":"Label","font_size":14,"target_width":100}`、`{"text":"A long label","max_width":100,"font_size":14}`。使用真实字体指标与SHA；wrap只返回建议，不改Scene。无rich text、字重、上下标、fallback或自动避让。`text validate-inventory` 校验另行的丰富文字清单，保留original/normalized/suggestion/uncertainty/source；不自动接受纠错。

```bash
figure-cli consume work/prepared --ids input --views source.png,evidence_board.png --output consumption.json
```

consume核对实际prepare目录、原始请求/源图SHA、ROI、映射、全部回执/文件和预算，返回真实文件内容及消费记录。它证明本地工具边界读取，不能证明模型看懂、内容已发给模型、发生在首轮之前。返回的runtime_preflight只描述本机renderer/fonts/schemas/OpenCV/pathops，adapter仍是adapter_not_available；无OCR/重复识别模型。外部候选可用 `candidates proposals.json --source reference.png` 校验来源与坐标，候选不改Scene。

## Registry 与组合闭包

内置小目录：15个Recipe、2个符号族元数据、1个合法Twemoji柠檬矢量资产。没有联网搜索/下载/插件执行。Recipe原始公式的项目公开许可未定，不擅自标MIT。Twemoji保留CC-BY4.0、作者、固定ref、原始SHA、实际分发文件SHA和viewport改动；两种SHA不可混用。合法复用不算栅格重建成绩。

composition-plan0.2支持Scene0.3容器与端口。组合保存原成员context/text/layout/style/protection/FigurePlan和生成输入的惰性快照，通过各实例命名空间聚合；同名token不自动合并。组合不继承成员审核，不安装活动的成员generation/Planner绑定。当前明确拒绝嵌套组合成员及token alias，避免丢失意图。

## 实验与评价边界

`primitives.normalize_fill`规范化填充交叉/winding，保留真实孔洞，不是任意曲线简化。closed_offset及variable_outline明确experimental：圆角边界带膨胀/侵蚀或采样圆盘/梯形包络。可能塌缩/改变拓扑；Skia float32、arc/conic近似，没有全局Hausdorff误差保证。

30个Recipe结构变体和流程示例证明本地工程链，不证明画图质量提高。用户已撤出正式pilot、A—E独立宿主消融、48项来源隔离、人类盲评、领域审核、Runtime接线、跨版本模板迁移和实验轮廓扩展；这些不再是绘图交付前提或当前待办。已有实验函数不扩展。实际任务以参考/要求、当前预览、必要结构和真实编辑导出判断；替换旧图须同尺寸对照。历史失败仍保留，不由新示例冲销。
