# CTI Translator

Converts raw threat intelligence reports into structured intelligence packages for different audiences.

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env
# Add your Anthropic API key to .env
```

## Usage

```bash
python main.py
```

Select an audience (executive, SOC analyst, or threat hunter), paste a raw threat intel report, and CTI Translator produces a structured package tailored to that audience.

## Audiences

- **Executive** — high-level business risk summary, no technical jargon
- **SOC analyst** — actionable indicators, detection guidance, triage steps
- **Threat hunter** — TTPs, hunting hypotheses, MITRE ATT&CK mappings
