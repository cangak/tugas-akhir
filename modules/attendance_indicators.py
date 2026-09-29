"""Shared definitions for compliance, physical attendance, and lateness."""
from __future__ import annotations

import pandas as pd


VALID_EXACT_STATUSES = {"HADIR", "WFH", "WFA", "DL", "CUTI", "SL", "SK", "MR", "PBT"}
VALID_CODE_PATTERN = r"\b(?:MESIN|WFH|WFA|DL|SL|SK|MR|PBT)\b|CUTI"
PHYSICAL_EXACT_STATUSES = {"HADIR", "SL", "SK", "MR", "PBT"}
PHYSICAL_CODE_PATTERN = r"\b(?:MESIN|SL|SK|MR|PBT)\b"


def prepare_daily_indicators(source: pd.DataFrame) -> pd.DataFrame:
    """Return at most one classified contribution for each NIP and date."""
    if source.empty or not {"NIP", "Tanggal", "Status"}.issubset(source.columns):
        return pd.DataFrame(columns=["NIP", "Tanggal", "Wajib Presensi", "Status Sah", "Hadir Fisik", "TK", "Terlambat", "Cuti", "WFH", "DL"])
    daily = source.copy()
    daily["Tanggal"] = pd.to_datetime(daily["Tanggal"], errors="coerce").dt.normalize()
    daily = daily[daily["Tanggal"].notna()].sort_values(["NIP", "Tanggal"], kind="stable")
    daily = daily.drop_duplicates(["NIP", "Tanggal"], keep="first").copy()
    status = daily["Status"].fillna("").astype(str).str.strip().str.upper()
    arrival = daily.get("Sumber_Datang", pd.Series("", index=daily.index)).fillna("").astype(str).str.upper()
    departure = daily.get("Sumber_Pulang", pd.Series("", index=daily.index)).fillna("").astype(str).str.upper()
    codes = arrival + "/" + departure
    required = daily.get("wajib_presensi", pd.Series(True, index=daily.index)).fillna(False).astype(bool)
    tk = daily.get("TK", pd.Series(False, index=daily.index)).fillna(False).astype(bool) | status.isin({"TK", "TK/TK"})
    leave_source = codes.str.contains("CUTI", regex=False, na=False) | status.eq("CUTI")
    wfh_source = codes.str.contains(r"\b(?:WFH|WFA)\b", regex=True, na=False) | status.isin({"WFH", "WFA"})
    official_duty_source = codes.str.contains(r"\bDL\b", regex=True, na=False) | status.eq("DL")
    # Satu NIP + tanggal hanya boleh menyumbang ke satu komposisi status.
    # Pada source campuran (mis. DL/WFH), status yang lebih spesifik dipilih
    # dengan urutan TK -> Cuti -> DL -> WFH tanpa mengubah status sahnya.
    leave = leave_source & ~tk
    official_duty = official_duty_source & ~tk & ~leave
    wfh = wfh_source & ~tk & ~leave & ~official_duty
    valid = (status.isin(VALID_EXACT_STATUSES) | codes.str.contains(VALID_CODE_PATTERN, regex=True, na=False)) & ~tk
    nonphysical_status = status.isin({"CUTI", "WFH", "WFA", "DL"})
    physical = (status.isin(PHYSICAL_EXACT_STATUSES) | codes.str.contains(PHYSICAL_CODE_PATTERN, regex=True, na=False)) & ~nonphysical_status & ~leave & ~wfh & ~official_duty & ~tk
    late = daily.get("Terlambat", pd.Series(False, index=daily.index)).fillna(False).astype(bool)
    result = daily.copy()
    result["Wajib Presensi"] = required
    result["Status Sah"] = required & valid
    result["Hadir Fisik"] = required & physical
    # TK adalah fakta presensi existing. Kalender hanya menentukan denominator
    # kepatuhan dan menandai anomali; nilainya tidak dihitung ulang di sini.
    result["TK"] = tk
    result["Terlambat"] = required & physical & late
    result["Cuti"] = required & leave
    result["WFH"] = required & wfh
    result["DL"] = required & official_duty
    return result


def summarize_attendance_indicators(source: pd.DataFrame) -> dict[str, float | int]:
    daily = prepare_daily_indicators(source)
    required = int(daily["Wajib Presensi"].sum()) if not daily.empty else 0
    valid = int(daily["Status Sah"].sum()) if not daily.empty else 0
    physical = int(daily["Hadir Fisik"].sum()) if not daily.empty else 0
    return {
        "required_days": required,
        "valid_status_days": valid,
        "physical_attendance_days": physical,
        "compliance_percentage": valid / required * 100 if required else 0.0,
        "physical_attendance_percentage": physical / required * 100 if required else 0.0,
        "late_events": int(daily["Terlambat"].sum()) if not daily.empty else 0,
        "tk_days": int(daily["TK"].sum()) if not daily.empty else 0,
        "leave_days": int(daily["Cuti"].sum()) if not daily.empty else 0,
        "wfh_days": int(daily["WFH"].sum()) if not daily.empty else 0,
        "official_duty_days": int(daily["DL"].sum()) if not daily.empty else 0,
    }
