"""
Rendering for breach analysis: an ASCII timeline and summary reports.

Output is plain text with optional ANSI color, so it works in any terminal
and degrades cleanly when piped to a file.
"""

from __future__ import annotations

from .core import Breach, TimelineAnalysis


class _C:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RED = "\033[31m"
    YELLOW = "\033[33m"
    GREEN = "\033[32m"
    CYAN = "\033[36m"
    MAGENTA = "\033[35m"


_SEV_COLOR = {"HIGH": _C.RED, "MEDIUM": _C.YELLOW, "LOW": _C.GREEN}
_SEV_MARK = {"HIGH": "●", "MEDIUM": "◐", "LOW": "○"}


def _c(text: str, color: str, use_color: bool) -> str:
    return f"{color}{text}{_C.RESET}" if use_color else text


def _human_count(n: int) -> str:
    """Format a large integer as a compact human string."""
    if n >= 1_000_000_000:
        return f"{n / 1_000_000_000:.1f}B"
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}K"
    return str(n)


def render_timeline(
    analysis: TimelineAnalysis,
    use_color: bool = True,
    title: str = "Breach Exposure Timeline",
) -> str:
    """Render a year-by-year ASCII timeline with a bar per year."""
    lines: list[str] = []
    by_year = analysis.by_year()

    lines.append("")
    lines.append(_c("=" * 64, _C.DIM, use_color))
    lines.append("  " + _c(title, _C.BOLD, use_color))
    lines.append(_c("=" * 64, _C.DIM, use_color))

    if not by_year:
        lines.append("")
        lines.append(_c("  No dated breaches to display.", _C.DIM, use_color))
        lines.append(_c("=" * 64, _C.DIM, use_color))
        return "\n".join(lines)

    # Scale bars to the busiest year.
    max_count = max(len(b) for b in by_year.values())
    bar_width = 28

    lines.append("")
    for year, breaches in by_year.items():
        count = len(breaches)
        filled = max(1, round((count / max_count) * bar_width))
        bar = "█" * filled

        # Color the bar by the worst severity present that year.
        worst = "LOW"
        for b in breaches:
            if b.severity == "HIGH":
                worst = "HIGH"
                break
            if b.severity == "MEDIUM":
                worst = "MEDIUM"
        bar_colored = _c(bar, _SEV_COLOR.get(worst, _C.GREEN), use_color)

        lines.append(f"  {year}  {bar_colored} {count}")

    lines.append("")
    lines.append(_c("=" * 64, _C.DIM, use_color))
    return "\n".join(lines)


def render_summary(analysis: TimelineAnalysis, use_color: bool = True) -> str:
    """Render headline statistics and a severity breakdown."""
    lines: list[str] = []

    lines.append("")
    lines.append("  " + _c("SUMMARY", _C.BOLD, use_color))
    lines.append(_c("  " + "-" * 30, _C.DIM, use_color))
    lines.append(f"  Breaches analyzed   : {analysis.total}")
    lines.append(
        f"  Accounts exposed    : {_human_count(analysis.total_accounts_exposed)}"
    )

    sev = analysis.severity_breakdown()
    lines.append("")
    lines.append("  " + _c("SEVERITY", _C.BOLD, use_color))
    lines.append(_c("  " + "-" * 30, _C.DIM, use_color))
    for level in ("HIGH", "MEDIUM", "LOW"):
        mark = _SEV_MARK[level]
        colored = _c(f"{mark} {level:<7}", _SEV_COLOR[level], use_color)
        lines.append(f"  {colored} {sev[level]}")

    # Most common exposed data types.
    freq = analysis.data_class_frequency()[:8]
    if freq:
        lines.append("")
        lines.append("  " + _c("MOST EXPOSED DATA TYPES", _C.BOLD, use_color))
        lines.append(_c("  " + "-" * 30, _C.DIM, use_color))
        for data_class, count in freq:
            lines.append(f"  {count:>4}  {data_class}")

    return "\n".join(lines)


def render_account_detail(
    breaches: list[Breach], email: str, use_color: bool = True
) -> str:
    """Render the chronological list of breaches for a specific account."""
    lines: list[str] = []

    lines.append("")
    lines.append(_c("=" * 64, _C.DIM, use_color))
    header = f"  Exposure report for {email}"
    lines.append("  " + _c(header.strip(), _C.BOLD, use_color))
    lines.append(_c("=" * 64, _C.DIM, use_color))

    if not breaches:
        lines.append("")
        lines.append(
            _c("  No breaches found for this address. ", _C.GREEN, use_color)
            + "Good news."
        )
        lines.append(_c("=" * 64, _C.DIM, use_color))
        return "\n".join(lines)

    ordered = sorted(breaches, key=lambda b: b.breach_date or "0000-00-00")
    lines.append("")
    for b in ordered:
        mark = _SEV_MARK[b.severity]
        sev_c = _c(mark, _SEV_COLOR[b.severity], use_color)
        date = b.breach_date or "unknown date"
        lines.append(f"  {sev_c} {_c(date, _C.CYAN, use_color)}  {_c(b.title, _C.BOLD, use_color)}")
        if b.data_classes:
            shown = ", ".join(b.data_classes[:5])
            if len(b.data_classes) > 5:
                shown += f", +{len(b.data_classes) - 5} more"
            lines.append(_c(f"       exposed: {shown}", _C.DIM, use_color))

    lines.append("")
    lines.append(_c("=" * 64, _C.DIM, use_color))
    return "\n".join(lines)
