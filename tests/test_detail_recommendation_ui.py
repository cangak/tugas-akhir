from streamlit.testing.v1 import AppTest

from modules.excel_parser import build_dashboard_dataframe, load_semua_presensi


def _page_text(app: AppTest) -> str:
    elements = list(app.warning) + list(app.info) + list(app.markdown) + list(app.caption)
    return " ".join(str(element.value) for element in elements)


def test_detail_recommendation_uses_same_employee_type_as_badge():
    employees = build_dashboard_dataframe(load_semua_presensi()).drop_duplicates("NIP")
    labels = {
        kind: f"{row['Nama Pegawai']} — {row['NIP']}"
        for kind in ("PNS", "PPPK")
        for _, row in employees[employees["Jenis Pegawai"].eq(kind)].head(1).iterrows()
    }
    assert set(labels) == {"PNS", "PPPK"}

    app = AppTest.from_file("app.py", default_timeout=30)
    app.session_state["is_logged_in"] = True
    app.session_state["username"] = "test"
    app.run()
    next(item for item in app.radio if item.label == "Pilih halaman").set_value("👤 Detail Pegawai").run()

    next(item for item in app.selectbox if item.label == "Pegawai").select(labels["PNS"]).run()
    pns_text = _page_text(app)
    assert "Status kepegawaian PNS/non-PNS tidak tersedia" not in pns_text
    assert "employee-type-badge pns" in pns_text

    next(item for item in app.selectbox if item.label == "Pegawai").select(labels["PPPK"]).run()
    pppk_text = _page_text(app)
    assert "Status kepegawaian PNS/non-PNS tidak tersedia" not in pppk_text
    assert "Jenis pegawai terdeteksi sebagai PPPK" in pppk_text
    assert "employee-type-badge pppk" in pppk_text
    assert not app.exception


def test_detail_page_uses_one_master_month_year_period():
    app = AppTest.from_file("app.py", default_timeout=30)
    app.session_state["is_logged_in"] = True
    app.session_state["username"] = "test"
    app.run()
    navigation = next(item for item in app.radio if item.label == "Pilih halaman")
    detail_option = next(option for option in navigation.options if "Detail Pegawai" in option)
    navigation.set_value(detail_option).run()

    period_filters = [item for item in app.selectbox if item.label == "Periode"]
    assert len(period_filters) == 1
    assert period_filters[0].options
    assert all(option.rsplit(" ", 1)[-1].isdigit() for option in period_filters[0].options)

    chosen_period = period_filters[0].options[0]
    period_filters[0].select(chosen_period).run()
    page_text = _page_text(app)
    assert f"Riwayat presensi pegawai pada {chosen_period}." in page_text
    assert len([item for item in app.selectbox if item.label == "Periode"]) == 1
    assert any(item.label == "Status" for item in app.selectbox)
    assert not app.exception
