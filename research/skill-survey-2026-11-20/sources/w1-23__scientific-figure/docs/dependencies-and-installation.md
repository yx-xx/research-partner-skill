# 完整依赖与安装（v0.9.0）

Python 包名为 `scientific-figure-skill`，Skill 名称为 `scientific-figure`，命令入口为 `figure-cli`。支持 Python >=3.12；实际验证为 Windows 11/Python 3.12.16 与 WSL Ubuntu 24.04/Python 3.12。核心使用 CPU，不需要模型 API、GPU、CUDA、浏览器、Node.js、Docker 或 GUI。

## 依赖表

以 [pyproject.toml](../pyproject.toml) 为安装依据。

| 依赖 | 声明版本 | 实际验证版本 | 用途 |
|---|---|---|---|
| Pillow | >=11,<13 | 12.3.0 | 图像读取、ROI、检查板 |
| NumPy | >=2,<3 | 2.5.5 | 像素数组与数值计算 |
| opencv-python-headless | >=4.10,<5 | 4.14.0.94 | 局部阈值、连通候选、模板匹配及显式像素工具 |
| FontTools | >=4.61,<5 | 4.68.0 | 字体测量、几何适配 |
| jsonschema | >=4.23,<5 | 4.26.0 | 严格协议检查 |
| resvg-py | >=0.2,<1 | 0.5.0 | 将同一 SVG 渲染成 PNG |
| skia-pathops | ==0.9.2，可选 construction | 0.9.2 | 面域布尔与定宽轮廓 |
| pytest | >=8,<10，可选 dev | Windows 9.2.0 | 开发测试 |
| setuptools | >=75，构建环境 | 由构建隔离环境解析 | Python 包构建 |

jsonschema 的传递依赖包括 attrs、jsonschema-specifications、referencing、rpds-py、typing_extensions；测试栈另含 iniconfig、packaging、pluggy、Pygments，以及 Windows colorama。版本快照见 [Windows 记录](../requirements-win-py312.lock.txt) 和 [Linux 运行时记录](../requirements-linux-py312.lock.txt)。它们只锁版本，不含下载哈希；不是跨平台二进制锁。Linux 文件未锁定开发工具。

## 一键创建独立环境

在仓库根目录运行；默认安装 construction，可选 `--dev`。新环境不继承系统包；目标目录已经存在时拒绝覆盖。

```bash
python -I scripts/bootstrap.py --venv .venv --dev
```

Python 3.12 的 Windows/Linux 可按本项目已验证的版本约束安装：

```bash
python -I scripts/bootstrap.py --venv .venv --dev --locked
```

先查看将执行的命令：

```bash
python -I scripts/bootstrap.py --venv .venv --locked --dry-run
```

脚本通过正常 pip 包源安装，可能联网下载；不自带离线依赖库，不修改代理或系统 Python。Linux 缺 ensurepip 时，先使用发行版提供的 python3-venv 或 Conda 创建 Python 环境；脚本不会自动修改系统软件。

## 手动安装

普通环境：

```bash
python -m venv .venv
```

Windows 的后续命令通过 `.venv/Scripts/python.exe` 执行：

```bash
.venv/Scripts/python.exe -m pip install ".[dev,construction]"
```

```bash
.venv/Scripts/figure-cli.exe doctor --json
```

Linux 的对应命令：

```bash
.venv/bin/python -m pip install ".[dev,construction]"
```

```bash
.venv/bin/figure-cli doctor --json
```

不需要可选构造或开发工具时，安装 `.` 即可。开发 editable 安装可使用 `python -m pip install -e ".[dev,construction]"`。

使用已构建 wheel：

```bash
python -m pip install "deliverables/scientific_figure_skill-0.9.0-py3-none-any.whl[construction]"
```

pip 将解析正常运行依赖；仅在依赖已经满足时才使用 `--no-deps`。

## Anaconda

```bash
conda env create --file environment.yml
```

```bash
conda run -n ScientificFigure_skill python -m pip install ".[dev,construction]"
```

```bash
conda run -n ScientificFigure_skill figure-cli doctor --json
```

`environment.yml` 仅建立 Python 3.12 和 pip 基础环境；完整 Python 依赖由 pyproject 安装。

## 字体与系统条件

本项目不分发系统字体。Windows 实测 Arial；Linux 实测 `/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf`。可使用 `SCIENTIFIC_FIGURE_FONT` 指向有使用权限的 TTF/OTF；中文等文字需选择实际覆盖相应字符的字体。具体字体路径与哈希会记录在工程中。

Linux 需要可用字体，例如发行版 `fonts-dejavu-core`；二进制 wheel 不可用时，pip 可能需要对应包的原生构建工具。项目未将 Rust/Skia 编译链设为默认安装方式。headless OpenCV 不要求桌面 GUI。

在 WSL 下，将**输出工程**放在 Linux 原生文件系统，例如 `~/figure-work`。本项目保留原子发布要求；Windows 盘的 `/mnt/c`、`/mnt/e` 挂载可能不支持所需 renameat2 行为，遇到拒绝时不要假装发布成功。

## 验证与构建

安装 dev 后运行：

```bash
python -I -m pytest -q
```

应用代码有些开发测试使用临时合成图；不需要 README 参考图来证明工程行为。Windows 部分符号链接测试可能因权限跳过。

```bash
python -I scripts/verify_v09_workflow.py --output work/workflow09
```

```bash
python -m pip wheel --no-deps --wheel-dir dist .
```

默认构建隔离可能联网安装 setuptools；`--no-build-isolation` 只适合已准备构建依赖的环境。

实际 0.9 验证使用既有依赖安装本地 wheel，两平台全部 74 个应用文件与 wheel 一致；未声称空环境全依赖离线安装或跨字体平台像素相同。原始记录见 [verification](../verification/README.md)。
