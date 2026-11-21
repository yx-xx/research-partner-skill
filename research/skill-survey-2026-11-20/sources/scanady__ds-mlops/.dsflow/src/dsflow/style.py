"""`dsflow lint-style`: clear-writing heuristics for Markdown prose. All findings are warnings."""

from __future__ import annotations

import re
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path

from dsflow import frontmatter, markdown, repo

DEFAULT_PATHS = ("AGENTS.md", "README.md", "docs", "studies", ".agents/skills", ".dsflow/templates")
WORD_LIST = Path("docs/standards/words.toml")
SENTENCE_LIMIT = 30

_BE = r"(?:is|are|was|were|be|been|being)"
_IRREGULAR = (
    "written|given|made|done|shown|known|taken|seen|built|kept|set|run|held|found|chosen|sent|read"
)
_NOT_PARTICIPLES = {
    "need", "speed", "feed", "seed", "indeed", "proceed", "exceed", "succeed", "hundred",
    "weed", "breed", "bleed", "greed", "deed", "creed", "steed", "embed", "shed", "bred",
}  # fmt: skip
_ADVERBS = r"(?:\w+ly|not|never|also|then|always|already|still|only|often|usually)"
_PASSIVE = re.compile(
    rf"\b{_BE}\s+(?:{_ADVERBS}\s+)?(\w+)\b",
    re.IGNORECASE,
)
_ITEM = re.compile(r"^(\s*)(?:[-*+]|\d+[.)])\s+(?:\[[ xX]\]\s+)?")
_ABBREVIATIONS = ("e.g.", "i.e.", "etc.", "vs.", "approx.", "cf.")
_SENTENCE_END = re.compile(r"""([.!?]+["')\]]*)\s+(?=[^a-z\s])""")


@dataclass(frozen=True)
class StyleFinding:
    path: str
    line: int
    rule: str
    message: str

    def format(self) -> str:
        return f"WARN {self.path}:{self.line}: {self.rule}: {self.message}"


@dataclass
class Block:
    kind: str  # "list" or "text"
    start: int
    lines: list[tuple[int, str]]


def load_avoid(root: Path) -> dict[str, str]:
    path = root / WORD_LIST
    if not path.is_file():
        print(f"WARN {WORD_LIST.as_posix()}: file not found; the word rule is off", file=sys.stderr)
        return {}
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as exc:
        raise repo.ConfigError(f"{WORD_LIST.as_posix()} is not valid TOML: {exc}") from exc
    return {str(k): str(v) for k, v in data.get("avoid", {}).items()}


def _clean(line: str) -> str:
    """Remove inline code, link URLs, autolinks, bare URLs and inline HTML from one line."""
    line = re.sub(r"(`+)(?:(?!\1).)+?\1", "X", line)
    line = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", line)
    line = re.sub(r"!?\[([^\]]*)\]\[[^\]]*\]", r"\1", line)
    line = re.sub(r"<(?:https?://|mailto:)[^>]*>", "X", line)
    line = re.sub(r"https?://\S+", "X", line)
    line = re.sub(r"</?[A-Za-z][^>]*>", "", line)
    return line


def blocks_of(text: str) -> list[Block]:
    """Split Markdown into prose blocks. Skipped regions never reach the rules."""
    fm = frontmatter.parse(text)
    first = fm.end_line + 1 if fm else 1
    blocks: list[Block] = []
    current: Block | None = None
    in_comment = False

    def close() -> None:
        nonlocal current
        if current is not None and current.lines:
            blocks.append(current)
        current = None

    for number, raw, in_fence in markdown.iter_lines(text):
        if number < first:
            continue
        if in_fence:
            close()
            continue
        line = raw
        if in_comment:
            end = line.find("-->")
            if end == -1:
                close()
                continue
            in_comment = False
            line = line[end + 3 :]
        line = re.sub(r"<!--.*?-->", "", line)
        start = line.find("<!--")
        if start != -1:
            in_comment = True
            line = line[:start]
        line = re.sub(r"^(\s*>)+\s?", "", line)
        stripped = line.strip()
        if (
            not stripped
            or stripped.startswith(("|", "#"))
            or re.match(r"^\[[^\]]+\]:\s", stripped)
            or re.fullmatch(r"[-*_=\s]{3,}", stripped)
        ):
            close()
            continue
        item = _ITEM.match(line)
        if item:
            close()
            current = Block("list", number, [])
            line = line[item.end() :]
        elif current is None:
            current = Block("text", number, [])
        cleaned = _clean(line).strip()
        if cleaned:
            current.lines.append((number, cleaned))
    close()
    return blocks


