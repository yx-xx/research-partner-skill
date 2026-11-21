# 安全重跑与Scene0.2（开发接口）

2026-11-18。核心为文件CLI与Python，无GUI、Node、浏览器或模型服务依赖。源码程序由宿主显式运行；以下所有工程/Bundle加载、diff和accept只读数据，均不执行保存的源码。Scene是当前生效状态，参数不是第二个实时编辑树。

## 安全重跑

`scientific_figure.generation`提供：

```python
from scientific_figure.generation import generation_input, attach_generation
from scientific_figure.project import write_project

# pure_scene是宿主程序已经计算完成、没有provenance的封闭Scene。
record = generation_input(
    pure_scene, language='python', source=source_text,
    params={'width': 22}, backend={'name': 'SceneBuilder', 'version': '0.2'},
    dependencies=[],
)
scene, extras = attach_generation(pure_scene, record)
write_project(scene, 'project', extras=extras)
```

若只有项目的一部分属于生成程序，传入自包含的`baseline=`；初始基线中的对象与资源必须与项目相符。未列入范围的用户对象不归生成程序所有。source是源码文本及SHA，params/inputs是有限JSON数据，backend是实际版本。保存来源不是允许应用自动运行它。

下一次宿主输出新目录，且目录中必须恰好只有`scene.json`与`generation-input.json`，分别包含纯生成C和用其生成的record。当前候选允许Scene0.1/0.2，不接受带任意provenance的外部工程；有上下文/科学来源的项目须通过既有正式入口建立，再按支持范围处理。

```bash
figure-cli generation diff project --candidate new-source --output diff-result
```

```bash
figure-cli generation accept project --candidate diff-result --base-revision 3
```

B是上一次接受的纯生成基线，U是用户当前Scene，C是新纯生成候选。U单独修改保U；C单独修改采用C；相同修改无冲突；双方改同一字段且不同则保U并报冲突。字典属性逐项合并，path、矩阵、有序数组是原子值。增删、ID碰撞、parent、资源、typed refs和兄弟顺序均参与。成功后基线更新为C，不把保留下来的用户改色/位置混入B。

Scene0.2整个occlusions数组目前按原子字段比较；不同位置的两个关系同时修改仍可能冲突。这是明确的保守边界，避免默默覆盖用户关系。冲突需宿主处理输入并重新diff，没有“自动选生成方”开关。

烘焙下游几何必须声明`dependencies=[{'object_id':'result','depends_on':[{'type':'object','id':'operand'}]}]`。它是有限DAG，读取对象及祖先/资源状态；用户保留了不同操作数、候选却更新了依赖它的烘焙path时报告冲突。不提供执行程序或自动重算任意依赖的服务。未声明的真实程序依赖无法由引擎猜出。

差异目录保存完整C、合并预览工程、冲突、proposed-scene和摘要。accept核验原候选文件、快照、所有产物（含预览）、当前revision及canonical内容/receipt SHA，重算合并后通过Patch0.4和原工程事务提交；锁内再查当前工程。冲突、陈旧或坏引用不改变工程。原候选文件必须保留至接受完成；摘要用于防止意外变化，不是防恶意重写者的数字签名。

## Patch0.4

旧set、0.2、0.3语义保留。0.4提供精确`put_object`/`put_resource`、`remove_object`/`remove_resource`、完整`order_objects`，以及受限`scene_fields`。整份记录替换可明确清除clip/mask或其他可选字段、重挂parent；关系通过scene_fields的occlusions更新或unset。所有引用在整个事务结束统一validate，失败不修改输入，不用replace_subtree伪装用户编辑保护。

## Scene0.2裁剪和遮罩

Scene0.1仍严格拒绝新字段。0.2对象可有`clip`指向`kind:clip_path`资源，或`mask`指向`kind:alpha_mask`资源：

```json
{"id":"crop","kind":"clip_path","d":"M0 0H40V30H0Z","fill_rule":"nonzero"}
```

```json
{"id":"fade","kind":"alpha_mask","region":[0,0,40,30],"shapes":[{"d":"M0 0H40V30H0Z","alpha":0.5}]}
```

均为对象局部坐标的userSpaceOnUse。mask是有限白色矢量形状的alpha合成，最多16形；不是luminance、位图、filter或任意混合。组opacity由SVG组合一次。资源类型、命名空间、引用闭包与渲染属性均校验，clip资源不能充当fill paint。

## 持续局部交织

```json
{"id":"cross-1","over":"band-a","under":"band-b","frame":"local-group","region":[40,20,50,80],"gap":4}
```

Scene顶层occlusions保存稳定关系ID、over/under对象、region坐标frame（组ID或null世界坐标）和非负gap。gap是在frame单位中对over轮廓外扩的距离。源对象首期仅支持不透明单色封闭填充path，或单色定宽round中心线path；两者合用、半透明祖先、text、connector、已经clip/mask的操作数明确不支持。

求值从各对象原始路径/宽度和当前变换计算，先统一到frame，再在region内切under；不递归读取对方切后的输出。因此局部A上B、另一处B上A可以形成全局关系环而不形成计算递归。共享操作数的region重叠首期保守拒绝，避免同一局部三方循环或未支持的混合次序。不同声明对象对的额外交叉、区域外交叉、交叉消失或多个轮廓均报告needs_review，不自动推断新上下关系。

诊断基于几何交集及轮廓数，不是完整拓扑证明；复杂含孔操作数可能保守地要求复核。最多32关系、16不同操作数、256资源及明确path/工作量预算。原始source保存在Scene，派生切后路径只用于当前渲染；移动、旋转、改宽或曲线时重新求值。

原`Geometry.bounds()`/bbox锚点仍表示原始保守bounds。新增`visible_bounds()`纳入局部切除及clip/mask范围，仍不是像素可见性证明。保护对象有非空原bbox不能自动通过遮挡检查：确定空范围会拒绝，无法证明实际覆盖则needs_review。defs路径计入复杂度。

## 保存、组合和导出

完整工程与Bundle保留源路径、资源和关系；组合将对象、资源、region frame及over/under全部映射到各实例，实例互相独立。clone需显式完整`occlusion_ids`，关系frame与双方必须在克隆子树内；跨子树或世界绑定的关系不猜迁移。

选中静态导出先按当前全Scene烘焙occlusion，再只输出选中对象和祖先，不顺带导出未选over对象；clip/mask仍保留实际资源闭包。导出provenance明确记录烘焙和当时diagnostic状态。完整Scene导出与Bundle才保留live关系，静态SVG交给外部编辑器后不具备本引擎的约束求值器。

实际链路见`scripts/verify_generation_workflow.py`及`scripts/verify_live_effects_workflow.py`。后者保留一条故意移出region的失败用例，不把needs_review称为通过。
