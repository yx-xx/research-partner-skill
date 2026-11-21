# 程序化构造升级：真实执行记录

日期：2026-11-18。完整范围见[批准计划](implementation-plan.md)，该文件保留批准时的基线判断；本文件和[执行JSON](../outputs/construction-v07-external-20261118/execution-report.json)记录之后的事实。当前源码和已构建应用wheel为0.7.0。P0—P4已完成开发验证；P5许可复用已实跑，陌生综合任务单列；P6六图重画完成，保留4通过/1不确定/1失败；P7 Windows和Linux原生文件系统的wheel工作流均已通过。包文件及真实缺口见[0.7交付](delivery-0.7.0.md)，不代表全部科研验收通过。

## 代理问题已解决

会话继承的HTTP_PROXY/HTTPS_PROXY指向`http://127.0.0.1:7897`，该端口没有监听，导致WinError10061。它是失效的本机进程环境代理地址，不是本项目必须启动的服务。注册表中的用户/系统环境、Windows系统代理及已检查启动文件未声明它；具体由哪个程序注入尚未确定，不能猜成某款代理软件。

Windows现有Meta Tunnel路由可访问公开HTTPS。下载脚本使用仅本次请求不读取失效代理变量的urllib opener；npm仅在子进程移除该失效地址。未修改系统网络、全局环境或持久代理设置，TLS校验保持开启。完整固定仓库与兼容wheel已取得，网络不再是当前阻断。

早期外部代码代理被自动审批以`Code from External`拒绝，未换入口绕过。用户随后明确“允许执行源码”，新调用获准后才执行。历史失败和下载回执保留，不再要求重复授权。

## P0：冻结与规范

- 原0.6源码、Schema、测试、原Skill、来源/私有输入记录和交付物冻结于`outputs/construction-v07-baseline-20261118/`，107个文件逐项SHA验证通过。旧包未覆盖。
- 当前Skill、绘图规范允许宿主Python/JS程序、局部坐标、成熟几何库及阶段预览；Scene保持当前编辑权威，工程加载不执行脚本。
- A/B/C镂空设计任务与预算在首轮前冻结。它是自然语言设计开发例，没有源图，不属于栅格重建、独立生物来源或保留集。

## P1：外部Skill真实执行

| 证据 | 实际结果 | 边界 |
|---|---|---|
| draw-better固定源码 | commit `5e65ee36fb4ad431267defcac268b020d096d7f4`，完整94文件快照与原始通知 | node_modules仅外部验证使用，不进入核心 |
| draw-better原示例 | npm ci禁用lifecycle脚本后成功；原生成器生成9SVG，两个原审计器及sharp/librsvg180/360/720预览，共7命令exit0 | 只证明原工具链可运行 |
| B独立宿主 | 读取原Skill，使用其允许的native SVG/resvg路线；参数化双瓣环、真孔洞、改色与附件移动，原审计6次全部0错误/警告 | 24渲染、2修正；交互用户批准pending，无速度或画质优势结论 |
| schematic固定源码 | commit `09d8b6e98d04b91de6e8b6632b3356b9fc237417`，完整84文件不变 | 核心MIT，字体另GUST/LPPL；系统字体未复制 |
| D原Skill与原示例 | 实际调用Skill(schematic-figure)，Node26/Chrome运行原render/check；原demo和冻结NL流程图真实生成，9命令exit0 | 复核为宿主自审，不是三名专家 |
| D完整要求 | Sample→Treatment→Measurement，Treatment含Control/Perturbed，5个真实text、无位图；基准/编辑gate均0 FAIL/0 WARN | 直接移动Treatment8pt，箭头端点偏8pt；源码重生成才恢复，故严格live连接要求失败 |

主线程查看A/B/D实际图片，核验各工程或文件摘要及编辑变化。原检查器通过不代表检查器未覆盖的关系要求通过。D的失败明确保留在report和D-main-verification，不用自评分覆盖。

## P2：构造工具和实际原型

新增[SceneBuilder](../src/scientific_figure/builder.py)和[pathops适配层](../src/scientific_figure/pathops_backend.py)，详见[实际API](construction-tools.md)。

