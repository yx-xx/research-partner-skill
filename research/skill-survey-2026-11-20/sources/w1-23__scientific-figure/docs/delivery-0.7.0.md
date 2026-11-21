# 0.7.0 开发交付与实际限制

日期2026-11-18。本轮落实宿主程序化构造、编辑保护、Scene0.2和受控复用，保留0.6及更早接口。交付是开发版，六图并未全部通过，科学核验、三名独立评阅及长期48图来源隔离验收没有完成。不初始化Git、不推送QAagent、不部署服务或上传私图。

## 宿主到产物

1. 宿主读参考图或自然语言要求，列对象、编辑单位、孔洞、连接、局部上下关系和未知内容；先决定重绘还是有许可复用。
2. 宿主显式运行Python/JS绘图程序。薄SceneBuilder处理稳定ID、局部组、重复、仿射、锚点与独立克隆；可选skia-pathops0.9.2计算布尔面域和round中心线轮廓。引擎不理解自然语言对象名，也没有额外模型服务。
3. 程序输出纯候选Scene；新工程通过write_project保存。已有工程先generation diff，比较B上次纯生成、U用户当前、C新纯生成，宿主查看合并预览与冲突后accept。用户改色、移动、改文字可保留；同字段异改、烘焙依赖冲突和陈旧候选明确拒绝。接受后基线是C，而非混入用户编辑的结果。
4. Scene0.2保存源path、宽度、变换、clip/alpha资源和局部关系。渲染按当前几何重新求值交织，SVG由Scene生成，PNG由该SVG渲染。参数、源码、预览和切后path均不构成第二个当前权威。
5. 宿主实际读预览，记录视觉结论。机械QA、宿主视觉和科学核验分开。工程/Bundle加载、diff和accept不运行保存的程序。

[构造API](construction-tools.md)、[安全重跑/Scene0.2](generation-and-effects.md)、[SVG子集](svg-import.md)、[完整批准计划](implementation-plan.md)。计划保留批准时的历史状态，当前事实以本文件和执行记录为准。

## 实测结果

| 项目 | 结果与证据 |
|---|---|
| 最终核心回归 | 557 passed、2 skipped、10 subtests passed，39.38秒；两项Windows symlink权限skip不算通过 |
| 真实NL流程图 | Sample→Treatment→Measurement，含Control/Perturbed；五个真实text。用户改色/移动/改字后采用新容器宽度，三类用户修改保留；连接随移动更新；冲突和陈旧accept不改变receipt |
| 持续局部交织 | 双方移动、改宽、改曲线、组镜像/移动、Bundle、双实例隔离和选中烘焙通过开发检查；故意移出region报告needs_review，预览含裁切，不算通过例 |
| 陌生交织开发例 | 独立上下文设计椭圆环＋圆角三角环，6个交替交叉；基础、双方小幅移动/改宽、组移动/镜像current。16/24渲染、3/3修正。左实例同时加宽移动越出局部region后needs_review且有突兀切口；右实例几何/关系/像素不变。保留该失败编辑，不称全部条件通过 |
| 许可复用 | Twemoji lemon v14.0.2，CC-BY-4.0；显式新增144×144视口后原生/导入像素一致，独立主体改色和Bundle/组合通过。它不计入栅格重绘成绩 |
| 外部draw-better | 固定完整源码、原生成器/审计真实执行；独立B真孔洞任务完成，交互用户批准pending |
| 外部schematic | 原Skill、原示例、独立NL流程实际运行；原gate无警告，但直接移动模块后连接脱离8pt，严格live要求失败 |
| P2收益门槛 | A主体82手填坐标数值；C以26参数计算、0手填最终控制点。只支持继续开发，不证明速度、画质、文件大小或统计优势 |

外部commit、命令、失败及方法/代码边界见[研究记录](../research/external_implementations.md)和[阶段记录](construction-progress-20261118.md)。未将外部JS引擎、浏览器、字体或node_modules纳入核心。

## 六张冻结栅格的新运行

仅使用原冻结栅格，未用官方SVG替换。输出在`outputs/construction-v07-six-redraw/`，实际41次引擎渲染，每例均未超24次/3修正。宿主工作耗时和token的准确遥测不可获取，15分钟目标不能据此宣称满足。

| 图 | 新结论 | 真实限制 |
|---|---|---|
| 头像 | 简化通过 | 圆盘、头、身体、边框独立；原始渐变和边缘仅近似 |
| 柠檬 | 通过 | 主体、柄、两叶分开；曲线控制点并非原矢量恢复 |
| 烧瓶 | 通过 | 真差集孔洞、独立瓶口；白/暗/彩背景成立 |
| Researcher | 简化通过 | 人物/电脑/真实text独立；原字体字重、面部细节未恢复 |
| 生物局部 | uncertain | 正则化膜带仍不同于真实不规则折叠；隐藏连接、中心层身份、引线目标未知 |
| 交织标志 | failed | 六瓣轮廓可辨，但内部角折、连接和上下次序错误；多个区域外/未声明交叉仍needs_review |

