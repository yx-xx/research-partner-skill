# 宿主程序化构造工具（开发版）

日期：2026-11-18。Engine0.7.0提供以下薄Python接口，兼容Scene0.1并新增Scene0.2。Scene是当前几何、文字、样式、层级和关系的唯一权威；加载工程、Bundle或渲染工程均不会执行生成程序。旧0.6发布包不含这些模块。

## 安装与运行边界

普通Scene构造不需要新增几何依赖。布尔运算和描边轮廓需可选的`skia-pathops`；本机已核验并安装0.9.2 Windows wheel。旧CLI不在启动时导入它。无需Node、浏览器、GPU或模型服务。

程序由宿主使用正常工具显式运行。已有工程的重跑输出独立candidate源目录，使用`generation diff`查看B/U/C合并预览，再以`generation accept --base-revision N`提交；冲突不覆盖当前用户工程。完整格式和限制见[安全重跑与Scene0.2](generation-and-effects.md)。

```bash
python -m pip install -e ".[dev,construction]"
```

## SceneBuilder

```python
from scientific_figure.builder import SceneBuilder
from scientific_figure.pathops_backend import boolean
from scientific_figure.project import write_project

b = SceneBuilder(200, 150)
b.group('asset', transform=[1, 0, 0, 1, 10, 10])
outer = 'M10 10H170V120H10Z'
hole = 'M55 40H120V90H55Z'
b.path('body', boolean('difference', outer, hole),
       parent='asset', style={'fill': '#286e84'})
b.ellipse('accent', 150, 25, 8, 5, parent='asset',
          style={'fill': '#d27c3e'})
b.anchor('asset', 'output', [170, 65])
scene = b.build()
write_project(scene, 'new-candidate-project', scale=1)
```

`build()`返回独立的验证后Scene快照，输入字典不被共享。每个新增对象也先验证再提交给builder，因此对象和资源必须先于引用它们的对象存在，不支持前向引用。

- `group(id, **options)`、`rect(id,x,y,width,height,**options)`、`ellipse(id,cx,cy,rx,ry,**options)`、`path(id,d,**options)`、`text(id,x,y,text,**options)`；通用`add(id,kind,geometry,**options)`可创建connector。
- 构造时可传`schema_version='0.2'`；默认仍0.1。
- options为Scene字段：`parent/transform/style/semantic/visible`，0.2另有`clip/mask`。坐标属于对象局部坐标系，父组变换统一生效；使用普通Python循环重复对象。
- `resource(id,kind,**data)`支持线性渐变；Scene0.2另支持`clip_path/alpha_mask`。没有径向渐变或任意SVG资源。
- `occlusion(id,over,under,frame=...,region=[x,y,w,h],gap=0)`添加0.2局部关系；源路径和关系都保存在Scene，渲染时求值。
- `anchor(id,name,[x,y])`登记显式局部点；`anchor_point(id,name,relative_to=None)`计算世界点或另一个对象局部点。锚点是程序内辅助数据，不写入Scene，不等于新的live特征点约束。原`Geometry.anchor()`仍是世界bbox锚点。
- `transform(id,matrix,compose=False)`设置六元仿射；compose=True使用旧矩阵乘新矩阵，先执行右侧新矩阵。
- `clone(id,ids,resource_ids=...,occlusion_ids=...,parent=...,transform=...)`显式映射完整子树及其资源ID，生成独立副本；connector和semantic中的typed内部引用均迁移，外部对象引用拒绝。仅在semantic中引用的资源也须提供resource_ids并独立复制；普通字符串不猜作ID。不自动把父级继承样式复制进子树根，应把完整编辑单元作为克隆根。
- `path(id,'')`省略空几何，不占用ID。空布尔结果不会生成无效Scene path。

## 单一几何后端

`pathops_backend.boolean(operation,left_d,right_d,fill_rule='nonzero',tolerance=.25)`提供union/intersection/difference/xor。操作数必须显式Z闭合；空操作数/空结果使用空字符串。输出使用nonzero绕向，真实孔洞不需要背景色补丁。

`stroke_outline(d,width,tolerance=.25)`把中心线变成round cap/join封闭轮廓。它复制工作路径，不修改源中心线。先描边再非均匀仿射与先变换中心线再描边代表不同的线宽语义，宿主必须明确选择。

`transformed(d,matrix)`使用FontTools pen计算仿射，无需加载Skia；镜像保留复合孔洞关系。`backend_info()`返回实际安装发行版与数值边界。

Skia使用float32。SVG arc先经FontTools转cubic；conic再转quadratic。tolerance仅控制conic转换，不是全局最大几何误差保证。适配层不默认叠加平滑；小尺度、细缝、相切和高曲率仍应查看实际SVG渲染。现有`geometry.union()`仅合并bbox，不承担面域union。

## 局部交织开发例

`scripts/construction_geometry_prototypes.py`用解析正弦中心线算出三处交叉，分别声明A在上、B在上、A在上。程序将中心线描边成轮廓，在各region内计算差集；生成的两个可编辑path不依赖全局先后顺序。加宽变体显式重运行程序，镜像和整体组移动使用普通Scene变换。

这是P2阶段保留的静态开发例，单独改其烘焙path不会重新计算穿插。0.7另有`scripts/verify_live_effects_workflow.py`，直接保存Scene0.2源中心线、宽度和局部关系：分别移动双方、改宽/曲线、组移动/镜像后重新求值；交叉离开区域则needs_review。完整Bundle/组合保留关系，选中静态导出烘焙当前效果。详见[关系求值限制](generation-and-effects.md)。程序、机械采样、真实预览和限制均保存，不以测试通过代替宿主视觉复核。
