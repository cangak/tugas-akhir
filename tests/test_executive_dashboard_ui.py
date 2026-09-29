import re

from streamlit.testing.v1 import AppTest


def test_executive_dashboard_is_compact_and_filterable():
    app = AppTest.from_file("app.py", default_timeout=30)
    app.session_state["is_logged_in"] = True
    app.session_state["username"] = "test"
    app.run()

    html = " ".join(str(item.value) for item in app.markdown)
    assert "Executive Dashboard" in html
    assert "Ringkasan Utama" in html
    assert "Status Keseluruhan" in html
    assert "Perubahan Kondisi" in html
    assert "Perlu Perhatian Pimpinan" in html
    assert "OPD dengan Perhatian Tertinggi" in html
    assert "Executive Insight" in html
    assert html.count("<div class='executive-kpi-label'>") == 4
    assert "Hari Rawan Ketidakpatuhan" not in html
    assert "Distribusi Waktu Kedatangan" not in html
    assert "Pegawai Memerlukan Perhatian" not in html
    assert not app.exception

    month_filter = next(item for item in app.selectbox if item.label == "Bulan")
    month_filter.select("Mei").run()
    filtered_html = " ".join(str(item.value) for item in app.markdown)
    assert re.search(r"Mei(?: \d{4})? •", filtered_html)
    assert not app.exception
