import re

from streamlit.testing.v1 import AppTest


def _open_page(app: AppTest, page_name: str):
    navigation = next(item for item in app.radio if item.label == "Pilih halaman")
    option = next(value for value in navigation.options if page_name in value)
    navigation.set_value(option).run()


def test_opd_analysis_owns_comparison_not_time_series():
    app = AppTest.from_file("app.py", default_timeout=30)
    app.session_state["is_logged_in"] = True
    app.session_state["username"] = "test"
    app.run()
    _open_page(app, "Analisis OPD")
    html = " ".join(str(item.value) for item in app.markdown)
    assert "Perbandingan OPD" in html
    assert "Detail OPD Terpilih" in html
    assert "Tren Presensi OPD" not in html
    assert not any(item.label == "Tampilan Tren" for item in app.selectbox)
    assert len([item for item in app.selectbox if item.label == "Pilih OPD"]) == 1
    comparison_table = next(
        item for item in app.dataframe
        if "Pegawai dengan TK" in item.value.columns and "Unit Kerja" in item.value.columns
    )
    assert "Hari Wajib Presensi Kalender" in comparison_table.value.columns
    calendar_days = comparison_table.value["Hari Wajib Presensi Kalender"]
    assert calendar_days.notna().all()
    assert calendar_days.nunique() == 1
    assert int(calendar_days.iloc[0]) < 366
    assert not app.exception


def test_top_five_is_exactly_capped_at_five_opds():
    app = AppTest.from_file("app.py", default_timeout=30)
    app.session_state["is_logged_in"] = True
    app.session_state["username"] = "test"
    app.run()
    _open_page(app, "Analisis OPD")
    selector = next(item for item in app.selectbox if item.label == "Tampilkan")
    selector.select("Top 5").run()
    html = " ".join(str(item.value) for item in app.markdown)
    displayed = int(re.search(r"opd-kpi-value'>(\d+) OPD</div><div class='opd-kpi-label'>OPD Ditampilkan", html).group(1))
    assert displayed <= 5
    assert displayed == min(5, len(next(item for item in app.selectbox if item.label == "Pilih OPD").options))
    assert not app.exception


def test_attendance_analysis_keeps_time_series_owner():
    app = AppTest.from_file("app.py", default_timeout=30)
    app.session_state["is_logged_in"] = True
    app.session_state["username"] = "test"
    app.run()
    _open_page(app, "Analisis Presensi")
    html = " ".join(str(item.value) for item in app.markdown)
    assert "Tren Presensi" in html
    assert any(item.label == "Granularitas" for item in app.radio)
    assert not app.exception
