# Scientific Figure Skill 0.9.0 本地交付

日期：2026-11-18。完整0.9计划P0—P6已实施。当前宿主负责参考理解、描述设计、方法选择和真实预览修正；新增接口给同一宿主提供结构化草稿、候选和局部事实。未增加第二模型服务，未改Scene权威或重写渲染底座。

## 已实施

| 阶段 | 实际结果 |
|---|---|
| P0 指南和基线 | 两类任务指南、画法选择表、当前工作流；修正旧文档的“当前0.6/未实现clip等”段，历史图和失败保留 |
| P1 草稿和检查 | planning_tools薄辅助模块；plan draft/check；复用unresolved和FigurePlan0.1；严格最小上下文，不建立第二对象图 |
| P2 候选选择 | registry search / plan suggest；复用已有字段、部件/参数/端口；中英文别名、稳定排序、真实缺少结构和许可限制；空命中不补造 |
| P3 局部测量 | view/profile/topology/repeat；源/ROI/映射/参数/版本/预算/结果摘要；自包含采用快照和检查板，内容缓存键；不输出语义、OCR或科学计数 |
| P4 工程与修正 | planning_context内联generation输入，随receipt、Bundle/组合快照保存；必要部件/当前文字/基线差异追踪；参数更新撤销受影响输入确认；B/U/C保护沿用 |
| P5 实际绘图 | 参考图与自然语言图均真实渲染、看图和一轮定向修正；均有改色/移动/改字、两项局部导出和重开；实际Bundle与组合保留输入快照 |
| P6 版本与交付 | 0.9.0源码/wheel/公开示例/私有图分包，Windows/Linux独立应用文件一致性和新增入口验证，SHA清单 |
| 本地 runtime preflight | prepare/consume在接触输入前探测renderer/fonts/schemas/OpenCV/pathops，回执与manifest记录`ok/degraded/failed`及逐项结果，`doctor`同样输出；模型adapter仍是`adapter_not_available`，`host_call_order_verified`为false |
| 任务字体预检 | `font-probe`汇总整图文字，报告当前字体缺失字符、本地TTF/OTF/TTC逐face覆盖、SHA与样例图；只选一个真实字体，环境变量由用户设置；不声称混排回退 |
| SVG审阅桥 | `review-serve`只读当前`figure.svg`，本机随机令牌、CSP与严格SVG清洗；单卡片预览页，图稿始终自动适配画布并居中（钉针光标，无缩放/平移，点击即标注），编号Pin与批注卡；反馈存`<preview>-review/feedback.json`，绑定SVG摘要与修订，旧版本提交返回409；`review-status`、`--wait` |
| fidelity检查映射 | `shape/detail/topology`映射到已有boundary/region/negative_space绑定并给`plan validate`输出；`plan review`逐项报告checked/missing；repetition/layers/occlusion/connectivity保持needs_review |
| 同源双SVG | `export-variants`从同一Scene输出`figure.final.svg`与无字`figure.graphics.svg`；共用ID几何/样式逐属性一致；文字装饰与指向文字的引线同步排除；工程不变 |

入口及请求示例见[语义规划流程](semantic-planning-workflow.md)、[局部测量契约](local-measurements.md)、[字体预检与双SVG](fonts-and-variants.md)、[交互审阅](../references/interactive-reconstruction.md)。协议保持独立：Engine0.9.0，FigurePlan0.1、Scene0.1/0.2/0.3、generation0.1和旧CLI继续支持。

## 两类实际任务

**参考图语义复刻：** 仍用用户已提供的纳米载体图。先保存未决草稿、四项真实局部测量和候选比较；再用独立模块程序形成新产物。602对象、38实际引用资源、22真text，主SVG与PNG逐像素同源。全部原有文字保留；原图疑似错字不自动纠正。

这不是从零绘制每条路径：明确复用了自己0.8纳米图的数学工具、径向色板、小鼠、载体、血管及若干局部函数。没有加载/执行旧build函数或把旧672对象Scene作为生成输入。新宿主流程将绘制分成独立片段，重画了ER断续曲线并调整肿瘤细胞位置；实际看图后把穿过NIR符号的解释虚线放到后层，正式candidate/diff/accept提交。对照图同时保留参考、0.8和0.9。

**自然语言生图：** “画一个纳米颗粒靶向肿瘤并通过激光触发释放的机制示意图。”新设计三段式图，122对象、3资源、17真text。没有加入制备、静脉注射、配体、受体、特定波长或剂量；开口载体和分散点是明确的示意设计。使用新program片段及两个现有arrow Recipe，共用原编译与Scene。真实预览发现释放文字碰到壳体开口，定向移开标签与引线后再看图。

两图均已实际：只改变三个指定对象（部件颜色、一个对象位置、文字），确认其他对象和共享资源不变；分别导出两个可编辑局部；保存重开；SVG拒绝位图、脚本、外链，PNG由相同SVG渲染。当前主图有实际宿主查看后提交的绑定记录；科学审核为not_executed。

对照可见局限：参考图的小鼠解剖、ER细节、载体剖面、肿瘤排布和柔和笔绘边缘仍有近似；不能宣称恢复了原作者控制点或整体高保真。新接口使拆解和选择可检查，不保证每图视觉自动变好。自然语言图不认证一种实际释放化学机制。

复用披露：参考图没有外部现成科学artwork；复用自家代码，使用SceneBuilder、FontTools、skia-pathops和resvg。描述图为新宿主程序，复用自己常用arc/批量构造模式和arrow Recipe，无外部artwork。Registry有Twemoji柠檬不代表两图使用了它。

## 验证事实

