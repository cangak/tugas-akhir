from datetime import datetime
from services import activity_log
from pathlib import Path


def test_activity_log_is_persistent_and_deduplicated(tmp_path, monkeypatch):
    path = tmp_path / "activity.jsonl"
    monkeypatch.setenv("ACTIVITY_LOG_PATH", str(path))
    assert activity_log.log_system_activity("DATA_LOAD_SUCCESS", "Data dimuat", "2 record", dedupe_key="source:a")
    assert not activity_log.log_system_activity("DATA_LOAD_SUCCESS", "Data dimuat", "2 record", dedupe_key="source:a")
    events = activity_log.load_system_activities()
    assert len(events) == 1
    assert datetime.fromisoformat(events[0]["timestamp"]).utcoffset().total_seconds() == 7 * 3600
    assert len(path.read_text(encoding="utf-8").splitlines()) == 1


def test_activity_log_keeps_distinct_real_download_clicks(tmp_path, monkeypatch):
    monkeypatch.setenv("ACTIVITY_LOG_PATH", str(tmp_path / "activity.jsonl"))
    activity_log.log_system_activity("REPORT_PDF_DOWNLOAD", "PDF diunduh")
    activity_log.log_system_activity("REPORT_PDF_DOWNLOAD", "PDF diunduh")
    assert len(activity_log.load_system_activities()) == 2


def test_report_download_buttons_use_click_callback():
    source = Path("app.py").read_text(encoding="utf-8")
    assert source.count("on_click=_record_report_download") == 2
    assert 'args=("EXCEL"' in source
    assert 'args=("PDF"' in source
