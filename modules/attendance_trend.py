"""Canonical time bucketing for the attendance trend chart."""
from __future__ import annotations

import pandas as pd
from modules.attendance_indicators import prepare_daily_indicators


MONTH_SHORT = {
    1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun",
    7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec",
}

# Label UI sengaja dipisahkan dari nama kolom internal hasil agregasi.
TREND_METRICS = {
    "Kepatuhan Presensi": "compliance_percentage",
    "Kehadiran Fisik": "physical_attendance_percentage",
    "TK": "tk_days",
    "Keterlambatan": "late_events",
    "Cuti": "leave_days",
    "WFH": "wfh_days",
    "DL": "official_duty_days",
}


def aggregate_attendance_trend(source: pd.DataFrame, granularity: str) -> pd.DataFrame:
    """Aggregate first by a canonical key, then create display labels.

    The attendance formula intentionally mirrors the existing chart formula.
    """
    frame = prepare_daily_indicators(source)
    if granularity == "Harian":
        frame["PeriodKey"] = frame["Tanggal"].dt.normalize()
    elif granularity == "Mingguan":
        frame["PeriodKey"] = frame["Tanggal"].dt.to_period("W-SUN")
    elif granularity == "Bulanan":
        frame["PeriodKey"] = frame["Tanggal"].dt.to_period("M")
    else:
        raise ValueError(f"Granularitas tidak dikenal: {granularity}")

    result = frame.groupby("PeriodKey", as_index=False).agg(
        Wajib=("Wajib Presensi", "sum"), Sah=("Status Sah", "sum"),
        physical_attendance_days=("Hadir Fisik", "sum"), tk_days=("TK", "sum"),
        leave_days=("Cuti", "sum"), late_events=("Terlambat", "sum"),
        wfh_days=("WFH", "sum"), official_duty_days=("DL", "sum"),
    )
    if granularity == "Harian":
        result["Periode"] = pd.to_datetime(result["PeriodKey"])
        result["PeriodLabel"] = result["Periode"].dt.strftime("%d %b %Y")
    else:
        result["Periode"] = result["PeriodKey"].dt.start_time
        if granularity == "Bulanan":
            result["PeriodLabel"] = result["Periode"].map(
                lambda value: f"{MONTH_SHORT[value.month]} {value.year}"
            )
        else:
            result["PeriodLabel"] = result["Periode"].dt.strftime("%d %b %Y")
    result = result.sort_values("Periode", kind="stable").reset_index(drop=True)
    if not result["PeriodKey"].is_unique:
        raise ValueError("Bucket periode tren tidak unik")
    if result["PeriodLabel"].duplicated().any():
        raise ValueError("Label periode tren tidak unik")

    result["compliance_percentage"] = (result["Sah"] / result["Wajib"].replace(0, pd.NA) * 100).fillna(0)
    result["physical_attendance_percentage"] = (result["physical_attendance_days"] / result["Wajib"].replace(0, pd.NA) * 100).fillna(0)
    # Alias kompatibilitas untuk pemakai existing di luar halaman Analisis Presensi.
    result["Kepatuhan Presensi"] = result["compliance_percentage"]
    result["Kehadiran Fisik"] = result["physical_attendance_percentage"]
    result["TK"] = result["tk_days"]
    result["Keterlambatan"] = result["late_events"]
    result["Cuti"] = result["leave_days"]
    result["WFH"] = result["wfh_days"]
    result["DL"] = result["official_duty_days"]
    return result