主线程实际查看总板、多背景板与原尺寸板，另核六工程receipt、冻结输入SHA、当前review绑定、每次补丁只改目标ID，以及选中Scene/SVG闭包。透明中心孔或机械验证成功均不能覆盖标志失败。代理报告初始运行可能写了Python字节码缓存，严格只写输出目录未能完全证实；没有核心源码编辑。

这些是已见开发图；四例通过限于明确简化范围，不是专家评阅、原矢量恢复或来源隔离泛化。旧0.6仍是四个简化通过、生物不确定、交织失败；本轮不能宣称解决了两例长期缺口。

## Windows 与 Linux

同一个`scientific_figure_skill-0.7.0-py3-none-any.whl`分别安装验证。应用来自各venv的site-packages，未从工作区src导入。实际执行doctor→旧证据/context/edit/review/bundle/compose/fit→新candidate diff/accept→冲突/陈旧拒绝→SVG复用→live交织/组合独立实例→SVG/PNG选中导出。

- Windows11、Conda Python3.12.16创建`.venv-wheel07`，应用独立安装，第三方依赖通过system-site-packages继承专用Conda；这不是空环境全依赖离线安装。字体Arial，SHA记录在verification.json。
- Linux为WSL Ubuntu24.04/Python3.12.3，`.venv-linux07`独立安装第三方依赖及同一wheel；缺ensurepip时仅在venv内用PyPI摘要核验的pip wheel准备，没有修改系统Python。工作流在Linux原生临时目录实际通过（确切路径记录于verification.json）；在同一进程完成结果归档，副本保存于`outputs/construction-v07-wheel-linux-native-verified-20261118/`。
- 首次Linux在`/mnt/e`的WSL Windows盘挂载运行，到evidence原子发布时失败：renameat2(RENAME_NOREPLACE)返回EINVAL。失败目录保留。未退回会覆盖目录的不安全发布；Linux运行应使用支持该操作的原生文件系统。
- Windows/Linux选用不同本机字体及二进制依赖，逐平台记录。未宣称跨平台像素相同，不复制系统字体。
- 依赖安装用过网络；安装后的这些工作流不需要网络。没有提供目标平台的完整依赖离线wheelhouse、Docker镜像、远程部署或GPU模型。核心CPU不等于QAagent服务默认GPU策略。

验证JSON分别见对应输出目录的`verification.json`；安装路径及临时Linux输出路径属于历史证明。复制后的候选diff含原路径绑定，需在新位置重新运行生成/diff流程再accept，不能直接把历史候选视为可移植接受令牌。

## 交付包

- `deliverables/scientific-figure-skill-0.7.0.zip`：Skill、源码、Schema、测试、文档和公开输入。
- `deliverables/scientific_figure_skill-0.7.0-py3-none-any.whl`：应用wheel；可选安装`construction`额外依赖。
- `deliverables/construction-public-examples-0.7.0.zip`：自建几何、NL、安全重跑、许可SVG复用和公开例；含对应许可。
- `deliverables/six-redraw-local-0.7.0.zip`：仅交给用户的本地六图输入/程序/工程/编辑/失败候选和复核，含私有派生，禁止当作公开示例包。
- `deliverables/verification-0.7.0.json`和`checksums-0.7.0.json`：真实状态、各平台及逐包SHA。不是数字签名。

公开包不包含私图及其派生工程、系统字体、模型权重、venv、外部仓库快照或依赖目录。所有包本地交付，未发布到GitHub。新代码没有替用户选择项目级公开许可证。

## 保留的限制

局部关系只支持不透明单色封闭填充或定宽round中心线；共享操作数region重叠拒绝，未知交叉需复核。mask仅有限矢量alpha。三方合并的path/矩阵/有序数组以及occlusions整体是原子字段；不自动解决冲突或执行程序重算任意依赖。SVG导入只接受严格子集；未知CSS/filter/image/use等直接拒绝。

无自动OCR/科学对象识别、富文本/字重/fallback/自动排版求解、undo/redo、GPU分割或完整科学正确性判断。科学核验、三名独立评阅、S05—S08独立来源、正式C02/C03组合、C04不可读截图、48图来源隔离及可选Inkvec/VTracer几何基线仍按完整计划记录，未用本轮例子抵消。
