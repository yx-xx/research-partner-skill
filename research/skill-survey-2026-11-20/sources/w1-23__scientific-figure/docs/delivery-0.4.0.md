# 0.4.0 本机交付记录

日期：2026-11-17。独立 Skill；Windows / Anaconda `ScientificFigure_skill` / Python 3.12 / CPU。

本轮完成默认语义绘制、声明式 Plan 0.3、对象与渐变资源事务、宿主视觉/科学复核绑定，以及四张旧图的实际重绘与编辑。没有新增模型 API、模型服务、题材专用算法或运行时依赖。Scene 仍为 0.1，旧 Plan/CLI 行为保留。

## 先看成图

[原图 / 0.3 自动 / 0.4 语义重绘，同尺度对照](../outputs/semantic-v04-delivery/comparison.png)

| 图 | 可直接打开的 SVG | 本次结果 |
|---|---|---|
| 头像 | [figure.svg](../outputs/semantic-v04-delivery/user-avatar/semantic/figure.svg) | 蓝圆、白头、白身体三个绘制对象；真线性渐变；在声明简化范围内宿主视觉通过 |
| 柠檬 | [figure.svg](../outputs/semantic-v04-delivery/twemoji-lemon/semantic/figure.svg) | 平滑果实、独立前后叶和叶柄；轮廓比例仍有小差异；宿主视觉通过 |
| 烧瓶 | [figure.svg](../outputs/semantic-v04-delivery/fontawesome-flask/semantic/figure.svg) | 规则曲线、圆角与真实内部孔洞；宿主视觉通过 |
| 生物局部 | [figure.svg](../outputs/semantic-v04-delivery/user-biological/semantic/figure.svg) | 15 条独立膜带，暗线、中心层和引线分组；35 个绘制节点、3 个渐变；宿主视觉不确定，尚未高保真通过 |

四图均实际单独改色并导出 SVG/PNG；另实测叶柄/引线线宽、头像渐变色标和一条膜带移动。非目标对象保持不变，影响图像的编辑使旧宿主复核过期。原始工程中保留 Scene、ID 清单、QA、回执和复核记录。

四图科学核验均未执行。生物局部的边缘轮廓还有 `outside_canvas` 提醒；它是裁剪构图中的延伸轮廓，保留该提醒，不将机械预算通过说成所有检查或科学检查通过。

## 验证事实

- 最终回归：186 passed、10 subtests passed，10.63 秒。
- `pip check`：No broken requirements found。
- wheel：`scientific_figure_skill-0.4.0-py3-none-any.whl`；核对新 schema 和 reviews 模块在包内。
- 在独立临时工作目录直接从 wheel 导入，断言模块来自 wheel，完成 doctor、无 source 绘图、资源 patch、SVG/PNG 局部导出、review 查询及两个公开参考图的重建。此检查没有借用 editable 源码模块。
- 四张最终 SVG 检查未包含 image、script、foreignObject、data URI 或外部 href。
- [安装包验证记录](../deliverables/verification-0.4.0.json)。

## 文件包

- `deliverables/scientific-figure-skill-0.4.0.zip`：Skill、源码、schema、文档、测试和公开/自建示例；排除用户参考截图、相关私有构造计划、派生工程、系统字体与环境。
- `dist/scientific_figure_skill-0.4.0-py3-none-any.whl`：Engine 安装包；配合源码包中的 SKILL.md 和规范使用。
- `deliverables/semantic-public-examples-0.4.0.zip`：仅柠檬、烧瓶和无参考通用关系图，含各自输入/计划/产物及公开素材许可与署名。
- `deliverables/semantic-four-images-local-0.4.0.zip`：提供给原用户的四图本机检查工程，包含用户截图派生内容；不属于公开示例包，不表示获得公开再分发许可。
- `deliverables/checksums-0.4.0.json`：交付包 SHA-256 与大小。

这些是本机交付文件，未提交至 QAagent，未推送、发布或启动服务。项目自身尚未选择公共再分发许可证；公开素材的 CC BY 4.0 许可独立保留。

## 当前结论与完整路线

本轮证明宿主明确分解对象并使用已有矢量工具，可以让这几张开发图更干净、更符合逐部件编辑。宿主提供了具体几何，auto 组没有同等纠正；没有独立上下文或匹配干预计时，不能据此宣称自动泛化提升。

[完整 A–I 路线](implementation-plan.md) 保留。48 张来源隔离集、独立专家、复杂素材的高保真完成、完整自主科研绘图/自动排版和 WSL/Linux 实测尚未完成；Inkvec/VTracer 外部基线未执行。上述事项不计入本轮完成成果。

[详细契约、实验步骤、计数口径与限制](semantic-drawing.md)
