import pandas as pd

from modules import attendance_compliance
from modules.attendance_compliance import calculate_monthly_attendance_compliance


def calendar_for(dates, workdays=None, required=None):
    workdays = set(dates if workdays is None else workdays)
    required = set(workdays if required is None else required)
    values = pd.to_datetime(dates)
    return pd.DataFrame({
        "tanggal": values,
        "is_hari_kerja": [date in pd.to_datetime(list(workdays)) for date in values],
        "wajib_presensi": [date in pd.to_datetime(list(required)) for date in values],
    })


def daily_rows(statuses, *, late_dates=()):
    rows = []
    for date, status in statuses:
        upper = status.upper()
        rows.append({
            "NIP": "1", "Tanggal": pd.Timestamp(date), "Status": upper,
            "Sumber_Datang": upper.split("/")[0],
            "Sumber_Pulang": upper.split("/")[-1],
            "TK": upper == "TK/TK", "Terlambat": date in late_dates,
        })
    return pd.DataFrame(rows)


def test_all_required_days_valid_is_100_percent(monkeypatch):
    dates = pd.date_range("2026-03-02", periods=20, freq="D")
    monkeypatch.setattr(attendance_compliance, "build_work_calendar", lambda *a, **k: calendar_for(dates))
    daily = daily_rows([(date, "MESIN/MESIN") for date in dates])

    result = calculate_monthly_attendance_compliance(daily, "1", 2026, 3)

    assert result["required_attendance_days"] == 20
    assert result["valid_status_days"] == 20
    assert result["compliance_percentage"] == 100.0


def test_tk_reduces_compliance_but_late_does_not(monkeypatch):
    dates = pd.date_range("2026-03-02", periods=20, freq="D")
    monkeypatch.setattr(attendance_compliance, "build_work_calendar", lambda *a, **k: calendar_for(dates))
    statuses = [(date, "MESIN/MESIN") for date in dates[:-1]] + [(dates[-1], "TK/TK")]
    daily = daily_rows(statuses, late_dates=set(dates[:15]))

    result = calculate_monthly_attendance_compliance(daily, "1", 2026, 3)

    assert result["valid_status_days"] == 19
    assert result["tk_days"] == 1
    assert result["compliance_percentage"] == 95.0


def test_individual_leave_is_valid(monkeypatch):
    dates = pd.date_range("2026-03-02", periods=20, freq="D")
    monkeypatch.setattr(attendance_compliance, "build_work_calendar", lambda *a, **k: calendar_for(dates))
    statuses = [(date, "MESIN/MESIN") for date in dates[:18]] + [(date, "CUTI/CUTI") for date in dates[18:]]

    result = calculate_monthly_attendance_compliance(daily_rows(statuses), "1", 2026, 3)

    assert result["valid_status_days"] == 20
    assert result["compliance_percentage"] == 100.0


def test_additional_source_codes_are_valid_physical_attendance(monkeypatch):
    dates = pd.date_range("2026-03-02", periods=4, freq="D")
    monkeypatch.setattr(attendance_compliance, "build_work_calendar", lambda *a, **k: calendar_for(dates))
    statuses = list(zip(dates, ["SL/SL", "SK/SK", "MR/MR", "PBT/PBT"]))

    result = calculate_monthly_attendance_compliance(daily_rows(statuses), "1", 2026, 3)

    assert result["valid_status_days"] == 4
    assert result["physical_attendance_days"] == 4
    assert result["compliance_percentage"] == 100.0


def test_collective_leave_and_holiday_are_not_denominator(monkeypatch):
    dates = pd.to_datetime(["2026-03-02", "2026-03-03", "2026-03-04"])
    required = {dates[0]}
    workdays = {dates[0], dates[1]}
    monkeypatch.setattr(
        attendance_compliance, "build_work_calendar",
        lambda *a, **k: calendar_for(dates, workdays=workdays, required=required),
    )
    daily = daily_rows([
        (dates[0], "MESIN/MESIN"),
        (dates[1], "CUTI BERSAMA/CUTI BERSAMA"),
        (dates[2], "LIBUR"),
    ])

    result = calculate_monthly_attendance_compliance(daily, "1", 2026, 3)

    assert result["calendar_workdays"] == 2
    assert result["required_attendance_days"] == 1
    assert result["valid_status_days"] == 1
    assert result["compliance_percentage"] == 100.0


def test_duplicate_date_contributes_at_most_once(monkeypatch):
    date = pd.Timestamp("2026-03-02")
    monkeypatch.setattr(attendance_compliance, "build_work_calendar", lambda *a, **k: calendar_for([date]))
    daily = daily_rows([(date, "MESIN/MESIN"), (date, "MESIN/MESIN")])

    result = calculate_monthly_attendance_compliance(daily, "1", 2026, 3)

    assert result["duplicate_days"] == 1
    assert result["valid_status_days"] == 1
    assert result["compliance_percentage"] == 100.0


def test_zero_required_days_is_not_zero_percent(monkeypatch):
    date = pd.Timestamp("2026-03-01")
    monkeypatch.setattr(
        attendance_compliance, "build_work_calendar",
        lambda *a, **k: calendar_for([date], workdays=set(), required=set()),
    )

    result = calculate_monthly_attendance_compliance(daily_rows([(date, "LIBUR")]), "1", 2026, 3)

    assert result["required_attendance_days"] == 0
    assert result["compliance_percentage"] is None
