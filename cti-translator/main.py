import argparse
import json
import os
import sys

from anthropic import Anthropic
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
from rich.table import Table
from rich.text import Text

SYSTEM_PROMPT = """You are a senior threat intelligence analyst. Analyze the provided raw threat intelligence text and return a single JSON object with exactly these keys:

- "executive_brief": string, 3-5 sentences summarizing the threat in plain language for non-technical leadership. Focus on business risk and impact.
- "technical_brief": string, detailed technical analysis for SOC analysts. Include TTPs, indicators, attack flow, and relevant context.
- "action_items": array of objects with "priority" ("high", "medium", or "low") and "action" (string describing what to do).
- "mitre_attack": array of objects with "id" (ATT&CK technique ID, e.g. "T1059.001") and "name" (technique name).
- "suggested_detections": array of strings, each a Sigma-style detection rule in YAML format.

Return only valid JSON. No markdown fences, no explanation outside the JSON object."""


def analyze(report: str, client: Anthropic) -> dict:
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": f"Analyze this threat intelligence report:\n\n{report}"}],
    )
    raw = response.content[0].text.strip()
    # Strip markdown fences if the model wraps the response anyway
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[-1]
        raw = raw.rsplit("```", 1)[0]
    return json.loads(raw)


def render(result: dict, console: Console) -> None:
    console.print()

    # Executive Brief
    console.print(Rule("[bold white]EXECUTIVE BRIEF[/bold white]", style="cyan"))
    console.print(Panel(result["executive_brief"], border_style="cyan", padding=(1, 2)))

    # Technical Brief
    console.print(Rule("[bold white]TECHNICAL BRIEF[/bold white]", style="blue"))
    console.print(Panel(result["technical_brief"], border_style="blue", padding=(1, 2)))

    # Action Items
    console.print(Rule("[bold white]ACTION ITEMS[/bold white]", style="yellow"))
    priority_color = {"high": "red", "medium": "yellow", "low": "green"}
    table = Table(show_header=True, header_style="bold", box=None, padding=(0, 2))
    table.add_column("Priority", width=10)
    table.add_column("Action")
    for item in result["action_items"]:
        p = item["priority"].lower()
        color = priority_color.get(p, "white")
        table.add_row(Text(p.upper(), style=f"bold {color}"), item["action"])
    console.print(Panel(table, border_style="yellow", padding=(1, 1)))

    # MITRE ATT&CK
    console.print(Rule("[bold white]MITRE ATT&CK[/bold white]", style="magenta"))
    att_table = Table(show_header=True, header_style="bold", box=None, padding=(0, 2))
    att_table.add_column("Technique ID", width=16)
    att_table.add_column("Name")
    for t in result["mitre_attack"]:
        att_table.add_row(Text(t["id"], style="bold magenta"), t["name"])
    console.print(Panel(att_table, border_style="magenta", padding=(1, 1)))

    # Suggested Detections
    console.print(Rule("[bold white]SUGGESTED DETECTIONS[/bold white]", style="green"))
    for i, rule in enumerate(result["suggested_detections"], 1):
        console.print(Panel(rule.strip(), title=f"[bold green]Detection {i}[/bold green]",
                            border_style="green", padding=(1, 2)))

    console.print()


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="cti-translator",
        description="Converts raw threat intelligence reports into structured intelligence packages.",
    )
    parser.add_argument("--file", "-f", metavar="PATH", help="Path to a text file containing the raw report")
    args = parser.parse_args()

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY environment variable is not set.", file=sys.stderr)
        sys.exit(1)

    if args.file:
        try:
            with open(args.file) as fh:
                report = fh.read().strip()
        except OSError as e:
            print(f"Error reading file: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        if sys.stdin.isatty():
            print("Reading from stdin — paste report, then press Ctrl-D (or Ctrl-Z on Windows):", file=sys.stderr)
        report = sys.stdin.read().strip()

    if not report:
        print("Error: no report provided.", file=sys.stderr)
        sys.exit(1)

    console = Console()
    console.print(Panel("[bold cyan]CTI Translator[/bold cyan]",
                        subtitle="converting threat intel...", border_style="cyan"))

    client = Anthropic(api_key=api_key)

    try:
        result = analyze(report, client)
    except json.JSONDecodeError as e:
        console.print(f"[red]Failed to parse model response as JSON: {e}[/red]")
        sys.exit(1)

    render(result, console)


if __name__ == "__main__":
    main()
