from streamlit.testing.v1 import AppTest
import pandas as pd
from modules.excel_parser import load_semua_presensi


def test_audit_trail_exposes_read_only_processing_tab():
    app = AppTest.from_file("app.py", default_timeout=30)
    app.session_state["is_logged_in"] = True
    app.session_state["username"] = "test"
    app.run()

    audit_nav = next(item for item in app.radio if item.label == "Pilih halaman")
    audit_option = next(option for option in audit_nav.options if "Audit Trail" in option)
    audit_nav.set_value(audit_option).run()

    html = " ".join(str(item.value) for item in app.markdown)
    tab_labels = [item.label for item in app.tabs]

    assert "Audit Trail" in html
    assert tab_labels == ["Aktivitas Sistem", "Pemrosesan Data"]
    assert "Status Data" in html
    assert "Data Siap Dianalisis" in html
    assert "Data Valid" not in html
    assert "Status TK perlu verifikasi" not in html
    assert "Perlu Diperiksa" not in html
    assert "Presensi tidak lengkap" not in html
    assert "Sumber Data Aktif" in html
    assert "Alur Pemrosesan Data" in html
    assert "Ringkasan Pemrosesan Terkini" in html
    assert "Validasi &amp; Isu Data" in html
    assert "Preview Data Hasil Proses" in html
    assert "Waktu pemrosesan terakhir belum tersedia" in html
    assert not app.exception

    raw = load_semua_presensi()
    quality = raw.attrs["etl_quality"]
    tk_total = int(raw["TK"].sum())
    actual_quality_issues = int(quality["duplicates"])
    assert quality["needs_verification"] == tk_total + quality["incomplete"]
    assert f"{actual_quality_issues:,} isu kualitas data nyata".replace(",", ".") in html
    assert f">{tk_total:,}</div><div class='processing-kpi-label'>".replace(",", ".") not in html
    if actual_quality_issues:
        assert "Perlu Pemeriksaan" in html
        assert f"{actual_quality_issues:,} data memerlukan pemeriksaan.".replace(",", ".") in html
    else:
        assert "Proses Selesai" in html
        assert "Data siap digunakan untuk analisis." in html


def test_system_activity_is_a_compact_grouped_timeline():
    app = AppTest.from_file("app.py", default_timeout=30)
    app.session_state["is_logged_in"] = True
    app.session_state["username"] = "test"
    now = pd.Timestamp.now()
    app.session_state["audit_trail"] = [
        {"Waktu": now.strftime("%d/%m %H:%M"), "User": "Admin", "Aktivitas": "Laporan TK PDF diunduh — Triwulan II 2026"},
        {"Waktu": (now - pd.Timedelta(days=1)).strftime("%d/%m %H:%M"), "User": "System", "Aktivitas": "Data presensi berhasil diproses"},
    ]
    app.run()

    audit_nav = next(item for item in app.radio if item.label == "Pilih halaman")
    audit_option = next(option for option in audit_nav.options if "Audit Trail" in option)
    audit_nav.set_value(audit_option).run()

    html = " ".join(str(item.value) for item in app.markdown)
    assert "audit-activity-timeline" in html
    assert "Hari ini" in html
    assert "Kemarin" in html
    assert "Laporan TK PDF diunduh" in html
    assert "Triwulan II 2026" in html
    assert "Data presensi berhasil diproses" in html
    assert "Ringkasan Aktivitas" not in html
    assert "Log Aktivitas" not in html
    assert "Unduh Log CSV" not in html
    assert not any(item.label in {"Periode", "Aktor", "Aktivitas", "Cari"} for item in app.selectbox)
    assert not app.exception
