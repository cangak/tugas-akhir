"""Pemetaan indikasi PP 94/2021 untuk Early Warning System.

Modul ini hanya menghasilkan indikasi berbasis data presensi. Keputusan
disiplin tetap berada pada pejabat yang berwenang setelah verifikasi dan
pemeriksaan.
"""

from __future__ import annotations

from typing import Any

import pandas as pd


REGULATION_PP94 = {
    "name": "PP Nomor 94 Tahun 2021",
    "title": "Disiplin Pegawai Negeri Sipil",
    "implementation": "Peraturan BKN Nomor 6 Tahun 2022",
}

MONTH_ORDER = [
    "Januari", "Februari", "Maret", "April", "Mei", "Juni",
    "Juli", "Agustus", "September", "Oktober", "November", "Desember",
]

PP94_TK_RULES = [
    {"min": 3, "max": 3, "level": "Ringan", "rule_range": "3 hari", "indication": "Teguran lisan", "article": "Pasal 9"},
    {"min": 4, "max": 6, "level": "Ringan", "rule_range": "4-6 hari", "indication": "Teguran tertulis", "article": "Pasal 9"},
    {"min": 7, "max": 10, "level": "Ringan", "rule_range": "7-10 hari", "indication": "Pernyataan tidak puas secara tertulis", "article": "Pasal 9"},
    {"min": 11, "max": 13, "level": "Sedang", "rule_range": "11-13 hari", "indication": "Pemotongan tunjangan kinerja sebesar 25% selama 6 bulan", "article": "Pasal 10"},
    {"min": 14, "max": 16, "level": "Sedang", "rule_range": "14-16 hari", "indication": "Pemotongan tunjangan kinerja sebesar 25% selama 9 bulan", "article": "Pasal 10"},
    {"min": 17, "max": 20, "level": "Sedang", "rule_range": "17-20 hari", "indication": "Pemotongan tunjangan kinerja sebesar 25% selama 12 bulan", "article": "Pasal 10"},
    {"min": 21, "max": 24, "level": "Berat", "rule_range": "21-24 hari", "indication": "Penurunan jabatan setingkat lebih rendah selama 12 bulan", "article": "Pasal 11"},
    {"min": 25, "max": 27, "level": "Berat", "rule_range": "25-27 hari", "indication": "Pembebasan dari jabatan menjadi jabatan pelaksana selama 12 bulan", "article": "Pasal 11"},
    {"min": 28, "max": None, "level": "Berat", "rule_range": "28 hari atau lebih", "indication": "Pemberhentian dengan hormat tidak atas permintaan sendiri sebagai PNS", "article": "Pasal 11"},
]


def calculate_tk_by_month(employee_df: pd.DataFrame, year: int) -> pd.DataFrame:
    """Jumlahkan rekap TK bulanan untuk tepat satu tahun."""
    source = employee_df.copy()
    if "Tahun" not in source or "Bulan" not in source or "TK" not in source:
        return pd.DataFrame(columns=["Bulan", "TK"])
    source = source[pd.to_numeric(source["Tahun"], errors="coerce").eq(int(year))]
    result = source.groupby("Bulan", as_index=False)["TK"].sum()
    result["Bulan"] = pd.Categorical(result["Bulan"], categories=MONTH_ORDER, ordered=True)
    return result.sort_values("Bulan").reset_index(drop=True)


def calculate_annual_tk(employee_df: pd.DataFrame, year: int) -> int:
    """TK kumulatif pada tahun yang diminta, tanpa mencampur tahun lain."""
    monthly = calculate_tk_by_month(employee_df, year)
    return int(monthly["TK"].sum()) if not monthly.empty else 0


def calculate_max_consecutive_tk(daily_df: pd.DataFrame) -> int | None:
    """Hitung TK berturut-turut jika data harian berstatus TK tersedia."""
    required = {"Tanggal", "TK"}
    if not required.issubset(daily_df.columns):
        return None
    source = daily_df.copy()
    source["Tanggal"] = pd.to_datetime(source["Tanggal"], errors="coerce")
    source = source.dropna(subset=["Tanggal"]).sort_values("Tanggal")
    if source.empty:
        return None
    if "Status" in source:
        source = source[source["Status"].astype(str).str.upper().ne("LIBUR")]
    maximum = streak = 0
    for is_tk in source["TK"].fillna(False).astype(bool):
        streak = streak + 1 if is_tk else 0
        maximum = max(maximum, streak)
    return maximum


