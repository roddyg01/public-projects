"""
Core logic for fetching and analyzing breach data from Have I Been Pwned.

Two data sources are used:

  * The public ``/breaches`` endpoint, which lists every breach HIBP knows
    about. This requires no authentication and powers the landscape view.
  * The authenticated ``/breachedaccount/{email}`` endpoint, which lists the
    breaches a specific address appears in. This requires an HIBP API key.

The module is deliberately tolerant of being run offline: if no network or
key is available, callers can feed it a cached JSON file instead.
"""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

HIBP_BASE = "https://haveibeenpwned.com/api/v3"
USER_AGENT = "breach-timeline-tool"


class HIBPError(RuntimeError):
    """Raised when the HIBP API returns an error we can't recover from."""


@dataclass
class Breach:
    """A single breach record, normalized from the HIBP schema."""

    name: str
    title: str
    domain: str
    breach_date: str | None
    added_date: str | None
    pwn_count: int
    data_classes: list[str] = field(default_factory=list)
    is_sensitive: bool = False
    is_verified: bool = True
    description: str = ""

    @property
    def year(self) -> int | None:
        if not self.breach_date:
            return None
        try:
            return datetime.strptime(self.breach_date, "%Y-%m-%d").year
        except ValueError:
            return None

    @property
    def exposes_passwords(self) -> bool:
        return any("password" in dc.lower() for dc in self.data_classes)

    @property
    def severity(self) -> str:
        """
        A coarse severity heuristic.

        High   : passwords plus any other personal data, or a sensitive breach.
        Medium : passwords alone, or a large volume of personal data.
        Low    : email/username only.
        """
        sensitive_classes = {
            "passwords",
            "credit cards",
            "social security numbers",
            "bank account numbers",
            "historical passwords",
            "security questions and answers",
        }
        hit = {dc.lower() for dc in self.data_classes} & sensitive_classes
        if self.is_sensitive or (self.exposes_passwords and len(self.data_classes) > 2):
            return "HIGH"
        if hit or self.pwn_count > 50_000_000:
            return "MEDIUM"
        return "LOW"

    @classmethod
    def from_api(cls, raw: dict[str, Any]) -> "Breach":
        return cls(
            name=raw.get("Name", ""),
            title=raw.get("Title", raw.get("Name", "")),
            domain=raw.get("Domain", ""),
            breach_date=raw.get("BreachDate"),
            added_date=raw.get("AddedDate"),
            pwn_count=int(raw.get("PwnCount", 0)),
            data_classes=list(raw.get("DataClasses", [])),
            is_sensitive=bool(raw.get("IsSensitive", False)),
            is_verified=bool(raw.get("IsVerified", True)),
            description=raw.get("Description", ""),
        )


def _get(url: str, api_key: str | None = None, retries: int = 3) -> Any:
    """Perform a GET request against HIBP with basic rate-limit handling."""
    headers = {"user-agent": USER_AGENT}
    if api_key:
        headers["hibp-api-key"] = api_key

    request = urllib.request.Request(url, headers=headers)

    for attempt in range(retries):
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                body = response.read().decode("utf-8")
                return json.loads(body) if body else []
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                # For account lookups, 404 means "no breaches found" — not an error.
                return []
            if exc.code == 429:
                # Rate limited. HIBP asks clients to back off ~1.5s.
                time.sleep(2 * (attempt + 1))
                continue
            if exc.code == 401:
                raise HIBPError(
                    "HIBP rejected the API key (401). Check that it is valid "
                    "and passed via --key or the HIBP_API_KEY environment variable."
                ) from exc
            raise HIBPError(f"HIBP returned HTTP {exc.code}: {exc.reason}") from exc
        except urllib.error.URLError as exc:
            raise HIBPError(f"Network error contacting HIBP: {exc.reason}") from exc

    raise HIBPError("Exceeded retry budget contacting HIBP (rate limited).")


def fetch_all_breaches(api_key: str | None = None) -> list[Breach]:
    """Fetch the full public breach catalog. No key required."""
    raw = _get(f"{HIBP_BASE}/breaches", api_key=api_key)
    return [Breach.from_api(item) for item in raw]


def fetch_account_breaches(email: str, api_key: str) -> list[Breach]:
    """
    Fetch breaches for a specific email address. Requires a valid API key.

    Returns truncated records from the account endpoint, then enriches them
    against the full catalog so we get dates and data classes.
    """
    if not api_key:
        raise HIBPError("An API key is required to look up a specific account.")

    encoded = urllib.parse.quote(email)
    url = f"{HIBP_BASE}/breachedaccount/{encoded}?truncateResponse=false"
    raw = _get(url, api_key=api_key)
    return [Breach.from_api(item) for item in raw]


def load_breaches_from_file(path: str | Path) -> list[Breach]:
    """Load breach data from a cached JSON file (offline mode / testing)."""
    path = Path(path)
    data = json.loads(path.read_text(encoding="utf-8"))
    return [Breach.from_api(item) for item in data]


# --------------------------------------------------------------------------- #
# Analysis
# --------------------------------------------------------------------------- #


@dataclass
class TimelineAnalysis:
    """Aggregated statistics over a set of breaches."""

    breaches: list[Breach]

    @property
    def total(self) -> int:
        return len(self.breaches)

    @property
    def total_accounts_exposed(self) -> int:
        return sum(b.pwn_count for b in self.breaches)

    def by_year(self) -> dict[int, list[Breach]]:
        buckets: dict[int, list[Breach]] = defaultdict(list)
        for breach in self.breaches:
            year = breach.year
            if year is not None:
                buckets[year].append(breach)
        return dict(sorted(buckets.items()))

    def data_class_frequency(self) -> list[tuple[str, int]]:
        counter: Counter[str] = Counter()
        for breach in self.breaches:
            counter.update(breach.data_classes)
        return counter.most_common()

    def severity_breakdown(self) -> dict[str, int]:
        counter: Counter[str] = Counter(b.severity for b in self.breaches)
        return {level: counter.get(level, 0) for level in ("HIGH", "MEDIUM", "LOW")}

    def sorted_by_date(self) -> list[Breach]:
        return sorted(
            self.breaches,
            key=lambda b: b.breach_date or "0000-00-00",
        )
