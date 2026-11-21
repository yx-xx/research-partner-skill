# 0.4 → 素材与组合链审计

2026-11-17。实际基线0.4.0；本轮执行授权涵盖批准方案的素材与后续组合阶段。原0.4源码ZIP/wheel摘要已核对并复制到 outputs/baseline-0.4.0；原四图工程不覆盖。

真实调用：宿主读图、声明具体几何 → Plan0.3 semantic → reconstruct._construct_semantic → Scene0.1 → write_project → SVG/resvg PNG → 宿主查看 → Patch0.3 → 当前绑定Review0.3。Skill自身不调用模型，修正轮次是宿主规范。

复用：已有contrast-only摘要、Lab颜色工具、曲线拟合、组样式继承/矩阵、资源事务、review绑定与对象导出。新增：持久证据/映射、上下文/风格/文字/布局契约、完整成员素材包、跨工程ID与资源映射、保留动态连接的组合。

需要纠正：失败回滚不等于undo；export_scene会冻结connector，不用作组合中间格式；Scene只有linear gradient和单字体真实文本，未支持任意富文本/fallback；新的sidecar必须有schema、持久化与摘要绑定。前置prepare不代表任意Runtime已在首轮前接线。

六图验收：旧avatar/lemon/flask/biological，加76×86 Researcher和47×35交织标志。第三上传为说明截图，架构缩略图不具备全文转录条件；完整C04重建标input_insufficient。所有私有输入与派生工程留本机，不进入可再分发示例。

正式视觉/科学验收、独立评阅与程序测试分开。完整实施范围见 implementation-plan.md；阶段结果以最终交付记录为准，不能从此审计文档推断已完成运行。
