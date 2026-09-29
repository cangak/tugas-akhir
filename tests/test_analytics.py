import pandas as pd

from modules.analytics import (
    WARNING_PRIORITY, apply_filters, attendance_rate, dashboard_metrics,
    employee_warning_summary, ews_period_context, get_monthly_tk_days,
    warning_status,
)


def sample_data():
    return pd.DataFrame([
        {"NIP": "1", "Nama Pegawai": "A", "Unit Kerja": "OPD A", "Jenis Pegawai": "PNS", "Tahun": 2026, "Bulan": "Januari", "TK": 1, "Terlambat": 0, "Hari Kerja": 20, "Cuti": 2, "WFH": 0, "DL": 1},
        {"NIP": "1", "Nama Pegawai": "A", "Unit Kerja": "OPD A", "Jenis Pegawai": "PNS", "Tahun": 2026, "Bulan": "Februari", "TK": 2, "Terlambat": 1, "Hari Kerja": 20, "Cuti": 0, "WFH": 0, "DL": 0},
        {"NIP": "2", "Nama Pegawai": "B", "Unit Kerja": "OPD B", "Jenis Pegawai": "PPPK", "Tahun": 2026, "Bulan": "Januari", "TK": 0, "Terlambat": 0, "Hari Kerja": 20, "Cuti": 5, "WFH": 0, "DL": 0},
    ])


def test_attendance_rate_does_not_treat_valid_leave_as_violation():
    assert attendance_rate(sample_data()) == 95.0


def test_unique_employee_and_tk_metrics_share_one_scope():
    metrics = dashboard_metrics(sample_data())
    assert metrics["total_employees"] == 2
    assert metrics["total_tk"] == 3
    assert metrics["employees_with_tk"] == 1


def test_filters_are_consistent():
    result = apply_filters(sample_data(), month="Februari", opd="OPD A")
    assert len(result) == 1
    assert result.iloc[0]["TK"] == 2


def test_employee_type_filter_combines_with_period_and_opd():
    all_rows = apply_filters(sample_data(), employee_type="Semua Jenis Pegawai")
    assert len(all_rows) == len(sample_data())
    pns = apply_filters(sample_data(), month="Februari", opd="OPD A", employee_type="PNS")
    assert set(pns["NIP"]) == {"1"}
    pppk = apply_filters(sample_data(), month="Januari", employee_type="PPPK")
    assert set(pppk["NIP"]) == {"2"}
    unknown = apply_filters(sample_data(), employee_type="Belum Diketahui")
    assert unknown.empty


def test_warning_rules_boundaries():
    assert [warning_status(value) for value in (0, 1, 2, 3, 5, 6)] == [
        "Normal", "Perlu Perhatian", "Perlu Perhatian",
        "Perlu Verifikasi", "Perlu Verifikasi", "Prioritas Tindak Lanjut",
    ]


def test_warning_priority_is_derived_with_expected_status_names():
    assert WARNING_PRIORITY == {
        "Normal": 0,
        "Perlu Perhatian": 1,
        "Perlu Verifikasi": 2,
        "Prioritas Tindak Lanjut": 3,
    }


def test_warning_comparison_uses_status_priority_then_tk_delta():
    current = sample_data().query("Bulan == 'Februari'")
    previous = sample_data().query("Bulan == 'Januari' and NIP == '1'")
    result = employee_warning_summary(current, previous).iloc[0]
    assert result["Status Early Warning"] == "Perlu Perhatian"
    assert result["Status Sebelumnya"] == "Perlu Perhatian"
    assert result["Delta TK"] == 1
    assert result["Tren"] == "Memburuk"


def test_ews_period_context_handles_january_previous_year():
    context = ews_period_context(2026, "Januari")
    assert context["previous_year"] == 2025
    assert context["previous_month"] == "Desember"


def test_monthly_tk_uses_unique_required_dates_and_distinguishes_missing_month():
    daily = pd.DataFrame({
        "NIP": ["123"] * 5,
        "Tanggal": pd.to_datetime(["2026-09-10", "2026-09-10", "2026-09-11", "2026-09-12", "2026-08-01"]),
        "TK": [True, True, True, True, True],
        "wajib_presensi": [True, True, False, False, True],
        "eligible_tk": [True, True, False, False, True],
    })
    assert get_monthly_tk_days(daily, "123", 2026, "September") == 1
    assert get_monthly_tk_days(daily, "123", 2026, "Oktober") is None
