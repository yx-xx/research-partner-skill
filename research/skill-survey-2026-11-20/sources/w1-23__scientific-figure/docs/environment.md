# Anaconda 开发环境

本项目使用 Anaconda 管理独立环境。

- 项目环境名称：`ScientificFigure_skill`
- 用户指定的显示名称：`ScientificFigure skill`
- 命名说明：Conda 环境名不允许空格，以 `_` 替代。
- 本机 Anaconda：`E:\anaconda`
- 本机环境位置：`E:\anaconda\envs\ScientificFigure_skill`
- Python 版本线：3.12（本机已验证版本：3.12.16）
- pip：26.2.2（已验证来自本环境的 `Lib\site-packages`）
- Python 解释器：`E:\anaconda\envs\ScientificFigure_skill\python.exe`
- 初始依赖：Python、pip。
- 当前最小原型已安装：Pillow、NumPy、OpenCV-headless、FontTools、jsonschema、resvg-py 与 pytest，以及本项目的 editable 安装；确切版本见项目根目录 `requirements-win-py312.lock.txt`。
- OCR、深度分割及 GPU 模型依赖尚未安装。
- 创建与验证日期：2026-11-17；已使用 `conda run` 验证解释器、环境路径和 pip。

0.6实际验证（2026-11-18）：Windows专用Conda的CPU链路通过；wheel另装到项目outputs下的venv，应用模块来自该venv的site-packages，第三方依赖继承专用Conda。WSL可见Ubuntu-24.04/Python3.12.3，但缺Pillow/NumPy/OpenCV/FontTools/resvg_py，未执行Linux运行验收；没有安装系统依赖或启动服务。详细记录见 [0.6交付](delivery-0.6.0.md)。

## 0.7 实际安装验证（2026-11-18）

新增可选构造依赖`skia-pathops==0.9.2`，核心源码、wheel及专用Conda editable metadata均为0.7.0。Windows另建`.venv-wheel07`安装应用wheel，第三方依赖继承Conda，不称为空环境离线安装。

Linux在WSL Ubuntu24.04/Python3.12.3的项目级`.venv-linux07`独立安装全部运行依赖与同一应用wheel，实际运行新旧文件工作流。缺ensurepip时，仅在venv内从PyPI摘要核验的pip wheel准备；未修改系统Python。Linux使用DejaVu Sans，Windows使用Arial，字体SHA分别记录，未复制系统字体。

Linux在`/mnt/e`的DrvFS上evidence原子发布失败（renameat2 RENAME_NOREPLACE，errno22）；随后在原生Linux临时目录运行全链成功并保存结果。请在支持该原子操作的Linux原生文件系统下输出，不静默降级成可能覆盖目标的重命名。安装需网络，已安装后的验证工作流无需网络；未准备全依赖离线wheelhouse或容器镜像。详情见[0.7交付](delivery-0.7.0.md)。

安装开发与构造工具：

```bash
python -m pip install -e ".[dev,construction]"
```

## 激活

在已初始化 Conda 的终端或 Anaconda Prompt 中运行：

```bash
conda activate ScientificFigure_skill
```

## 不激活直接运行

适合自动化脚本与 Agent 调用：

```bash
conda run -n ScientificFigure_skill python --version
```

安装 Python 包时确保指向本项目环境：

```bash
conda run -n ScientificFigure_skill python -m pip install <package>
```

## 在其他机器重建基础环境

在项目根目录运行：

```bash
conda env create --file environment.yml
```

`environment.yml` 仅声明基础环境需求，使用目标机器的 Conda channel 配置；不是完整的跨平台依赖锁文件。后续引擎依赖与可选后端需另行锁定。CPU/GPU 后端选择属于引擎配置，基础环境建立并不代表已安装 CUDA 或模型权重。
