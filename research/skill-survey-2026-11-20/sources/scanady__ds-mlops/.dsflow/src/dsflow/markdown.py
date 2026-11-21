"""Small Markdown helpers shared by the gate, the style linter and the doctor."""

from __future__ import annotations

import re
from collections.abc import Iterator

_FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})")


def iter_lines(text: str) -> Iterator[tuple[int, str, bool]]:
    """Yield `(line_number, line, in_fence)`. Fence delimiter lines count as in the fence."""
    fence: str | None = None
    for number, line in enumerate(text.split("\n"), start=1):
        match = _FENCE.match(line)
        if fence is None:
            if match:
                fence = match.group(1)
                yield number, line, True
                continue
            yield number, line, False
        else:
            yield number, line, True
            if match:
                marker = match.group(1)
                if (
                    marker[0] == fence[0]
                    and len(marker) >= len(fence)
                    and not line.strip()[len(marker) :].strip()
                ):
                    fence = None


def h2_headings(text: str, start_line: int = 1) -> list[str]:
    """Return the trimmed `## ` headings outside fences, from `start_line` on."""
    found: list[str] = []
    for number, line, in_fence in iter_lines(text):
        if number >= start_line and not in_fence and line.startswith("## "):
            found.append(line.strip())
    return found
