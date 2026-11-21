# Engine 0.6.0 开发交付与验收记录

2026-11-18。按“全部开始执行；直到完成”授权，实施独立素材链与可编辑组合执行。保留完整合并方案及长期路线：[implementation-plan.md](implementation-plan.md)。本次是代码与开发工程交付；六图尚未全部通过视觉验收。

宿主仍实际看图、分解对象、提供坐标/曲线/颜色/布局并检查预览。Engine不调用模型、不自行从自然语言补出几何，也没有内部自动视觉推理循环。没有新增模型服务、供应商SDK、GPU依赖或GUI。

## 实际新增能力

| 能力 | 实际行为与边界 |
|---|---|
| evidence | contrast默认，detail/palette按需；原图只读，源/ROI/board显式仿射与逆映射、alpha背景假设、严格预算、文件摘要。证据不是对象/科学概率。小图不放大；47×35全通道板由1152×1224缩为457×206。 |
| prepare | 接受显式single_asset/asset_bundle输入清单，执行CPU准备；实际返回not_integrated，不称任意Runtime已前置接线。 |
| context/profile | 严格角色/表示/证据/不确定性引用；profile/text/layout为自包含快照；初建显式token解析进Scene。attach只改意图并revision+1，不偷偷重绘。旧复核失效；克隆保留完整闭包。 |
| style-check | 对照真实Scene检查token、圆角、字体、文字与布局；报告mechanical_style_only。没有自动审美、自动科学判断或任意线宽范围规则。 |
| Asset Bundle | 完整成员工程的不可变快照；成员局部ID可重复；严格路径/摘要/文件集/资源限制。字体只记录family/SHA，不复制系统字体。 |
| compose | 真正导入Scene，重写对象/资源/parent/connector/paint与显式typed引用；独立实例、文字、渐变、组透明度与live连接保留；背景preserve/omit必须明确。 |
| fit | 包装既有开放点列拟合/闭合曲线平滑。宿主选点，不读图猜对象；开放输出不报告精确最大残差，不保证自交/隐藏拓扑。 |
| 修补 | 拒绝负渐变stop；context替换时清理旧文档闭包；orphan profile拒绝；新元数据进入receipt与复核绑定。 |

当前仍是Scene0.1、Plan0.1/0.2/0.3、Patch0.2/0.3、Host Review0.3；各新契约独立为0.1。保留旧CLI行为。对齐/间距由宿主显式transform执行，没有自动布局求解器。仅linear gradient，单选字体；没有radial、rich text、font-weight、fallback、自动换行/避让。事务失败回滚和不可变克隆不等于undo/redo历史。

## 六图结果

实际运行目录：`outputs/assets-v06-final`。每图均执行：固定几何无证据构造 → evidence/validate → 绑定context构造 → style-check → 指定ID改色 → 断言非目标对象不变 → 可见渲染差异 → 局部SVG/PNG导出。Researcher另改文字为Scientist并保持text；头像另测共享渐变修改。原四图几何保留，以核对升级没有改变既有绘制。

| 图 | 宿主实际视觉结论 | 主要结果/剩余问题 |
|---|---|---|
| 头像 | passed，限声明简化 | 三个主要形状、蓝渐变保持；不恢复截图边框。 |
| 柠檬 | passed，限声明简化 | 果实、前后叶、柄独立，保持扁平；小轮廓差异仍在。 |
| 烧瓶 | passed，限声明简化 | 圆角、斜边与真实复合孔洞保留。 |
| 生物局部 | uncertain | 主要膜带/中心层/暗线/引线独立；细部间距、连接和周边结构尚不高保真。 |
| Researcher | passed，限风格化简化 | 人物/眼镜/衣领/电脑可编辑，真实文字；头发/头脸比例、面部笔触和字重不同。不是精确肖像恢复。 |
| 交织标志 | failed | 首稿为错误花瓣状；修正改善中央空隙与六瓣轮廓，但连续带、交叉遮挡和间隙比例仍不符合精确验收。另一个修正候选更差，已保留。 |

所有科学复核均not_executed。Host Review已绑定当前Scene/preview/source/runtime；不是外部专家或三人盲评。人物低清不能支持补造身份或手指细节。交织图不导入官方源SVG，背景色clearance并不等于透明孔洞。

`bundle-reviewed-preserve-style`保存六个复核后的完整成员；`bundle-accent-variants`是实际单对象改色后的独立设计任务，不称统一画风或忠实复刻；`bundle-reviewed-public`只含两项许可明确的公开素材。新两图用原冻结0.4 wheel实际跑过首稿，首稿未被新结果覆盖。

同尺度对照：`outputs/assets-v06-final/comparison.png`。详细源SHA、耗时、节点/解析段数、证据回执、编辑任务和复核在`summary.json`。

