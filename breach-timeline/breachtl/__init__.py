"""
breachtl - Breach exposure timeline and analysis built on Have I Been Pwned data.
"""

from .core import (
    Breach,
    HIBPError,
    TimelineAnalysis,
    fetch_account_breaches,
    fetch_all_breaches,
    load_breaches_from_file,
)

__version__ = "0.1.0"
__all__ = [
    "Breach",
    "TimelineAnalysis",
    "HIBPError",
    "fetch_all_breaches",
    "fetch_account_breaches",
    "load_breaches_from_file",
]
