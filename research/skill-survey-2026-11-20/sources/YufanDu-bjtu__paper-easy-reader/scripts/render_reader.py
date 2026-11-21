"""Render a source-checked, annotated paper manifest as a self-contained UTF-8 HTML file."""

import argparse
import base64
import html
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlsplit

ASSETS = Path(__file__).resolve().parent.parent / "assets"
MATH = "http://www.w3.org/1998/Math/MathML"
ET.register_namespace("", MATH)
MATH_TAGS = set(
    """math semantics annotation mrow mi mn mo mtext mspace ms mfrac msqrt mroot
mstyle merror mpadded mphantom mfenced menclose msub msup msubsup munder mover munderover
mmultiscripts mprescripts none mtable mlabeledtr mtr mtd maligngroup malignmark maction""".split()
)
MATH_ATTRS = set(
    """display mathvariant mathsize displaystyle scriptlevel stretchy symmetric
maxsize minsize fence separator separators form accent accentunder movablelimits largeop lspace rspace
linethickness bevelled columnalign rowalign columnspacing rowspacing columnspan rowspan columnlines
rowlines frame framespacing equalrows equalcolumns columnwidth width height depth voffset open close
notation subscriptshift superscriptshift lquote rquote encoding side align mathcolor""".split()
)
CATEGORIES = {
    "thesis": "核心论点",
    "term": "概念术语",
    "data": "实证证据",
    "caveat": "让步与局限",
    "method": "方法说明",
}
METRICS = ("中科院分区", "新锐分区", "影响因子", "年发文量")
KINDS = {"figure": "图", "table": "表", "equation": "式"}
STATUS = {"verified": "已核对", "pending": "待核验"}
esc = html.escape


def need(obj, key):
    value = obj.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"缺少文本字段 {key}")
    return value


def url(value, local=False):
    if any(ord(c) < 32 for c in value) or "\\" in value:
        raise ValueError(f"无效链接 {value!r}")
    parts = urlsplit(value)
    if parts.scheme.lower() in ("https", "http") and parts.hostname:
        return esc(value, quote=True)
    if (
        local
        and not parts.scheme
        and not parts.netloc
        and not value.startswith(("/", "#"))
        and parts.path
    ):
        return esc(value, quote=True)
    raise ValueError(f"无效来源或导航链接 {value!r}")


def link(href, label, local=False):
    return f'<a href="{url(href, local)}">{esc(label)}</a>'


def mathml(source, display):
    if "<!" in source or "<?" in source:
        raise ValueError("MathML 仅接受公式元素")
    m = ET.fromstring(source)
    if m.tag not in ("math", f"{{{MATH}}}math"):
        raise ValueError("公式根元素应为 math")
    for node in m.iter():
        tag = node.tag.removeprefix("{" + MATH + "}")
        if tag not in MATH_TAGS or tag == "merror":
            raise ValueError(f"请核对数学元素 {tag}")
        node.tag = "{" + MATH + "}" + tag
        for key in list(node.attrib):
            if key not in MATH_ATTRS:
                del node.attrib[key]
    m.set("display", display)
    return ET.tostring(m, encoding="unicode", short_empty_elements=False)


def rich(value, highlight=False):
    if isinstance(value, str):
        return esc(value)
    if not isinstance(value, list):
        raise ValueError("正文应为文本或文本与数学片段数组")
    output = []
    for token in value:
        if isinstance(token, str):
            output.append(esc(token))
        elif "ref" in token:
            anchor = "obj-" + safe_id(token["ref"])
            output.append(f'<a href="#{anchor}">{esc(need(token, "text"))}</a>')
        elif "mathml" in token:
            output.append(mathml(token["mathml"], "inline"))
        else:
            phrase = esc(need(token, "text"))
            role = token.get("role")
            if role and role not in CATEGORIES:
                raise ValueError(f"未知高亮类型 {role}")
            output.append(
                f'<mark class="{role}">{phrase}</mark>'
                if role and highlight
                else phrase
            )
    return "".join(output)


def safe_id(value):
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z][\w.-]*", value):
        raise ValueError(f"无效 ID {value!r}")
    return value


