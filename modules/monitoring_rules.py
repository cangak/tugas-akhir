"""Ambang referensi untuk Rule-Based Monitoring Kepatuhan Presensi.

Modul ini tidak menentukan pelanggaran, sanksi, atau keputusan disiplin.
Pergub hanya digunakan sebagai dasar referensi monitoring dan verifikasi awal.
"""

from __future__ import annotations

from typing import Any

from modules.discipline_rules import (
    REGULATION,
    calculate_consecutive_unexcused_days,
    calculate_ytd_tk,
)


MONITORING_DISCLAIMER = (
    "Rule-Based digunakan sebagai alat bantu monitoring dan identifikasi awal "
    "berdasarkan data presensi serta ambang referensi Pergub Kalbar Nomor 2 "
    "Tahun 2024. Hasil sistem bukan merupakan penetapan pelanggaran, hukuman, "
    "atau keputusan disiplin."
)

REFERENCE_BANDS = (
    {"min_days": 0, "max_days": 2, "band": "0–2 hari", "status": "Monitoring", "article": None,
     "note": "Belum mencapai ambang referensi 3 hari"},
    {"min_days": 3, "max_days": 3, "band": "3 hari", "status": "Perlu Perhatian", "article": "Pasal 10 ayat (1) huruf c",
     "note": "Akumulasi TK telah mencapai ambang referensi 3 hari dalam tahun berjalan."},
    {"min_days": 4, "max_days": 6, "band": "4–6 hari", "status": "Perlu Verifikasi", "article": "Pasal 10 ayat (1) huruf c",
     "note": "Akumulasi TK berada pada rentang referensi 4–6 hari dalam tahun berjalan."},
    {"min_days": 7, "max_days": 10, "band": "7–10 hari", "status": "Prioritas Tindak Lanjut", "article": "Pasal 10 ayat (1) huruf c",
     "note": "Akumulasi TK berada pada rentang referensi 7–10 hari dalam tahun berjalan."},
    {"min_days": 11, "max_days": 13, "band": "11–13 hari", "status": "Prioritas Tindak Lanjut", "article": "Pasal 11",
     "note": "Akumulasi TK telah memasuki rentang referensi 11–13 hari dalam tahun berjalan."},
    {"min_days": 14, "max_days": 16, "band": "14–16 hari", "status": "Prioritas Tindak Lanjut", "article": "Pasal 11",
     "note": "Akumulasi TK telah memasuki rentang referensi 14–16 hari dalam tahun berjalan."},
    {"min_days": 17, "max_days": 20, "band": "17–20 hari", "status": "Prioritas Tindak Lanjut", "article": "Pasal 11",
     "note": "Akumulasi TK telah memasuki rentang referensi 17–20 hari dalam tahun berjalan."},
    {"min_days": 21, "max_days": None, "band": "≥21 hari", "status": "Prioritas Verifikasi", "article": "Pasal 12",
     "note": "Akumulasi TK telah mencapai rentang yang memerlukan perhatian dan verifikasi lebih lanjut."},
)


def evaluate_attendance_monitoring_rule(
    annual_tk_days: int,
    consecutive_tk_days: int | None = None,
    consecutive_available: bool = False,
    *,
    nip: str | None = None,
    employee_type: str | None = None,
    period_end: object = None,
    data_granularity: str = "AGGREGATED",
) -> dict[str, Any]:
    """Bandingkan TK tercatat dengan ambang referensi tanpa keluaran hukuman."""
    try:
        annual_days = int(annual_tk_days)
        consecutive_days = None if consecutive_tk_days is None else int(consecutive_tk_days)
    except (TypeError, ValueError):
        annual_days, consecutive_days = 0, None
        invalid = True
    else:
        invalid = annual_days < 0 or (consecutive_days is not None and consecutive_days < 0)
    base = {
        "regulation": REGULATION["short_title"],
        "annual_tk_days": max(annual_days, 0),
        "consecutive_tk_days": consecutive_days if consecutive_available else None,
        "consecutive_available": bool(consecutive_available),
        "special_monitoring_flag": False,
        "requires_verification": max(annual_days, 0) > 0,
        "nip": None if nip is None else str(nip),
        "employee_type": str(employee_type or "UNKNOWN").upper(),
        "period_end": period_end,
        "data_granularity": str(data_granularity).upper(),
    }
    if invalid:
        return {**base, "reference_status": "Perlu Verifikasi", "reference_band": "Data perlu diverifikasi",
                "monitoring_note": "Data monitoring tidak valid dan perlu diverifikasi.", "reference_article": None,
                "requires_verification": True}
    if consecutive_available and consecutive_days is not None and consecutive_days >= 10:
        return {**base, "reference_status": "Prioritas Verifikasi", "reference_band": "10 hari kerja berturut-turut",
                "monitoring_note": "Terdeteksi indikasi TK pada 10 hari wajib presensi berturut-turut. Memerlukan verifikasi lebih lanjut.",
                "reference_article": "Pasal 12", "special_monitoring_flag": True, "requires_verification": True}
    rule = next(
        item for item in REFERENCE_BANDS
        if annual_days >= item["min_days"] and (item["max_days"] is None or annual_days <= item["max_days"])
    )
    return {**base, "reference_status": rule["status"], "reference_band": rule["band"],
            "monitoring_note": rule["note"], "reference_article": rule["article"]}


__all__ = [
    "MONITORING_DISCLAIMER", "REFERENCE_BANDS", "REGULATION",
    "calculate_consecutive_unexcused_days", "calculate_ytd_tk",
    "evaluate_attendance_monitoring_rule",
]