def _join(block: Block) -> tuple[str, list[tuple[int, int]]]:
    """Join block lines with spaces. Return the text and `(offset, line)` pairs."""
    parts: list[str] = []
    marks: list[tuple[int, int]] = []
    offset = 0
    for number, text in block.lines:
        marks.append((offset, number))
        parts.append(text)
        offset += len(text) + 1
    return " ".join(parts), marks


def _line_at(marks: list[tuple[int, int]], offset: int) -> int:
    line = marks[0][1]
    for start, number in marks:
        if start <= offset:
            line = number
    return line


def _sentences(text: str) -> list[tuple[int, str]]:
    """Split `text` into `(offset, sentence)` pairs. Abbreviations do not end a sentence."""
    protected = text
    for abbreviation in _ABBREVIATIONS:
        protected = protected.replace(abbreviation, abbreviation.replace(".", "\0"))
    result: list[tuple[int, str]] = []
    start = 0
    for match in _SENTENCE_END.finditer(protected):
        end = match.end(1)
        result.append((start, protected[start:end].replace("\0", ".")))
        start = match.end()
    tail = protected[start:].strip()
    if tail:
        result.append((start, tail.replace("\0", ".")))
    return result


def _word_count(sentence: str) -> int:
    return sum(1 for token in sentence.split() if re.search(r"[A-Za-z0-9]", token))


def _avoid_patterns(avoid: dict[str, str]) -> list[tuple[str, str, re.Pattern[str]]]:
    patterns = []
    for word, replacement in avoid.items():
        body = r"\s+".join(re.escape(part) for part in word.split())
        patterns.append(
            (word, replacement, re.compile(rf"(?<![\w-]){body}(?![\w-])", re.IGNORECASE))
        )
    return patterns


def lint_text(
    text: str, shown: str, patterns: list[tuple[str, str, re.Pattern[str]]]
) -> list[StyleFinding]:
    findings: list[StyleFinding] = []
    for block in blocks_of(text):
        joined, marks = _join(block)
        sentences = _sentences(joined)
        for offset, sentence in sentences:
            count = _word_count(sentence)
            if count > SENTENCE_LIMIT:
                findings.append(
                    StyleFinding(
                        shown,
                        _line_at(marks, offset),
                        "sentence-length",
                        f"sentence has {count} words; the limit is {SENTENCE_LIMIT}",
                    )
                )
        for match in _PASSIVE.finditer(joined):
            word = match.group(1).lower()
            if not _is_participle(word):
                continue
            findings.append(
                StyleFinding(
                    shown,
                    _line_at(marks, match.start()),
                    "passive-voice",
                    f"possible passive voice: '{match.group(0)}'; use the active voice",
                )
            )
        for _word, replacement, pattern in patterns:
            for match in pattern.finditer(joined):
                advice = "delete it" if replacement == "(delete)" else f"use '{replacement}'"
                findings.append(
                    StyleFinding(
                        shown,
                        _line_at(marks, match.start()),
                        "word",
                        f"avoid '{match.group(0)}'; {advice}",
                    )
                )
    findings.sort(key=lambda f: (f.line, f.rule))
    return findings


def _is_participle(word: str) -> bool:
    if re.fullmatch(_IRREGULAR, word):
        return True
    return len(word) >= 4 and word.endswith("ed") and word not in _NOT_PARTICIPLES


def collect_files(root: Path, paths: list[str]) -> list[Path]:
    files: list[Path] = []
    for item in paths:
        path = Path(item)
        if not path.is_absolute() and not path.exists():
            path = root / item
        if path.is_dir():
            files.extend(sorted(path.rglob("*.md")))
        elif path.is_file():
            files.append(path)
    seen: set[Path] = set()
    unique: list[Path] = []
    for f in files:
        key = f.resolve()
        if key not in seen:
            seen.add(key)
            unique.append(f)
    return unique


def cmd_lint_style(root: Path, paths: list[str], *, strict: bool) -> int:
    avoid = load_avoid(root)
    patterns = _avoid_patterns(avoid)
    count = 0
    for path in collect_files(root, paths or list(DEFAULT_PATHS)):
        text = path.read_text(encoding="utf-8")
        for finding in lint_text(text, repo.rel(root, path), patterns):
            print(finding.format())
            count += 1
    if count:
        print(f"lint-style: {count} warning(s)")
    else:
        print("lint-style: no findings")
    return 1 if strict and count else 0
