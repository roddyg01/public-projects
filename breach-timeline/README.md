# breachtl

A command-line tool that turns Have I Been Pwned breach data into a timeline and exposure analysis. It works two ways: it can map the entire public breach landscape with no API key, or — with a key — show you the chronological exposure history of a specific email address.

Most breach checkers answer a yes/no question: *has this address been pwned?* That's useful, but it throws away the interesting part. `breachtl` keeps the dimension that actually tells a story — **time**. When did the exposures happen? What kind of data leaked, and when did that shift from "just email addresses" to "passwords and financial data"? Is exposure clustered in a few bad years or spread evenly? A timeline answers questions a count cannot.

## What it does

- **Landscape mode** — analyzes the full public HIBP breach catalog (no key required) and renders a year-by-year timeline with severity coloring, a severity breakdown, and the most commonly exposed data types.
- **Account mode** — with an HIBP API key, pulls the breaches a specific address appears in and renders a chronological, severity-rated exposure report.
- **Filtering** — narrow any analysis to a single year, or to only breaches that exposed passwords.
- **Severity scoring** — each breach is rated HIGH / MEDIUM / LOW based on what was actually exposed (passwords plus personal data and financial/SSN leaks rank highest; email-only leaks rank lowest).
- **JSON output** — structured output for piping into other tools.
- **Offline mode** — point it at a cached catalog file and it runs with no network at all.

## A note on the HIBP API

Have I Been Pwned changed its API model some time ago: **searching a specific email address requires a paid subscription key** (it's intentionally priced around the cost of a coffee to keep it accessible while preventing abuse). There is no free email-search endpoint.

This tool is built around that reality rather than pretending otherwise:

- The **landscape mode needs no key** because the breach catalog itself is a free, unauthenticated endpoint. You get a fully functional tool out of the box.
- **Account mode requires your own key**, passed via `--key` or the `HIBP_API_KEY` environment variable. HIBP also offers a free *test* key that works against their integration test domain if you want to verify the account flow without a subscription.

## Installation

```bash
git clone https://github.com/YOUR_USERNAME/breach-timeline.git
cd breach-timeline
```

It uses only the Python standard library — there are no dependencies to install.

## Usage

**Map the whole breach landscape** (no key needed):

```bash
python3 -m breachtl.cli --landscape
```

```
================================================================
  Breach Exposure Timeline
================================================================

  2008  █████████ 1
  2012  ███████████████████ 2
  2013  ███████████████████ 2
  2017  █████████ 1
  2019  ████████████████████████████ 3
  2021  █████████ 1

================================================================

  SUMMARY
  ------------------------------
  Breaches analyzed   : 10
  Accounts exposed    : 5.5B

  SEVERITY
  ------------------------------
  ● HIGH    5
  ◐ MEDIUM  5
  ○ LOW     0
```

**Look up a specific address** (requires a key):

```bash
python3 -m breachtl.cli --account you@example.com --key YOUR_HIBP_KEY
```

Or set the key once in your environment:

```bash
export HIBP_API_KEY=your_key_here
python3 -m breachtl.cli --account you@example.com
```

**Filter to a single year:**

```bash
python3 -m breachtl.cli --landscape --year 2019
```

**Only breaches that leaked passwords:**

```bash
python3 -m breachtl.cli --landscape --exposes-passwords
```

**JSON output:**

```bash
python3 -m breachtl.cli --landscape --json
```

**Run offline from a cached catalog** (a sample is included):

```bash
python3 -m breachtl.cli --landscape --from-file sample_catalog.json
```

### Options

| Flag | Description |
|------|-------------|
| `--landscape` | Analyze the full public breach catalog (no key). |
| `--account EMAIL` | Analyze breaches for one address (needs `--key`). |
| `--key KEY` | HIBP API key (or set `HIBP_API_KEY`). |
| `--from-file PATH` | Load breach data from a cached JSON file. |
| `--year YEAR` | Restrict to a single calendar year. |
| `--exposes-passwords` | Only include breaches that exposed passwords. |
| `--json` | Output JSON instead of the rendered report. |
| `--no-color` | Disable ANSI colors. |

## How it compares

Plenty of tools wrap the HIBP API, and the official site already tells you what you need for a single lookup. `breachtl` is narrower and more specific: it exists to make the **temporal and categorical shape** of breach data visible. The landscape timeline is something the basic checkers don't give you at all — it's a view of how the breach problem has evolved year over year, which is genuinely useful for understanding the threat landscape rather than just auditing one address.

It's not trying to be a full threat-intelligence platform. It does one thing: take breach data and show you its shape over time.

## Responsible use

Only look up email addresses you own or are explicitly authorized to investigate. The landscape mode uses only public, aggregate data. Account lookups touch personal data and should be treated accordingly.

## Running the tests

```bash
python3 -m unittest discover -s tests -v
```

## License

MIT — see [LICENSE](LICENSE).