## 组合的真实修改证明

公开示例：`examples/composition-public`；执行脚本：`scripts/demo_composition.py`；已运行目录：`outputs/composition-public-demo-20261118`。

两种无参考自建Scene都含组、渐变和text，局部ID故意重复；一种带内部connector。同素材导入两次，加第三实例、容器/标签和跨实例连接。修改中间实例wrapper平移后：

- exactly one Scene对象改变；左侧实例数据及世界bbox不变。
- 内部connector仍为connector，端点随实例变换。
- `between_nodes`的SVG路径从`M 267.75 277 L 372.25 277`变为`M 267.75 277 L 392.25 322`。
- `to_stage`从`M 567.75 277 L 721.25 282`变为`M 587.75 322 L 721.25 282`。
- 原组合及Bundle摘要保持；局部导出仍含text/linearGradient/path/rect/g。局部导出的连接是静态path，后续live编辑应保留完整Scene工程。

这证明C01通用流程的构造与编辑链路；不是用户缩略架构图的还原。C02三栏/C03科学机制整图未正式验收；C04说明截图只有极小架构缩略，input_insufficient。

## 实际验证

- 最终源码测试：306 passed、2 skipped、10 subtests passed，23.06秒。两个skip是Windows符号链接创建权限；未据此声明已执行该平台权限场景。
- 源码ZIP已解包到独立目录，用独立安装wheel的解释器运行包内完整测试：306 passed、2 skipped、10 subtests passed，20.11秒。证明公开源码包未漏掉测试所需的公开文件；私图未参与这项测试。
- pip check：No broken requirements found。
- wheel逐模块/Schema字节与当前源码一致，实际离线构建并安装到`outputs/install-check-0.6.0/Lib/site-packages`。工作流断言application模块来自安装目录，未从src导入。
- 独立安装工作流已实际跑：doctor → draw → bundle/validate → compose → 移动实例 → SVG/PNG导出；另跑evidence/validate → prepare → context/token → edit clone → review记录 → bundle → fit。
- 运行无网络/GUI需求。运行依赖从专用Conda通过system-site-packages继承，因此不是在空白机器上从零离线安装全部第三方依赖。原生resvg/OpenCV等仍需目标平台匹配的依赖。
- 0.4 ZIP SHA256保持`4fe7b6a6416f378f49d19f44a1ed32a9c3671bf55bd305c34bb5cac2bc8897b1`；0.4 wheel保持`9ad41ce6c9dcf7763253dc8f06b6fca279411303dea79e22d26e5521ccf6e125`。

## 没有执行的评测与平台

证据关闭/开启采用同一个新Engine和固定宿主几何，渲染字节相同。这只验证证据传递不偷偷改变Scene，不能证明证据使宿主画得更好。没有独立新宿主A/B、真实视觉token/调用数/费用遥测或三名独立盲评；字段如实为unavailable/not_executed。宿主几何编写时间未完整计时，不能认证15分钟人工预算。

没有外部C基线：本机没有Rust；VTracer可选查询在已配置localhost代理处连接被拒绝。未绕过代理，也不把查询失败称为PyPI没有该包。固定提交外部源码研究见`research/external_implementations.md`；无代码/权重复制，无新增运行依赖。

已确认WSL Ubuntu-24.04 / Python3.12.3，但缺Pillow/NumPy/OpenCV/FontTools/resvg_py，因此Linux运行未验证。没有安装系统依赖或启动服务。六图是开发材料，S05–S08新增独立来源与长期48图/来源隔离保留评测未执行；自建几何不增加独立来源数。

## 交付与复现

- `deliverables/scientific-figure-skill-0.6.0.zip`：Skill、源码、Schema、测试、完整计划和文档；排除私图、私有几何、系统字体与环境。
- `dist/scientific_figure_skill-0.6.0-py3-none-any.whl`：安装用Engine；不含模型权重/外部字体。
- `deliverables/public-assets-composition-0.6.0.zip`：公开两图完整Bundle、无参考组合示例、修改前后和局部导出及许可说明。
- `deliverables/six-assets-local-0.6.0.zip`：仅给用户本地的六图/证据/编辑/复核/Bundle与失败候选。包含私图派生物，不做公开再分发。
- `deliverables/verification-0.6.0.json`、`checksums-0.6.0.json`：实测范围、版本、摘要与限制。

```bash
conda run -n ScientificFigure_skill python -I scripts/demo_composition.py --output work/composition-demo
```

本机有私有固定输入时复现六图：

```bash
conda run -n ScientificFigure_skill python -I scripts/benchmark_assets.py --output work/six-assets
```

这条命令不自动批准视觉；新输出必须重新查看后绑定复核。不会创建Git提交、推送到QAagent、发布外部服务或公开上传私图。
