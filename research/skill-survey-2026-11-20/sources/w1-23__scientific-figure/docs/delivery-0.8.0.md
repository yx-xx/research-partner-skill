# Scientific Figure Skill 0.8.0 基础技术交付

日期：2026-11-18。用户授权“按完整计划实施”后，完成了P2—P7的本地核心能力及P9基础技术包。**P8正式评测、Runtime真实接线和外部审核仍有明确缺项，不能称整个P0—P9正式验收全部完成。** 完整范围与当前状态保留在[完整计划](next-stage-plan-0.8.md)，用法见[0.8工作流](drawing-workflow-0.8.md)。没有Git初始化、提交、推送、部署或对外上传。

## 已实现

- Primitives：原子add_many、稳定namespace、Scene0.3持久局部端口、径向渐变、虚线、显式新版SVG导入。旧Scene/Plan/Patch/CLI保留严格行为。单素材recipe CLI自动留白适配viewBox。
- 15个Recipe族：arrow、flow_node、legend、zoom_callout、leaf、cell_symbol、vessel_segment、particle、loop_band、interwoven_bands、fruit、simple_microbe、lab_lamp、lab_book、cluster。严格参数/跨参数范围、固定版本、稳定内部部件、私有资源、seed与来源限制。每族两个结构变体，真实内部编辑、选中导出、保存重开和独立双实例。
- FigurePlan：意图/构造输入协议、确定性编译、execute/check/semantic分级、显式未知和缺输入、程序片段摘要验证。无第二份活动几何或新增模型API。
- 选中实例更新：生成候选，再走原有B/U/C diff/accept；保留用户改色、整体移动和其他实例文字，冲突拒绝覆盖，成功纯生成基线仍是C。Recipe局部派生依赖明确声明坐标框架；旧记录继续保守世界依赖。
- Registry：15 Recipe、2符号族元数据、1个CC-BY4.0 Twemoji资产；严格本地版本/许可/原始与分发SHA、受控导入、来源闭包及包内数据。原创代码公开许可未定，不擅自标MIT。
- Evidence/Text：真实prepare文件消费、原请求/源图/ROI/映射/回执/预算核对；无模型的外部OCR/重复候选校验；真字体测量、显式换行建议及保留原文/纠错/不确定性的文字清单校验。建议不自动写回Scene。
- Composition：Scene0.3与ports保留；成员context/text/layout/style/protection/FigurePlan/generation惰性来源闭包，独立实例命名空间；不继承成员审核。

## 实际证据

验证目录：`outputs/implementation-v08-20261118/`。

| 检查 | 结果与证据 |
|---|---|
| 全量回归 | 最终846 passed、5 skipped、10 subtests passed，108.05s；`pytest-release.xml`。5项skip均为Windows符号链接权限；早前集成轮844通过记录另保留 |
| Recipe变体 | 15族、30变体，15项内部编辑/导出/双实例隔离；全30成员Bundle与组合；`recipes/evaluation.json`、真实PNG atlas。记录生成时版本字段仍0.7.0，是0.8开发代码在版本号正式升档前的运行，不是历史0.7能力 |
| 图组 | 263对象、100 paths、38 texts、1资源、2occlusions；当前预览已查看，属于示意符号和工程验证 |
| A参考链 | 已知公共柠檬栅格→真实prepare/consume→FigurePlan direct构造→参考对照→叶片编辑/局部导出/重开；`reference-plan/`。轮廓与顶端细节仍近似，非新来源或高保真成绩；没有用Registry源SVG替换栅格任务 |
| B自然语言链 | 明确的Prepare particle→Expose cells→Measure signal意图，Recipe构造、真实文字编辑、端口跟随、选中模板更新；`workflow-final/` |
| C组合链 | 两实例完整Bundle/compose、成员意图快照、Scene编辑、导出；另有30素材总览组合。正式科学图整体验收未完成 |
| 旧六图兼容 | 当前0.8读取冻结0.7工程并重渲染，同机六例像素均相等；`legacy-six-compatibility.json`。不重画、不改旧视觉状态：四例简化通过、生物uncertain、交织标志failed |
| Windows应用wheel | 新`.venv-wheel08`从自身site-packages加载0.8；继承专用Conda第三方依赖，非空环境离线全依赖安装；`wheel-windows-final/verification.json` |
| Linux应用wheel | WSL Ubuntu24.04、Python3.12.3，从既有独立venv安装0.8 wheel、原生Linux临时文件系统跑完整新链后复制证据；依赖沿用此前已安装环境；`wheel-linux-final/verification.json` |
| 来源一致性 | wheel内全部72个源码/Schema/Registry数据文件逐字节与当前源码核对，ZIP CRC通过；最终包SHA和文件数见checksums |

