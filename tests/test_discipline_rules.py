import pandas as pd
import pytest

from modules.discipline_rules import (
    calculate_consecutive_unexcused_days,
    calculate_ytd_tk,
    evaluate_discipline_rule,
)


@pytest.mark.parametrize(("days", "level", "text"), [
    (0, "Belum Mencapai Ambang", "Belum mencapai ambang"),
    (2, "Belum Mencapai Ambang", "Belum mencapai ambang"),
    (3, "Ringan", "Teguran Lisan"),
    (5, "Ringan", "Teguran Tertulis"),
    (8, "Ringan", "Pernyataan Tidak Puas"),
    (12, "Sedang", "6 bulan"),
    (15, "Sedang", "9 bulan"),
    (18, "Sedang", "12 bulan"),
    (22, "Berat", "Penurunan jabatan"),
    (26, "Berat", "Pembebasan dari jabatan"),
    (28, "Berat", "Pemberhentian dengan hormat"),
])
def test_pns_rules(days, level, text):
    result = evaluate_discipline_rule("PNS", days, 0)
    assert result["discipline_level"] == level
    assert text in result["indication"]
    assert result["requires_verification"] is True
    assert result["is_final_decision"] is False


@pytest.mark.parametrize(("days", "level", "text"), [
    (3, "Ringan", "Teguran Lisan"),
    (5, "Ringan", "Teguran Tertulis"),
    (8, "Ringan", "Pernyataan Tidak Puas"),
    (12, "Sedang", "1 tahun"),
    (15, "Sedang", "2 tahun"),
    (18, "Sedang", "3 tahun"),
    (22, "Berat", "Pemutusan hubungan"),
])
def test_pppk_rules(days, level, text):
    result = evaluate_discipline_rule("PPPK", days, 0)
    assert result["discipline_level"] == level
    assert text in result["indication"]


@pytest.mark.parametrize(("kind", "article"), [
    ("PNS", "huruf f angka 4"), ("PPPK", "huruf g angka 2"),
])
def test_consecutive_rule_has_priority(kind, article):
    result = evaluate_discipline_rule(kind, 10, 10)
    assert result["discipline_level"] == "Berat"
    assert article in result["article"]


def test_unknown_type_never_defaults_to_pns():
    result = evaluate_discipline_rule("UNKNOWN", 28, 10)
    assert result["rule_status"] == "EMPLOYEE_TYPE_REVIEW_REQUIRED"
    assert result["discipline_level"] == "Perlu Verifikasi"
    assert "Jenis pegawai perlu diverifikasi" in result["indication"]


def test_pppk_unmapped_range_requires_review():
    result = evaluate_discipline_rule("PPPK", 25, 0)
    assert result["rule_status"] == "REVIEW_REQUIRED"
    assert result["indication"] == "Memerlukan verifikasi ketentuan"


def test_ytd_cutoff_and_duplicate_month_are_not_double_counted():
    rows = pd.DataFrame({
        "NIP": ["1", "1", "1", "1"], "Tahun": [2026] * 4,
        "Bulan": ["Januari", "Februari", "Februari", "April"], "TK": [1, 2, 2, 9],
    })
    assert calculate_ytd_tk(rows, 2026, "Maret") == 3


def test_ytd_daily_counts_only_unique_required_days():
    rows = pd.DataFrame({
        "NIP": ["1"] * 5,
        "Tanggal": pd.to_datetime(["2026-03-02", "2026-03-02", "2026-03-03", "2026-03-07", "2026-04-01"]),
        "TK": [True, True, True, True, True],
        "wajib_presensi": [True, True, False, False, True],
        "eligible_tk": [True, True, False, False, True],
    })
    assert calculate_ytd_tk(rows, 2026, "Maret") == 1


def test_consecutive_uses_required_workdays_only():
    rows = pd.DataFrame({
        "Tanggal": pd.to_datetime(["2026-01-02", "2026-01-03", "2026-01-05", "2026-01-06"]),
        "TK": [True, False, True, False],
        "wajib_presensi": [True, False, True, True],
        "eligible_tk": [True, False, True, True],
    })
    assert calculate_consecutive_unexcused_days(rows, 2026, "Januari") == 2


def test_consecutive_unavailable_without_calendar_fields():
    rows = pd.DataFrame({"Tanggal": ["2026-01-02"], "TK": [True]})
    assert calculate_consecutive_unexcused_days(rows, 2026, "Januari") is None


@pytest.mark.parametrize(("days", "expected"), [
    (3, "Ringan"), (4, "Ringan"), (6, "Ringan"), (7, "Ringan"),
    (10, "Ringan"), (11, "Sedang"), (13, "Sedang"), (14, "Sedang"),
    (16, "Sedang"), (17, "Sedang"), (20, "Sedang"), (21, "Berat"),
    (24, "Berat"), (25, "Berat"), (27, "Berat"), (28, "Berat"),
])
def test_pns_all_boundaries(days, expected):
    assert evaluate_discipline_rule("PNS", days, 9)["discipline_level"] == expected


def test_consecutive_boundary_9_to_10():
    assert evaluate_discipline_rule("PNS", 10, 9)["discipline_level"] == "Ringan"
    assert evaluate_discipline_rule("PNS", 10, 10)["discipline_level"] == "Berat"


def test_engine_returns_requested_context():
    result = evaluate_discipline_rule(
        "PNS", 3, None, nip="123", period_end="2026-03-31",
        data_granularity="daily", consecutive_rule_available=False,
    )
    assert result["nip"] == "123"
    assert result["annual_tk_days"] == 3
    assert result["consecutive_tk_days"] is None
    assert result["consecutive_rule_available"] is False
    assert result["data_granularity"] == "DAILY"
