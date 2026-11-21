"""Read back an exported reader; report its actual structure without claiming visual/source validation."""

import argparse
import base64
import json
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote


class Audit(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids = set()
        self.hrefs = []
        self.err = []
        self.trail = []
        self.pairs = {}
        self.counts = Counter()
        self.labels = {}
        self.obj = None
        self.ledger = {}

    def handle_starttag(self, tag, attrs):
        at = dict(attrs)
        classes = at.get("class", "").split()
        ident = at.get("id", "")
        if ident:
            if ident in self.ids:
                self.err.append("重复锚点 " + ident)
            self.ids.add(ident)
        if tag == "a":
            self.hrefs.append(at.get("href", ""))
        if tag in (
            "img",
            "script",
            "link",
            "iframe",
            "source",
            "video",
            "audio",
            "embed",
            "object",
        ):
            for key in ("src", "srcset", "href", "data"):
                if key not in at:
                    continue
                src = at[key]
                if tag == "img" and src.startswith("data:image/"):
                    try:
                        raw = base64.b64decode(src.split(",", 1)[1], validate=True)
                        if not raw:
                            raise ValueError("空图像")
                    except (IndexError, ValueError):
                        self.err.append("损坏的内嵌图像 " + ident)
                    self.counts["embedded_images"] += 1
                else:
                    self.err.append("非内嵌依赖 " + src[:90])
        if tag == "figure" and ident.startswith("obj-"):
            self.obj = ident
            self.ledger[ident] = {"label": "", "pending": False}
        if self.obj and "pending" in classes:
            self.ledger[self.obj]["pending"] = True
        if tag == "b" and self.obj and not self.ledger[self.obj]["label"]:
            self.labels["capture"] = self.obj
        if tag == "article" and "row" in classes:
            self.counts["paragraphs"] += 1
        if tag == "section" and "paper-section" in classes:
            self.counts["sections"] += 1
        if "formula-line" in classes:
            self.counts["equation_lines"] += 1
        if "equation-panel" in classes:
            self.counts["verified_equations"] += 1
        if tag == "table":
            self.counts["native_tables"] += 1
        if tag == "math":
            self.counts["mathml"] += 1
            if at.get("xmlns") != "http://www.w3.org/1998/Math/MathML":
                self.err.append("数学命名空间缺失")
        if tag == "merror":
            self.err.append("公式排版错误")
        if tag == "div" and ("en" in classes or "zh" in classes):
            self.trail.append("en" if "en" in classes else "zh")
        elif tag == "div":
            self.trail.append(None)
        if "data-pair" in at:
            lang = next((x for x in reversed(self.trail) if x), None)
            self.pairs.setdefault(at["data-pair"], Counter())[lang] += 1

    def handle_endtag(self, tag):
        if tag == "div" and self.trail:
            self.trail.pop()
        if tag == "figure":
            self.obj = None
        if tag == "b":
            self.labels.pop("capture", None)

    def handle_data(self, data):
        if "capture" in self.labels:
            self.ledger[self.labels["capture"]]["label"] += data


def main():
    a = argparse.ArgumentParser(description=__doc__)
    a.add_argument("reader", type=Path)
    args = a.parse_args()
    audit = Audit()
    audit.feed(args.reader.read_text("utf8"))
    audit.close()
    for href in audit.hrefs:
        u = urlsplit(href)
        if href.startswith("#") and unquote(u.fragment) not in audit.ids:
            audit.err.append("悬空锚点 " + href)
        if (
            u.path
            and not u.scheme
            and not u.netloc
            and not (args.reader.parent / unquote(u.path)).exists()
        ):
            audit.err.append("找不到合集页面 " + href)
    if any(p != Counter(en=1, zh=1) for p in audit.pairs.values()):
        audit.err.append("存在缺失或重复的句对")
    for name in ("sections", "paragraphs"):
        if not audit.counts[name]:
            audit.err.append("缺少 " + name)
    if not audit.pairs:
        audit.err.append("缺少句对")
    if "argument" not in audit.ids or "framework" not in audit.ids:
        audit.err.append("缺少技术路线或论证骨架")
    print(
        json.dumps(
            {
                "structure": dict(audit.counts),
                "sentence_groups": len(audit.pairs),
                "objects": audit.ledger,
                "errors": audit.err,
            },
            ensure_ascii=False,
            indent=1,
        )
    )
    raise SystemExit(bool(audit.err))


if __name__ == "__main__":
    main()