Windows用Arial，Linux用DejaVu Sans，均记录字体SHA，未复制字体。没有声称跨平台像素相同。两边都实际验证编译→edit→template candidate→diff→accept→review→Bundle→compose→SVG/PNG，以及径向/虚线native/imported同平台像素相等；工作流本身无需联网。

### 批量性能

同机开发环境、每种方式三次，比较相同输入/对象/资源。826对象纳米载体工程只读Scene，不执行私图生成器：旧0.7逐对象构造中位46.8803s，当前逐对象45.0279s，当前batch0.1906s。1000圆点旧24.7670s、当前batch0.0911s。SVG和PNG耗时基本相当。证据：`builder-profile.json`。改善来自一批统一校验，不能说视觉质量提高或整任务/模型推理快了246倍。

### 宿主视觉记录

当前宿主实际读取30变体atlas、总览组合、编辑后流程和参考对照。示意图在已声明范围内可读；叶片/微生物/血管不是解剖复原，参考柠檬主形/叶尖/顶端绿色细节有明显近似。记录：`host-visual-review.json`。它不是三名独立人类评阅或领域科学认证。

## 未完成与受限项

- 12项新来源正式pilot、独立宿主A—E消融、长期48项来源隔离/保留集没有执行。当前30个参数变体不能充30个独立来源；旧图和开发例不能充保留集。方法冻结前缺少运行前完整任务卡是本轮评测门槛缺口，不能事后补写为已冻结。
- 三名人类盲评与领域科学核验：not_executed；Runtime adapter：not_integrated。consume只证明本地工具实际读取文件，不证明模型理解或首轮前调用顺序。
- 固定Recipe仅1.0.0；当前参数更新已验证，跨版本部件重命名/迁移未实现。Recipe库实现摘要变化会拒绝自动升级。
- repeats/mirrors/magnifies等未提供几何执行器；execute明确needs_input，宿主可写自由构造程序或保留semantic。check之外的科学含义不由机械系统认证。
- 嵌套组合成员和token alias明确拒绝；高级富文本/字重/上下标/fallback、自动避让/排版、真正undo/redo未实现。
- closed_offset/variable_outline仅experimental，有塌缩/拓扑改变及数值近似限制。虚线"none"继承覆盖暂不支持，有限occlusion不接受虚线中心线。
- Registry只有一个有许可外部资产；不声称科研素材市场或自动资源检索。项目原创代码尚无选定公共发行许可。

Linux验证曾因跨调用临时目录未保留、随后shell临时变量为空失败，最终使用固定原生临时路径并在同一次调用复制证据后通过。源码集成脚本先后因错误的composition字段和漏写背景策略失败，均在独立失败目录保留，最终修正脚本后全链通过。它们不是最终通过记录的替代。

## 本地交付物

- `deliverables/scientific-figure-skill-0.8.0.zip`：源码、Skill、完整说明、测试和明确公开开发输入；排除私有截图/派生题图、环境、权重和系统字体。
- `deliverables/scientific_figure_skill-0.8.0-py3-none-any.whl`：应用wheel，含全部Schema和Registry实际资源/许可。
- `deliverables/scientific-figure-examples-0.8.0.zip`：30变体、示例工程/编辑/局部导出/Bundle/组合、A/B/C工程链与验证报告。
- `deliverables/verification-0.8.0.json`、`checksums-0.8.0.json`：实际结果和SHA。

旧0.7源码包、私有六图、台灯与纳米载体交付保持原样，不重复打包或更改历史失败状态。本次交付在本机提供，没有上传或发布。