def font_css():
    rules = []
    for font, family, license_name in [
        ("Lora", "Lora", "lora"),
        ("Plex", "IBM Plex Sans", "plex"),
    ]:
        binary = base64.b64encode((ASSETS / (font + ".ttf")).read_bytes()).decode(
            "ascii"
        )
        license_text = (ASSETS / (license_name + ".license")).read_text("utf-8-sig")
        rules.append(
            f'/* {license_text.replace("*/", "* /")} */\n@font-face{{font-family:"{family}";src:url(data:font/ttf;base64,{binary}) format("truetype");font-weight:100 900;font-display:swap}}'
        )
    return "\n".join(rules)


def picture(base, item, fallback):
    raw = (base / need(item, "file")).read_bytes()
    if raw.startswith(b"\x89PNG\r\n\x1a\n"):
        kind = "png"
    elif raw.startswith(b"\xff\xd8\xff"):
        kind = "jpeg"
    elif raw[:4] == b"RIFF" and raw[8:12] == b"WEBP":
        kind = "webp"
    elif raw[:6] in (b"GIF87a", b"GIF89a"):
        kind = "gif"
    else:
        raise ValueError("请提供已核对的 PNG、JPEG、WebP 或 GIF 原图或原页")
    data = base64.b64encode(raw).decode("ascii")
    return f'<button type="button" class="open-image" aria-label="放大{esc(fallback)}"><img loading="lazy" decoding="async" src="data:image/{kind};base64,{data}" alt="{esc(item.get("alt") or fallback)}"></button>'


def table_html(rows):
    cells = []
    for row in rows:
        if not row:
            raise ValueError("表格存在空行")
        line = []
        for cell in row:
            c = cell if isinstance(cell, dict) else {"text": cell}
            tag = "th" if c.get("head") else "td"
            attrs = ""
            for key in ("rowspan", "colspan"):
                if key in c:
                    val = int(c[key])
                    if val < 1:
                        raise ValueError(key)
                    attrs += f' {key}="{val}"'
            line.append(f"<{tag}{attrs}>{rich(c['text'])}</{tag}>")
        cells.append("<tr>" + "".join(line) + "</tr>")
    return (
        '<div tabindex="0" class="table-scroll"><table>'
        + "".join(cells)
        + "</table></div>"
    )


def render_object(o, base, source_url):
    kind, status = o["kind"], o["status"]
    if kind not in KINDS or status not in STATUS:
        raise ValueError(f"原件类型或核验状态无效 {o.get('id')}")
    label, loc = need(o, "label"), need(o, "loc")
    ident = "obj-" + safe_id(o["id"])
    source = o.get("url") or source_url
    head = f'<div class="obj-head"><b>{esc(label)}</b><span>{esc(loc)}'
    if source:
        head += " · " + link(source, "来源")
    head += "</span></div>"
    content = []
    if status == "pending":
        content.append('<p class="pending">' + esc(need(o, "reason")) + "</p>")
        if kind in ("figure", "table"):
            if o.get("table"):
                content.append(table_html(o["table"]))
            content.extend(picture(base, img, label) for img in o.get("images", []))
    elif kind == "equation":
        lines = o.get("lines") or [need(o, "mathml")]
        for s in lines:
            content.append(
                '<div class="formula-line" tabindex="0">'
                + mathml(s, "block")
                + "</div>"
            )
        code = o.get("tex") or "\n".join(lines)
        fmt = "LaTeX" if o.get("tex") else "MathML"
        content.append(
            f'<details class="tex-source"><summary>查看 {fmt} 源码</summary><pre>{esc(code)}</pre></details>'
        )
    else:
        if o.get("table"):
            content.append(table_html(o["table"]))
        content.extend(picture(base, img, label) for img in o.get("images", []))
        if not content:
            raise ValueError(f"{label} 已标为核对，却无图像或表格内容")
    for key, lang in (("caption_en", "en"), ("caption_zh", "zh"), ("note", "zh")):
        if o.get(key):
            content.append(f'<p class="caption" lang="{lang}">{rich(o[key])}</p>')
    cls = "equation-panel" if kind == "equation" and status == "verified" else "object"
    return f'<figure id="{ident}" class="{cls}">{head}{"".join(content)}</figure>'


