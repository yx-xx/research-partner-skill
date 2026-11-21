# Paper Easy Reader · 论文便捷阅读

给 Codex 一篇论文，把原文、中文意译和证据批注放在同一页。将鼠标移到一句译文上，就能看到对应的原句。读到一个结论时，可以沿着批注回到支撑它的图、表、公式或原文页段。生成的读本是单个 HTML 文件，保存后可离线打开。

## 安装与使用

在使用 Codex 的项目根目录运行以下命令，将此技能安装到该项目。

```sh
git clone https://github.com/YufanDu-bjtu/paper-easy-reader.git .agents/skills/paper-easy-reader
```

在该项目中打开新的 Codex 对话，附上你有权处理的论文 PDF，输入：

> 请用 $paper-easy-reader 精读这篇论文。按原文章节生成离线 HTML，保留双语逐句对照。请在关键结论旁标出支撑它的图、表或公式，并列出尚未核实的材料。

也可以提供全文网页、DOI、arXiv 链接或题名，或指定“只读第 3 节及其引用的图表”。只有摘要时，技能会报告全文获取状态。拿到完整原件后，可以要求补核缺项并保存新版。

## 读本里有什么

| 阅读时想做什么 | 在读本中怎么看 |
| --- | --- |
| 核对一句译文 | 悬停、键盘聚焦或触屏点选，让对应句组一起高亮。桌面并排显示三栏，小屏依次排列。 |
| 看懂研究方法 | 从双语目录进入原章节，或先看技术路线，了解输入数据、方法、对照和输出。 |
| 核查一条结论 | 批注给出原文位置，区分测量、推断与解读。图件可放大，公式用 MathML 显示并保留可复制的源码。 |
| 判断证据有多强 | 文末汇总核心主张、最强与最弱的证据。原图、附件或正式版本缺失时，会标明待补项。 |

## 试运行排版器

从仓库根目录执行下面两条命令即可试读。示例使用虚构的流量测量，只用于展示句组、批注和公式。排版和静态检查只依赖 Python 3.9 或以上版本的标准库。

```sh
python scripts/render_reader.py examples/flow.json reader.html
python scripts/check_reader.py reader.html
```

用浏览器打开生成的 `reader.html`。如输出文件已存在，排版器会另存为新版本，检查时请使用它实际返回的路径。

Codex 负责阅读、翻译和组织证据；排版器接收整理好的 JSON。需要自行准备材料时，可参考[字段说明和原件核对方法](references/reader-data.md)。可选的原件提取程序读取 PDF 时使用 PyMuPDF，读取 HTML/XML 时使用 lxml。已配置 Node.js、Playwright 和 Chromium 时，还可以运行 `node scripts/check_browser.cjs reader.html` 检查离线交互；译文、公式含义及图文对应关系需要回看原件。

## 许可

本项目的原创脚本、样式和文档采用 [MIT License](LICENSE)。随附的 Lora 和 IBM Plex 字体各自采用 SIL Open Font License 1.1，读本会内嵌相应声明。[Lora 字体许可](assets/lora.license) · [IBM Plex 字体许可](assets/plex.license)

论文正文、译文、图表和补充材料的使用与分享须遵循原作许可或权利人的授权。
