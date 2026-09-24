"""Shared display helpers for Day 3 labs (boxed tables, bullets).

Kept inside day3 so the day stays self-contained; other days do not import it.
"""

from __future__ import annotations

import textwrap


def render_table(
    headers: list[str],
    rows: list[list[str]],
    max_widths: list[int | None] | None = None,
    center: set[int] | None = None,
) -> str:
    """Unicode box table with per-column wrapping. No extra dependencies."""
    ncols = len(headers)
    max_widths = max_widths or [None] * ncols
    center = center or set()

    def wrap(text: str, width: int | None) -> list[str]:
        raw = str(text).splitlines() or [""]
        if width is None:
            return raw
        lines: list[str] = []
        for para in raw:
            if para.startswith("• "):
                lines.extend(textwrap.wrap(para, width, subsequent_indent="  ") or ["• "])
            else:
                lines.extend(textwrap.wrap(para, width) or [""])
        return lines or [""]

    wrapped = [[wrap(str(cell), max_widths[i]) for i, cell in enumerate(row)] for row in rows]
    widths = [len(header) for header in headers]
    for cells in wrapped:
        for i, lines in enumerate(cells):
            for line in lines:
                widths[i] = max(widths[i], len(line))

    def pad(text: str, i: int) -> str:
        return text.center(widths[i]) if i in center else text.ljust(widths[i])

    def row_line(cells_line: list[str]) -> str:
        return "│ " + " │ ".join(pad(cells_line[i], i) for i in range(ncols)) + " │"

    def bar(left: str, mid: str, right: str) -> str:
        return left + mid.join("─" * (width + 2) for width in widths) + right

    out = [bar("┌", "┬", "┐"), row_line(headers), bar("├", "┼", "┤")]
    for idx, cells in enumerate(wrapped):
        if idx:
            out.append(bar("├", "┼", "┤"))
        height = max(len(cell) for cell in cells)
        for row in range(height):
            out.append(
                row_line([cells[i][row] if row < len(cells[i]) else "" for i in range(ncols)])
            )
    out.append(bar("└", "┴", "┘"))
    return "\n".join(out)


def bullets(items: list[str]) -> str:
    cleaned = []
    for item in items:
        text = str(item).strip().lstrip("•- ").rstrip(".")
        if text:
            cleaned.append(f"• {text}")
    return "\n".join(cleaned) or "• —"