- builder输出普通Scene0.1：稳定显式ID、局部group坐标、重复、显式锚点、仿射、独立子树克隆；连接和semantic typed refs按既有契约迁移，外部对象引用拒绝，semantic-only资源独立复制。
- pathops0.9.2 Windows wheel经PyPI SHA校验安装。封闭面union/intersection/difference/xor、round中心线轮廓、镜像、空结果和仿射已真实序列化并经resvg渲染。
- 依赖惰性加载，旧CLI无需Skia仍运行。Skia float32、SVG arc→cubic、conic→quadratic均有精度限制；tolerance不是全局误差保证。
- 不规则体与独立附件、三处交替穿插、加宽重生成、镜像、整体移动均有真实预览。交换全局绘制顺序后像素一致，透明间隙在白/暗/彩/透明背景均成立。
- P2阶段的穿插为烘焙差集，单独移动不会更新；该历史静态例保留。之后P4已另实现持续关系，不能把两者混称。

独立任务对照：

| 组 | 真实结构/编辑 | 渲染 | 修正 | 可确认构造负担 |
|---|---|---:|---:|---|
| A，冻结0.6 | 真孔洞、主体改色、附件移动通过 | 10 | 0 | 主体路径82显式坐标数值，含26个cubic控制点 |
| B，原外部Skill | 同类要求通过，交互批准pending | 24 | 2 | 参数化解析曲线；原生SVG |
| C，新薄工具 | 真孔洞、主体改色、附件移动通过；工程回执和编辑隔离经主线程核验 | 15 | 1 | 26输入参数，0手填最终控制点；32个主体cubic由计算产生 |

C记录宿主417.56秒，初步设置时间未单独测量；各组计时范围不能严格比较。无完整模型调用/token账单遥测，不将缺失写成零。C读取一般API文档时接触历史汇总文字已披露，未读取其他臂几何或产物。

[P2判定](../outputs/construction-v07-external-20261118/p2-gate.json)：允许进入P3。收益限于减少手填最终几何，关键结构和编辑要求成立；不声称更快、更少修正、更小SVG、画质领先或统计泛化。实际输出路径数/段数不是质量分。

## P3—P7实际集成

P3已实现generation输入/基线、B/U/C三方比较、精确Patch0.4、声明依赖冲突和revision/content/receipt绑定。真实NL流程图的用户颜色、移动和文字在接受新容器宽度后保留；同字段冲突与预览后再编辑的陈旧候选拒绝，receipt不变。纯生成基线仍是C，保存源码不执行。

P4已实现Scene0.2的typed clip/alpha资源、源几何局部关系、派生求值、visible_bounds、保护项复核以及编辑/克隆/组合/Bundle/选中导出全链。共享操作数region重叠拒绝，未知交叉报告needs_review，不自动补上下关系。完整工程保留live关系，选中静态导出只烘焙当前效果，不带出未选over。

P5严格SVG子集已实现并有许可复用实跑：Twemoji原SVG明确增加144×144尺寸后，原生/导入像素一致，主体改色、Bundle/组合成功。该资源复用单列；陌生交织用椭圆环＋圆角三角环产生6处交替交叉，16/24渲染、3/3修正。基础及小幅移动/改宽current；组合左实例同时移动加宽后越出region，needs_review且有突兀切口，右实例对象/关系/像素不变。主线程实际看板并验证保存工程，不把该失败编辑或开发任务冒称通过/来源隔离保留集。

P6已重新读六张冻结栅格生成新绘图程序，41次实际渲染。主线程查看总板、目标尺寸和多背景图，并独立核输入SHA、六工程receipt、当前review绑定、改色/移动/文字的ID隔离及选中静态Scene/SVG闭包。结果仍是头像/柠檬/烧瓶/Researcher四个简化通过，生物uncertain，交织标志failed；内部错连和折角没有被透明孔洞或机械通过抵消。严格只写输出目录未完全证实，可能存在Python字节码缓存写入；未改核心源码。

P7同一0.7wheel已在Windows与Linux分别安装运行完整新旧工作流，应用来自各venv的site-packages。Windows继承Conda第三方依赖；Linux在独立venv安装依赖、原生文件系统输出通过。首次WSL Windows盘挂载的原子发布失败保留，不冒称DrvFS通过。源码、wheel、公开/私有示例及SHA分包交付，不提供全平台全依赖离线包。

## 最终验证与保留缺口

历史66/372等测试是开发快照。首次包含导入器的全量运行曾有两个Pillow已缓存颜色tuple错误，修复并加回归后，最终全量557 passed、2 skipped、10 subtests passed（39.38秒）。两项Windows symlink权限skip不当作通过。测试数量只是程序回归记录，不是绘图质量分数。

科学核验、三名独立评阅、48图来源隔离、S05—S08独立来源和正式C02/C03/C04仍保留在完整计划。0.7开发交付不表示这些长期验收完成；也不表示生物或交织标志已解决。

没有初始化Git、提交/推送QAagent、部署服务或上传私图。外部快照、依赖目录和系统字体不进入可分发核心包。