- 完整回归：1056 passed、5 skipped、10 subtests passed，69.95秒。5项skip是Windows符号链接权限限制。测试证明工程行为，不是视觉质量分数。
- 柑橘示例实测：501个对象、45个text对象、39条文字/632字符（47个去重字符）；`font-probe`选Arial且无缺失并画出全部39条；`export-variants`得456个图形对象，`figure.final.svg`与工程`figure.svg`字节一致。
- 审阅与双SVG：本地服务实测`/svg`、`/state`、`/feedback`三路由，无令牌403、旧摘要409、未知对象400；反馈按轮次追加且不被预览替换删除。双SVG测试逐属性比较共用对象的id/transform/style，并验证文字、文字装饰、指向文字的引线和空组被排除，祖先/occlusion冲突明确失败而不是猜。
- 字体预检：在本机Windows字体目录枚举64个候选；Arial缺一个私用区字符时返回needs_input并列出来源，指定真实候选可报告覆盖与需要用户设置的环境变量。样例图用被选字体实际绘制。
- fidelity映射：hard/soft/shape/detail/holes各自产生独立阈值；有约束包时只移除已覆盖项，未覆盖与无机械检查的拓扑项保持needs_review；失败约束使总状态为failed。
- 显式测量缓存：`--cache-dir`关闭时不读不写；命中前重验源字节SHA、完整规范化请求、实现标记和numpy/opencv/pillow版本，并重算`result_sha256`。测试以禁止`_load_source`证明命中不重新解码或计算，并覆盖ROI/问题/源/版本变化与损坏条目按未命中重算。
- 快速预览与分段计时：501对象的柑橘Scene用`--preview`（scale 1）0.33秒，完整交付（scale 3）1.16秒，差主要来自PNG渲染；两条路径都返回`validate/to_svg/render/.../total`秒数，回执记录发布前各段。为本机单次测量，只说明同一台机器上的路径差异，不含模型推理时间。
- 公开文件链：草稿→缺构造返回needs_input→真实检索→四种测量→内联上下文→编译→用户改色/移动/改字→候选合并保留编辑→局部SVG/PNG→Bundle/两个实例组合→源目录移走后重开。自动脚本的视觉字段明确not_executed。
- 边界：复杂细胞Recipe报告缺少mitochondrion；不存在mouse/未知品牌返回空；模糊交叉的阈值变化为ambiguous，宿主保留上下层unknown；简单扁平流程节点不强加渐变或强制检索。
- 实际参考测量：view/profile为ok；选定阈值孔洞和同源模板重复为ambiguous。没有据此宣称透明孔洞、隐藏ER连接或分子数量。
- Windows新`.venv-wheel09`从自身site-packages加载0.9应用，依赖继承专用Conda环境；Linux沿用既有独立venv第三方依赖，应用升级为新wheel。两边逐字节核对wheel内全部应用文件，并实际运行新增CLI、工程、编辑、导出、Bundle/组合链。Linux工作在原生/tmp运行后复制证据，未声称DrvFS原子rename可用。
- 不称空环境全依赖离线安装；两平台使用本地wheel与既有依赖，无网络安装。不承诺跨字体平台PNG逐像素相同。

结构化证据在`deliverables/verification-0.9.0.json`与公开示例包；完整pytest输出和平台验证原始stdout/stderr本地保留在outputs/implementation-v09-20261118。

## 交付包

| 文件 | 内容 |
|---|---|
| scientific-figure-skill-0.9.0.zip | 更新Skill、专业指南、源码、Schema、测试、可运行脚本和文档；不含私图或外部下载代码 |
| scientific_figure_skill-0.9.0-py3-none-any.whl | 与源码一致的Python应用和包数据 |
| scientific-figure-examples-0.9.0.zip | 原创合成源的完整工程链、自然语言图、实际编辑/导出和绑定记录，无私有参考 |
| scientific-figure-private-reference-0.9.0.zip | 用户参考、采用测量、程序、独立片段、新工程、修正候选/差异、真实编辑/局部导出与组合；仅本地私有分发 |
| verification-0.9.0.json / checksums-0.9.0.json | 实际验证结果、文件SHA256；摘要是完整性校验，不是签名 |

安装：

```bash
python -m pip install --no-deps scientific_figure_skill-0.9.0-py3-none-any.whl
```

该命令假设依赖已满足；全新环境正常安装应允许pip安装pyproject列出的依赖。需要面域布尔/定宽stroke_outline时安装construction可选依赖skia-pathops==0.9.2。

程序始终由宿主显式执行；加载、render、diff/accept和Bundle不执行保存源码。python -I不是安全沙箱。规划确认只表示当次输入，不是当前工程审批；当前审核依赖Scene/preview绑定。无隐式持久缓存；测量缓存只在显式`--cache-dir`时读写，命中前重验源字节、完整请求、实现与库版本。无OCR，无自动科学理解。原始外部源未打包时明确external_not_packaged，内联测量仍可读。

未重新引入用户排除的正式大评测、独立宿主消融、盲评、科学认证、Runtime首轮接线、跨版本部件迁移或实验轮廓扩展。系统字体、环境、模型权重和私图没有混入公共包。未初始化Git、未提交/推送QAagent、未启动或部署服务、未修改网络/安全设置。

本轮审阅页是仓库内独立实现，未复制Draw Better SVG或其他第三方UI代码，因此未新增第三方声明；也未提供VS Code Webview侧栏适配器，本地浏览器页是通用回退。Draw Better SVG的MIT审阅流程只作为设计参考，若以后移植其代码，必须在合并前记录固定上游版本、文件、MIT声明和修改。