def paragraph(p, index, original="en"):
    en_label, zh_label = (
        ("英文译文", "中文原文") if original == "zh" else ("英文原文", "中文意译")
    )
    sentences = p["pairs"]
    if not sentences or not p.get("notes"):
        raise ValueError("每一正文段需有句对和中文批注")
    en, zh = [], []
    for i, pair in enumerate(sentences, 1):
        for field, target in (("en", en), ("zh", zh)):
            s = rich(pair[field], field == original)
            if not s.strip():
                raise ValueError(f"空句对 {index}.{i}")
            target.append(f'<span tabindex="0" data-pair="{index}-{i}">{s}</span>')
    annotations = []
    for n in p["notes"]:
        annotations.append(
            f'<div class="annotation"><strong>{esc(need(n, "label"))}</strong><p>{rich(n["text"])}</p></div>'
        )
    return (
        f'<article class="row" id="para-{index}"><div class="loc">{esc(need(p, "loc"))}</div>'
        f'<div class="en" lang="en"><span class="mobile-label">{en_label}</span>{" ".join(en)}</div>'
        f'<div class="zh"><span class="mobile-label">{zh_label}</span>{"".join(zh)}</div>'
        f'<aside class="notes">{"".join(annotations)}</aside></article>'
    )


def header(m):
    authors, affiliations = m["authors"], m["affiliations"]
    if not authors:
        raise ValueError("请填写作者或原文署名状态")
    marks = {str(a["id"]) for a in affiliations}
    if len(marks) != len(affiliations):
        raise ValueError("单位编号重复")
    names = []
    for a in authors:
        refs = [str(v) for v in a.get("aff", [])]
        if not set(refs) <= marks:
            raise ValueError("作者单位编号无对应单位")
        sup = f"<sup>{esc(','.join(refs))}</sup>" if refs else ""
        names.append(esc(need(a, "name")) + sup)
    institution = "　".join(
        f"<sup>{esc(str(a['id']))}</sup> {esc(need(a, 'name'))}" for a in affiliations
    ) or esc(m.get("affiliation_status", "单位待核验"))
    metrics = {v["name"]: v for v in m.get("metrics", [])}
    metric_html = []
    for key in METRICS:
        item = metrics.get(key, {})
        value = esc(item.get("value", "待核验"))
        if item.get("url"):
            value += " · " + link(item["url"], need(item, "basis"))
        elif item.get("basis"):
            value += " · " + esc(item["basis"])
        elif item.get("value") and item["value"] not in ("待核验", "不适用"):
            raise ValueError(f"{key} 需注明版次、统计口径和依据")
        metric_html.append(f"<div><dt>{key}</dt><dd>{value}</dd></div>")
    return (
        f'<header><p class="journal">{esc(need(m, "journal"))}　{esc(need(m, "date"))}</p>'
        f'<h1 lang="en">{esc(need(m, "title_en"))}</h1><p class="title-zh">{esc(need(m, "title_zh"))}</p>'
        f'<p class="authors">{" · ".join(names)}</p><p class="affiliations">{institution}</p>'
        f'<dl class="metrics">{"".join(metric_html)}</dl></header>'
    )


def framework_html(steps):
    stages = []
    levels = {}
    lookup = {}
    branched = any("from" in step for step in steps)
    for i, step in enumerate(steps):
        key = safe_id(step.get("id", f"step-{i + 1}"))
        parents = (
            step.get("from", [])
            if branched
            else ([next(reversed(levels))] if i else [])
        )
        if (
            key in levels
            or not isinstance(parents, list)
            or any(p not in levels for p in parents)
        ):
            raise ValueError("技术路线的节点 ID 需唯一，前驱节点须先列出")
        level = max((levels[p] for p in parents), default=-1) + 1
        if len(stages) <= level:
            stages.append([])
        levels[key] = level
        lookup[key] = need(step, "title")
        ancestry = "，".join(lookup[p] for p in parents)
        stages[level].append(
            f'<li class="flow-node" id="flow-{key}" data-from="{esc(" ".join(parents))}"><b>{esc(lookup[key])}</b><p>{rich(step["text"])}</p><span class="sr-only">{esc("依据：" + ancestry) if ancestry else ""}</span></li>'
        )
    columns = "".join(
        '<ul class="stage">' + "".join(nodes) + "</ul>" for nodes in stages
    )
    return f'<section id="framework"><h2>技术路线</h2><div class="diagram"><svg aria-hidden="true" class="connect"><defs><marker id="arrowend" markerWidth="5" markerHeight="5" refX="4.6" refY="2.5" orient="auto"><path d="M0 0L5 2.5L0 5Z" fill="#65816a"></path></marker></defs></svg><div class="flow-stages">{columns}</div></div></section>'


