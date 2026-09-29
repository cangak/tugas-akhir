"""Null-safe formatting helpers for user-facing values."""
from __future__ import annotations

import pandas as pd


NULL_TEXT = {"", "nan", "none", "null", "n/a", "<na>"}


def safe_display(value: object, default: str = "Tidak ada indikasi tindak lanjut") -> str:
    if value is None:
        return default
    try:
        if bool(pd.isna(value)):
            return default
    except (TypeError, ValueError):
        pass
    text = str(value).strip()
    return default if text.casefold() in NULL_TEXT else text


def format_percentage_exact(value: float, *, minimum_decimals: int = 2) -> str:
    """Format persen tanpa membuat nilai di bawah 100 tampak tepat 100%."""
    numeric = float(value)
    decimals = max(int(minimum_decimals), 0)
    rendered = f"{numeric:.{decimals}f}"
    while numeric < 100 and float(rendered) >= 100 and decimals < 12:
        decimals += 1
        rendered = f"{numeric:.{decimals}f}"
    return rendered.replace(".", ",") + "%"
