# breach-timeline

A command-line tool (`breachtl`) that turns Have I Been Pwned (HIBP) breach data into a timeline with severity ratings.

> **For lawful, ethical research only.** Only look up email addresses you own or are authorized to investigate. Landscape mode uses public, aggregate data. Account lookups involve personal data.

## What it does

- **Landscape mode** — pulls the full public HIBP breach catalog (no API key needed) and shows breaches per year, a severity breakdown, and the most exposed data types.
- **Account mode** — with an HIBP API key, lists the breaches one email address appears in, oldest first.
- **Filters** — limit to one year, or to breaches that exposed passwords.
- **Severity** — each breach gets a rating:
  - `HIGH` — passwords plus at least two other data types, or HIBP marks it sensitive
  - `MEDIUM` — passwords, financial data, SSNs, or security questions; or more than 50 million accounts
  - `LOW` — everything else
- **JSON output** and an **offline mode** that reads a saved catalog file.

## Why it's useful

Most breach checkers answer yes or no. This one shows when breaches happened and what leaked, so you can see patterns over time. Landscape mode is a quick way to see how the breach problem has changed year to year.

## Requirements

- Python 3.9+
- No third-party packages. It uses only the standard library.
- An HIBP API key, only for account mode. Searching a specific email is a paid HIBP feature.

## How to run it

```bash
git clone https://github.com/roddyg01/public-projects.git
cd public-projects/breach-timeline
```

Landscape view (no key):

```bash
python3 -m breachtl.cli --landscape
```

Offline, using the included sample of 10 breaches:

```bash
python3 -m breachtl.cli --landscape --from-file sample_catalog.json
```

One email address (needs a key):

```bash
export HIBP_API_KEY=your-key-here
python3 -m breachtl.cli --account you@example.com
```

| Flag | Description |
|------|-------------|
| `--landscape` | Analyze the full public breach catalog. |
| `--account EMAIL` | Analyze breaches for one address. Needs a key. |
| `--key KEY` | HIBP API key. Falls back to `HIBP_API_KEY`. |
| `--from-file PATH` | Read breach data from a saved JSON file. |
| `--year YEAR` | Only one calendar year. |
| `--exposes-passwords` | Only breaches that exposed passwords. |
| `--json` | Output JSON. |
| `--no-color` | Turn off colors. |

Run the tests:

```bash
python3 -m unittest discover -s tests -v
```

## Example output

From `--landscape --from-file sample_catalog.json`:

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

  MOST EXPOSED DATA TYPES
  ------------------------------
    10  Email addresses
     7  Passwords
     5  Names
     4  Usernames
     3  Geographic locations
     1  Password hints
     1  Social security numbers
     1  Credit cards
```

## License

MIT — see [LICENSE](LICENSE).
