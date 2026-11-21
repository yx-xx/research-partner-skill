"""Flat YAML front matter: read and write while keeping the rest of the file unchanged."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FrontMatter:
    data: dict[str, str]
    end_line: int  # 1-based line number of the closing `---`


def _parse_value(raw: str) -> str:
    raw = raw.strip()
    if raw.startswith('"'):
        out: list[str] = []
        i = 1
        while i < len(raw):
            ch = raw[i]
            if ch == "\\" and i + 1 < len(raw):
                out.append(raw[i + 1])
                i += 2
                continue
            if ch == '"':
                break
            out.append(ch)
            i += 1
        return "".join(out)
    if raw.startswith("'"):
        end = raw.find("'", 1)
        return raw[1:end] if end != -1 else raw[1:]
    comment = raw.find(" #")
    return raw[:comment].strip() if comment != -1 else raw


def quote(value: str) -> str:
    """Return `value` as a double-quoted YAML string."""
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def _closing_index(lines: list[str]) -> int | None:
    if not lines or lines[0].strip() != "---":
        return None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return i
    return None


def parse(text: str) -> FrontMatter | None:
    """Return the front matter of `text`, or None when the file has none."""
    lines = text.split("\n")
    end = _closing_index(lines)
    if end is None:
        return None
    data: dict[str, str] = {}
    for line in lines[1:end]:
        if not line.strip() or line[0] in " \t#" or ":" not in line:
            continue
        key, _, value = line.partition(":")
        data[key.strip()] = _parse_value(value)
    return FrontMatter(data=data, end_line=end + 1)


def set_fields(text: str, updates: dict[str, str]) -> str:
    """Return `text` with the given front matter keys set to quoted values."""
    lines = text.split("\n")
    end = _closing_index(lines)
    if end is None:
        raise ValueError("no front matter")
    pending = dict(updates)
    for i in range(1, end):
        line = lines[i]
        if not line.strip() or line[0] in " \t#" or ":" not in line:
            continue
        key = line.partition(":")[0].strip()
        if key in pending:
            lines[i] = f"{key}: {quote(pending.pop(key))}"
    extra = [f"{k}: {quote(v)}" for k, v in pending.items()]
    lines[end:end] = extra
    return "\n".join(lines)
