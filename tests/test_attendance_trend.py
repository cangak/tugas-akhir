import pandas as pd

from modules.attendance_trend import TREND_METRICS, aggregate_attendance_trend


def trend_source(dates):
    return pd.DataFrame({
        "NIP": [str(index) for index in range(len(dates))],
        "Tanggal": pd.to_datetime(dates), "Status": "HADIR", "wajib_presensi": True,
        "Sumber_Datang": "MESIN", "Sumber_Pulang": "MESIN", "TK": False,
        "Terlambat": False,
    })


def test_monthly_trend_has_one_chronological_point_per_year_month():
    dates = [f"2026-{month:02d}-01" for month in range(1, 9)] + [
        "2026-03-05", "2026-03-17", "2026-03-31"
    ]
    result = aggregate_attendance_trend(trend_source(dates), "Bulanan")
    assert result["PeriodLabel"].tolist() == [
        "Jan 2026", "Feb 2026", "Mar 2026", "Apr 2026",
        "May 2026", "Jun 2026", "Jul 2026", "Aug 2026",
    ]
    assert len(result) == 8
    assert result["PeriodKey"].is_unique
    assert not result["PeriodLabel"].duplicated().any()
    assert int(result.loc[result["PeriodLabel"].eq("Mar 2026"), "Wajib"].iloc[0]) == 4
    assert TREND_METRICS["Kepatuhan Presensi"] == "compliance_percentage"
    assert TREND_METRICS["Kehadiran Fisik"] == "physical_attendance_percentage"


def test_year_is_part_of_month_bucket_and_no_missing_month_is_invented():
    result = aggregate_attendance_trend(
        trend_source(["2025-03-01", "2026-03-01", "2026-08-01"]), "Bulanan"
    )
    assert result["PeriodLabel"].tolist() == ["Mar 2025", "Mar 2026", "Aug 2026"]


def test_daily_and_weekly_buckets_remain_unique():
    source = trend_source(["2026-03-01", "2026-03-01", "2026-03-02", "2026-03-08"])
    daily = aggregate_attendance_trend(source, "Harian")
    weekly = aggregate_attendance_trend(source, "Mingguan")
    assert len(daily) == 3 and daily["PeriodKey"].is_unique
    assert len(weekly) == 2 and weekly["PeriodKey"].is_unique
