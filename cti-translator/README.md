# CTI Translator

Converts a raw threat intelligence report into a structured intelligence package.

## What it does

You give it a threat report as plain text. It sends the text to the Anthropic API and asks for a structured analysis. Then it prints five sections in the terminal:

- **Executive brief** — 3–5 sentences on business risk, written for non-technical leadership.
- **Technical brief** — TTPs, indicators, and attack flow for SOC analysts.
- **Action items** — what to do next, each marked high, medium, or low priority.
- **MITRE ATT&CK** — technique IDs and names that match the report.
- **Suggested detections** — Sigma-style detection rules in YAML.

## Why it's useful

Threat reports are long, and different people need different parts of them. Leadership needs the risk. Analysts need the technical detail and something to hunt with. This gets you a first draft of all of it from one report, so you review instead of starting from nothing.

The output comes from an LLM. Check the ATT&CK mappings and detection rules before you use them.

## Requirements

- Python 3
- An Anthropic API key
- `anthropic` and `rich` (see `requirements.txt`)

## How to run it

```bash
git clone https://github.com/roddyg01/public-projects.git
cd public-projects/cti-translator
pip install -r requirements.txt
export ANTHROPIC_API_KEY=your-key-here
```

The script reads the key from the `ANTHROPIC_API_KEY` environment variable. `.env.example` shows the variable name, but the script doesn't load `.env` files itself, so export the variable in your shell.

Pass a report as a file:

```bash
python main.py --file report.txt
```

Or pipe it in:

```bash
cat report.txt | python main.py
```

Run `python main.py` with no input and it waits for you to paste the report. Press Ctrl-D when you're done (Ctrl-Z on Windows).

## Example output

Five panels, always in this order. What's inside depends on the report.

```
──────────────── EXECUTIVE BRIEF ────────────────
  3–5 sentence summary for leadership

──────────────── TECHNICAL BRIEF ────────────────
  TTPs, indicators, attack flow

───────────────── ACTION ITEMS ──────────────────
  Priority    Action
  HIGH        ...
  MEDIUM      ...
  LOW         ...

───────────────── MITRE ATT&CK ──────────────────
  Technique ID      Name
  T1059.001         PowerShell

───────────── SUGGESTED DETECTIONS ──────────────
  Detection 1
    title: ...
    logsource: ...
    detection: ...
```