def render(data, base):
    source = data["source"]
    original = data["meta"].get("original_language", "en")
    if original not in ("en", "zh"):
        raise ValueError("本读本支持英中双语，请明确原文语言")
    en_label, zh_label = (
        ("英文译文", "中文原文") if original == "zh" else ("英文原文", "中文意译")
    )
    scope_name = source.get("scope")
    argument_heading = {
        "full": "全文论证结构",
        "excerpt": "节选论证结构",
        None: "论证结构",
    }[scope_name]
    claim_heading = "本节主张" if scope_name == "excerpt" else "作者核心主张"

    source_url = source.get("url")
    doi = source.get("doi")
    doi_url = "https://doi.org/" + doi if doi else ""
    sources = []
    if doi_url:
        sources.append(link(doi_url, "DOI · " + doi))
    if source_url and source_url != doi_url:
        sources.append(link(source_url, "原文入口"))
    for href_value, caption in (
        (data.get("home"), "返回周报列表"),
        (data.get("issue"), "本期周报"),
    ):
        if href_value:
            sources.append(link(href_value, caption, True))
    version = esc(need(source, "version"))
    scope = esc(need(source, "coverage"))
    status = ""
    if source.get("formal_pdf") == "pending":
        status = '<strong class="pending">待补正式 PDF</strong> · '
    elif source.get("formal_pdf") not in ("verified", "preprint", "not-applicable"):
        raise ValueError("请注明正式 PDF 的状态")
    if source.get("formal_pdf") == "preprint":
        status = "<strong>预印本</strong> · "
    version_box = f'<section class="source"><h2>阅读版本与来源</h2><p>{status}{version}</p><p>{scope}</p><p>{"　".join(sources)}</p></section>'
    objects = {}
    for item in data["objects"]:
        key = safe_id(item["id"])
        if key in objects:
            raise ValueError(f"重复原件 {key}")
        objects[key] = item
    flow = data["framework"]
    if not flow:
        raise ValueError("缺少论文技术路线")
    framework = framework_html(flow)
    toc = ['<a href="#framework">技术路线</a>']
    sections = []
    used = set()
    ids = set()
    index = 0
    if not data["sections"]:
        raise ValueError("缺少论文章节")
    for sec in data["sections"]:
        key = safe_id(sec["id"])
        if key in ids:
            raise ValueError(f"重复章节 {key}")
        ids.add(key)
        level = int(sec.get("level", 1))
        if not 1 <= level <= 6:
            raise ValueError("目录层级需为 1–6")
        en, zh = esc(need(sec, "en")), esc(need(sec, "zh"))
        num = esc(str(sec.get("number", "")))
        if sec.get("editorial") and not num:
            raise ValueError("请填写阅读序号")
        number = (
            f"<small>{'阅读序号 ' if sec.get('editorial') else ''}{num}</small>"
            if num
            else ""
        )
        toc.append(
            f'<a class="toc-link" style="--level:{level}" href="#sec-{key}">{number}{zh}<span lang="en">{en}</span></a>'
        )
        tag = "h" + str(min(level + 1, 6))
        blocks = [
            f'<{tag} class="sec-title">{number}{zh}<span lang="en">{en}</span></{tag}>'
        ]
        for p in sec["blocks"]:
            if "object" in p:
                obj = p["object"]
                if obj in used or obj not in objects:
                    raise ValueError(f"原件位置重复或未登记 {obj}")
                used.add(obj)
                blocks.append(render_object(objects[obj], base, source_url or doi_url))
            else:
                index += 1
                blocks.append(paragraph(p, index, original))
        sections.append(
            f'<section class="paper-section" id="sec-{key}">{"".join(blocks)}</section>'
        )
    if used != set(objects):
        raise ValueError(
            "有原件未放入正文或附件：" + ", ".join(sorted(set(objects) - used))
        )
    if index == 0:
        raise ValueError("缺少双语正文")
    if objects:
        items = "".join(
            f'<a href="#obj-{key}">{esc(o["label"])}{" · 待核" if o["status"] == "pending" else ""}</a>'
            for key, o in objects.items()
        )
        toc.append(
            f'<details><summary>图表与公式索引</summary><div class="object-links">{items}</div></details>'
        )
    conclusion = data["argument"]
    lineage = ""
    if data.get("prior"):
        rows = []
        for item in data["prior"]:
            detail = rich(item["comparison"])
            title = (
                link(item["url"], need(item, "title"))
                if item.get("url")
                else esc(need(item, "title"))
            )
            rows.append(
                f"<li><b>{title}</b> · {esc(need(item, 'status'))}<p>{detail}</p></li>"
            )
        lineage = (
            '<section id="lineage"><h2>作者与前序研究</h2><ul>'
            + "".join(rows)
            + "</ul></section>"
        )
        toc.append('<a href="#lineage">作者与前序研究</a>')
    toc.append(f'<a href="#argument">{argument_heading}</a>')
    claim = rich(conclusion["claim"])
    chain = "".join(f"<li>{rich(x)}</li>" for x in conclusion["chain"])
    if not chain:
        raise ValueError("缺少论证链")
    argument = f'<section id="argument"><h2>{argument_heading}</h2><ol>{chain}</ol><h3>{claim_heading}</h3><p>{claim}</p><h3>论证最强处</h3><p>{rich(conclusion["strong"])}</p><h3>论证最弱处</h3><p>{rich(conclusion["weak"])}</p></section>'
    legend = "".join(
        f'<span><i class="{c}"></i>{v}</span>' for c, v in CATEGORIES.items()
    )
    style = font_css() + (ASSETS / "reader.css").read_text("utf8")
    script = (
        (ASSETS / "reader.js").read_text("utf8")
        + "\n"
        + (ASSETS / "math-fit.js").read_text("utf8")
    )
    nav = (
        "　".join(sources[-int(bool(data.get("home")) + bool(data.get("issue"))) :])
        if data.get("home") or data.get("issue")
        else ""
    )
    return f"""<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(data["meta"]["title_zh"])}</title><style>{style}</style></head><body>
<div class="mobile-bar"><button id="menu" aria-expanded="false" aria-controls="toc">章节目录</button>{nav}</div><div class="layout"><aside id="toc"><div class="toc-nav">{nav}</div><h2>论文章节目录</h2><nav>{"".join(toc)}</nav></aside>
<main>{header(data["meta"])}{version_box}<div class="legend">{legend}</div>{framework}<div class="column-head"><span>{en_label}</span><span>{zh_label}</span><span>精读批注</span></div>{"".join(sections)}{lineage}{argument}<footer>{nav}　<a href="#top" id="back-top">返回页首</a></footer></main></div>
<dialog id="zoom" aria-labelledby="zoom-title"><div class="dialog-bar"><b id="zoom-title">原图</b><button id="size">原始尺寸</button><button id="close">关闭</button></div><div class="zoom-pan" tabindex="0"><img alt=""></div></dialog><script>{script}</script></body></html>""".replace(
        "<body>", '<body id="top">', 1
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    data = json.loads(args.manifest.read_text("utf-8-sig"))
    result = render(data, args.manifest.resolve().parent).encode("utf8")
    dest = args.output.resolve()
    if dest.suffix.lower() != ".html":
        parser.error("输出文件应使用 .html")
    dest.parent.mkdir(parents=True, exist_ok=True)
    candidate = dest
    version = 1
    while True:
        try:
            f = candidate.open("xb")
        except FileExistsError:
            version += 1
            candidate = dest.with_name(f"{dest.stem}_v{version}{dest.suffix}")
            continue
        try:
            with f:
                f.write(result)
        except BaseException:
            candidate.unlink(missing_ok=True)
            raise
        break
    print(candidate)


if __name__ == "__main__":
    try:
        main()
    except (KeyError, ValueError, OSError, ET.ParseError) as error:
        sys.exit(f"生成失败：{error}")