def get_next_pp94_threshold(tk_days: int) -> dict[str, Any] | None:
    """Ambang berikutnya untuk pesan early warning, bila masih ada."""
    thresholds = [3, 4, 7, 11, 14, 17, 21, 25, 28]
    for threshold in thresholds:
        if tk_days < threshold:
            rule = next(rule for rule in PP94_TK_RULES if rule["min"] <= threshold <= (rule["max"] or threshold))
            return {"next_threshold": threshold, "remaining_days": threshold - tk_days, "next_level": rule["level"]}
    return None


def get_pp94_indication(annual_tk_days: int, consecutive_days: int | None = None, verified: bool = False) -> dict[str, Any]:
    """Peta TK *terverifikasi* tahunan ke indikasi, bukan keputusan otomatis."""
    annual_tk_days = max(int(annual_tk_days), 0)
    result: dict[str, Any] = {
        "has_indication": False,
        "level": "Belum mencapai ambang",
        "pp94_status": "Belum Mencapai Ambang",
        "tk_days": annual_tk_days,
        "rule_range": "0-2 hari",
        "indication": "Monitoring presensi",
        "article": None,
        "regulation": REGULATION_PP94["name"],
        "verification_required": True,
        "consecutive_evaluable": consecutive_days is not None,
        "special_consecutive_warning": False,
    }
    if not verified:
        result.update({
            "pp94_status": "Memerlukan Verifikasi",
            "level": None,
            "indication": "Data TK tercatat belum dapat digunakan untuk menentukan indikator disiplin sebelum alasan ketidakhadiran diverifikasi.",
            "verification_status": "NEEDS_VERIFICATION",
        })
        return result
    result["verification_status"] = "VERIFIED"
    for rule in PP94_TK_RULES:
        if annual_tk_days >= rule["min"] and (rule["max"] is None or annual_tk_days <= rule["max"]):
            result.update({
                "has_indication": True,
                "level": rule["level"],
                "pp94_status": f"Indikasi {rule['level']}",
                "rule_range": rule["rule_range"],
                "indication": rule["indication"],
                "article": rule["article"],
            })
            break
    next_threshold = get_next_pp94_threshold(annual_tk_days)
    if next_threshold and next_threshold["remaining_days"] == 1:
        result["near_threshold"] = next_threshold
        if not result["has_indication"]:
            result["pp94_status"] = "Mendekati Ambang"
    if consecutive_days is not None and consecutive_days >= 10:
        result.update({
            "level": "Berat",
            "pp94_status": "Peringatan Khusus 10 Hari Berturut-turut",
            "indication": "Pemberhentian dengan hormat tidak atas permintaan sendiri sebagai PNS",
            "article": "Pasal 11",
            "special_consecutive_warning": True,
            "has_indication": True,
        })
    return result


def evaluate_pp94_indicator(*, year: int, recorded_tk_days: int, employee_type: str | None = None, verified_unexcused_days: int | None = None, consecutive_days: int | None = None) -> dict[str, Any]:
    """Indikator disiplin PNS terpusat; TK presensi mentah tidak dipetakan otomatis."""
    recorded_tk_days = max(int(recorded_tk_days), 0)
    if verified_unexcused_days is not None:
        verified_unexcused_days = int(verified_unexcused_days)
        if verified_unexcused_days < 0:
            raise ValueError("Hari terverifikasi tidak boleh negatif.")
        if verified_unexcused_days > recorded_tk_days:
            raise ValueError("Hari terverifikasi tidak boleh melebihi hari TK tercatat.")
    result = {
        "year": int(year), "recorded_tk_days": recorded_tk_days,
        "verified_unexcused_days": verified_unexcused_days, "legal_basis": REGULATION_PP94["name"],
        "implementation_basis": REGULATION_PP94["implementation"], "is_final_decision": False,
    }
    if employee_type is None:
        result.update({"applicable": None, "verification_status": "EMPLOYMENT_STATUS_UNAVAILABLE", "discipline_level": None, "indicator": "Status kepegawaian belum tersedia; indikator PP 94/2021 belum dapat ditentukan otomatis."})
        return result
    if str(employee_type).upper() not in {"PNS", "CPNS"}:
        result.update({"applicable": False, "verification_status": "NOT_APPLICABLE", "discipline_level": None, "indicator": "Indikator PP 94/2021 untuk Disiplin PNS tidak diterapkan pada status pegawai ini."})
        return result
    result["applicable"] = True
    mapped = get_pp94_indication(verified_unexcused_days or 0, consecutive_days, verified=verified_unexcused_days is not None)
    result.update({
        "verification_status": mapped.get("verification_status"),
        "discipline_level": mapped.get("level"), "indicator": mapped.get("indication"),
        "article": mapped.get("article"), "pp94_status": mapped.get("pp94_status"),
        "consecutive_10_workdays": mapped.get("special_consecutive_warning", False),
    })
    return result
