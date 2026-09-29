import pandas as pd

from modules.employee_active_status import apply_employee_active_status, get_employee_inactive_status


INACTIVE_NIPS = ["197712232011011001", "197006261995031006"]


def monthly_rows():
    return pd.DataFrame([
        {"NIP": nip, "Tahun": 2026, "Bulan": month, "TK": 1}
        for nip in INACTIVE_NIPS
        for month in ["Januari", "Juni", "Juli", "Agustus"]
    ])


def test_inactive_employee_filter_is_period_aware_and_preserves_history():
    source = monthly_rows()
    filtered = apply_employee_active_status(source)
    assert filtered.empty
    assert len(source) == 8


def test_explicit_analysis_date_switches_on_effective_date():
    source = monthly_rows().iloc[:2]
    assert len(apply_employee_active_status(source, "2025-12-31")) == 2
    assert apply_employee_active_status(source, "2026-01-01").empty


def test_detail_status_remains_available_without_removing_history():
    for nip in INACTIVE_NIPS:
        status = get_employee_inactive_status(nip)
        assert status["status"] == "NONAKTIF"
        assert status["effective_date"] == pd.Timestamp("2026-01-01")
