"""Normalisasi dan klasifikasi jenis pegawai berbasis NIP/NI PPPK."""

from __future__ import annotations

from datetime import datetime
from typing import Any

import pandas as pd


PNS_MONTH_MIN = 1
PNS_MONTH_MAX = 12
PPPK_CODE_MIN = 21
PPPK_CODE_MAX = 99
KNOWN_EMPLOYEE_TYPES = {"PNS", "PPPK", "CPNS"}
UNKNOWN_EMPLOYEE_TYPE = "Belum Diketahui"


def normalize_nip(value: Any) -> str | None:
    """Pertahankan digit sebagai string; format rusak tidak ditebak/dikonversi."""
    if value is None or pd.isna(value):
        return None
    nip = str(value).strip().replace(" ", "").replace("-", "")
    if nip.lower() in {"", "nan", "none", "nat"}:
        return None
    # Scientific notation tidak aman dipulihkan karena digit aslinya mungkin
    # sudah kehilangan presisi ketika dibaca sebagai floating point.
    if "e" in nip.lower() or "." in nip:
        return None
    return nip


def detect_employee_type_from_nip(value: Any) -> str:
    nip = normalize_nip(value)
    if not nip or len(nip) != 18 or not nip.isdigit():
        return UNKNOWN_EMPLOYEE_TYPE
    try:
        datetime.strptime(nip[:8], "%Y%m%d")
    except ValueError:
        return UNKNOWN_EMPLOYEE_TYPE
    code = int(nip[12:14])
    if PNS_MONTH_MIN <= code <= PNS_MONTH_MAX:
        return "PNS"
    if PPPK_CODE_MIN <= code <= PPPK_CODE_MAX:
        return "PPPK"
    return UNKNOWN_EMPLOYEE_TYPE


def resolve_employee_type(value: Any, official_type: Any = None) -> tuple[str, str]:
    official = "" if official_type is None or pd.isna(official_type) else str(official_type).strip().upper()
    if official in KNOWN_EMPLOYEE_TYPES:
        return official, "MASTER"
    detected = detect_employee_type_from_nip(value)
    if detected != UNKNOWN_EMPLOYEE_TYPE:
        return detected, "NIP_DETECTION"
    return UNKNOWN_EMPLOYEE_TYPE, "UNKNOWN"


def add_employee_type_columns(
    frame: pd.DataFrame,
    nip_column: str = "NIP",
    official_column: str | None = None,
) -> pd.DataFrame:
    """Deteksi sekali per NIP unik, lalu map kembali ke seluruh record."""
    result = frame.copy()
    if nip_column not in result.columns:
        result["Jenis Pegawai"] = UNKNOWN_EMPLOYEE_TYPE
        result["Jenis Pegawai Source"] = "UNKNOWN"
        return result
    normalized = result[nip_column].map(normalize_nip).astype("string")
    result[nip_column] = normalized
    unique_rows = pd.DataFrame({nip_column: normalized.drop_duplicates()})
    official_map: dict[str, Any] = {}
    if official_column and official_column in result.columns:
        official_map = (
            result.dropna(subset=[nip_column])
            .drop_duplicates(nip_column)
            .set_index(nip_column)[official_column]
            .to_dict()
        )
    resolved = {
        nip: resolve_employee_type(nip, official_map.get(nip))
        for nip in unique_rows[nip_column].dropna()
    }
    result["Jenis Pegawai"] = normalized.map({nip: value[0] for nip, value in resolved.items()}).fillna(UNKNOWN_EMPLOYEE_TYPE)
    result["Jenis Pegawai Source"] = normalized.map({nip: value[1] for nip, value in resolved.items()}).fillna("UNKNOWN")
    return result

