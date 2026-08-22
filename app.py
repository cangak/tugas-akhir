import pandas as pd
import altair as alt
import streamlit as st


st.set_page_config(
    page_title="EWS Kehadiran Pegawai",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

VALID_USERNAME = "admin"
VALID_PASSWORD = "admin123"
EXTRACTION_TOTAL_PAGES = 500
EXTRACTION_ANOMALY_PAGES = 10


def initialize_session() -> None:
    st.session_state.setdefault("is_logged_in", False)
    st.session_state.setdefault("username", "")


def login(username: str, password: str) -> bool:
    return username == VALID_USERNAME and password == VALID_PASSWORD


def logout() -> None:
    st.session_state.is_logged_in = False
    st.session_state.username = ""
    st.rerun()


def load_employee_data() -> pd.DataFrame:
    """Data contoh absensi yang bisa diganti dengan sumber data instansi."""
    data = pd.DataFrame(
        [
            ["PGW-001", "Andi Pratama", "Administrasi", "Januari", 7, 3, 14, 18, 8.12, "Rabu"],
            ["PGW-002", "Siti Rahma", "Keuangan", "Januari", 4, 1, 9, 20, 7.56, "Senin"],
            ["PGW-003", "Budi Santoso", "Teknologi Informasi", "Januari", 1, 0, 2, 22, 7.38, "Selasa"],
            ["PGW-004", "Dewi Lestari", "Administrasi", "Januari", 0, 0, 1, 22, 7.29, "Kamis"],
            ["PGW-005", "Rizky Maulana", "Keuangan", "Januari", 3, 2, 8, 19, 8.03, "Jumat"],
            ["PGW-006", "Nadia Putri", "Teknologi Informasi", "Januari", 2, 0, 5, 21, 7.47, "Rabu"],
            ["PGW-007", "Fajar Nugroho", "Administrasi", "Februari", 8, 2, 16, 17, 8.18, "Senin"],
            ["PGW-008", "Maya Sari", "Keuangan", "Februari", 5, 1, 11, 19, 7.51, "Selasa"],
            ["PGW-009", "Dimas Saputra", "Teknologi Informasi", "Februari", 1, 0, 3, 21, 7.34, "Rabu"],
            ["PGW-010", "Lina Marlina", "Administrasi", "Februari", 0, 0, 0, 22, 7.25, "Kamis"],
            ["PGW-011", "Arif Hidayat", "Keuangan", "Februari", 3, 1, 7, 20, 7.58, "Jumat"],
            ["PGW-012", "Citra Anggraini", "Teknologi Informasi", "Februari", 2, 0, 4, 21, 7.43, "Senin"],
            ["PGW-013", "Yusuf Kurniawan", "Administrasi", "Maret", 6, 2, 13, 18, 8.08, "Selasa"],
            ["PGW-014", "Rani Wulandari", "Keuangan", "Maret", 4, 0, 10, 20, 7.53, "Rabu"],
            ["PGW-015", "Galang Prakoso", "Teknologi Informasi", "Maret", 1, 0, 2, 22, 7.31, "Kamis"],
            ["PGW-016", "Putri Amelia", "Administrasi", "Maret", 0, 0, 1, 22, 7.27, "Jumat"],
            ["PGW-017", "Hendra Wijaya", "Keuangan", "Maret", 3, 1, 6, 20, 7.49, "Senin"],
            ["PGW-018", "Vina Oktavia", "Teknologi Informasi", "Maret", 2, 0, 5, 21, 7.41, "Selasa"],
        ],
        columns=[
            "NIP", "Nama Pegawai", "Unit Kerja", "Bulan", "TK", "Cuti", "Terlambat",
            "Hari Kerja", "Jam Datang", "Hari Dominan",
        ],
    )
    data["WFH"] = [2, 1, 1, 0, 2, 1, 1, 2, 0, 1, 1, 2, 2, 1, 0, 1, 2, 1]
    data["DL"] = [1, 0, 1, 1, 0, 1, 0, 1, 2, 0, 1, 0, 1, 2, 1, 0, 1, 2]
    data["Jabatan"] = "Pelaksana"
    data["Pangkat/Golongan"] = "III/a"
    return data


def classify_ews(tk: int) -> tuple[str, str]:
    if tk >= 6:
        return "Risiko Tinggi", "🔴"
    if tk >= 3:
        return "Peringatan Dini", "🟠"
    return "Aman", "🟢"


def sanction_recommendation(tk: int) -> str:
    if tk >= 6:
        return "Rekomendasi pemeriksaan disiplin / sanksi administratif"
    if tk >= 3:
        return "Teguran tertulis dan pembinaan atasan langsung"
    return "Monitoring rutin"


def leave_recommendation(cuti: int) -> str:
    if cuti >= 3:
        return "Verifikasi kelengkapan dokumen dan persetujuan cuti"
    return "Administrasi cuti telah dicatat"


def tardiness_recommendation(tardy_count: int) -> str:
    if tardy_count >= 12:
        return "Teguran tertulis dan evaluasi atasan langsung"
    if tardy_count >= 8:
        return "Pembinaan kedisiplinan kehadiran"
    return "Monitoring rutin"


def discipline_zone(tk: int) -> str | None:
    if 3 <= tk <= 10:
        return "Hukuman Disiplin Ringan"
    if 11 <= tk <= 20:
        return "Hukuman Disiplin Sedang"
    if tk >= 21:
        return "Hukuman Disiplin Berat"
    return None


def calculate_risk_score(tk: int, late_count: int) -> int:
    return min(tk * 8 + late_count * 2, 100)


def risk_status(score: int) -> str:
    if score >= 75:
        return "Kritis"
    if score >= 50:
        return "Tinggi"
    if score >= 25:
        return "Waspada"
    return "Normal"


def warning_indicators(tk: int, late_count: int) -> str:
    indicators = []
    if tk >= 3:
        indicators.append(f"TK {tk} hari")
    if late_count >= 8:
        indicators.append(f"Terlambat {late_count} kali")
    return ", ".join(indicators) if indicators else "Tidak ada indikator warning"


def risk_recommendation(status: str) -> str:
    recommendations = {
        "Kritis": "Panggilan klarifikasi dan pemeriksaan disiplin segera",
        "Tinggi": "Teguran tertulis serta pembinaan oleh atasan langsung",
        "Waspada": "Konseling kedisiplinan dan monitoring mingguan",
        "Normal": "Monitoring rutin",
    }
    return recommendations[status]


def build_attendance_calendar(record: pd.Series) -> pd.DataFrame:
    workdays = int(record["Hari Kerja"])
    statuses = (
        ["TK"] * int(record["TK"])
        + ["Cuti"] * int(record["Cuti"])
        + ["WFH"] * int(record["WFH"])
        + ["DL"] * int(record["DL"])
    )
    statuses += ["Hadir"] * max(workdays - len(statuses), 0)
    statuses = statuses[:workdays]
    weekdays = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat"]
    calendar_rows = []
    for start in range(0, workdays, len(weekdays)):
        row = {"Minggu": f"Minggu {start // len(weekdays) + 1}"}
        for day_offset, weekday in enumerate(weekdays):
            index = start + day_offset
            row[weekday] = f"{index + 1}: {statuses[index]}" if index < workdays else "-"
        calendar_rows.append(row)
    return pd.DataFrame(calendar_rows)


def inject_dashboard_css() -> None:
    st.markdown(
        """
        <style>
            header[data-testid="stHeader"] { background: #f7f9fc; }
            .stApp { background: #f7f9fc; color: #172033; }
            [data-testid="stSidebar"] { background: #0f2942; border-right: 1px solid rgba(148,163,184,.18); }
            [data-testid="stSidebar"] * { color: #f8fafc !important; }
            [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] > div,
            [data-testid="stSidebar"] input { background: #173b5e !important; border-color: rgba(148,163,184,.28) !important; }
            [data-testid="stSidebar"] hr { border-color: rgba(148,163,184,.2); margin: .55rem 0; }
            .sidebar-brand { display:flex; align-items:center; gap:.65rem; padding:.25rem .15rem .7rem; }
            .sidebar-brand .brand-icon { display:grid; place-items:center; width:30px; height:30px; font-size:1.35rem; }
            .sidebar-brand .brand-name { font-size:1.02rem; font-weight:800; letter-spacing:.08em; line-height:1.1; }
            .sidebar-brand .brand-subtitle { color:#94a3b8 !important; font-size:.68rem; margin-top:.2rem; }
            .sidebar-nav-title, [data-testid="stSidebar"] .sidebar-filter-title { color:#94a3b8 !important; text-transform:uppercase; letter-spacing:.1em; font-size:.68rem; font-weight:700; margin:.25rem 0 .35rem; }
            [data-testid="stSidebar"] div[role="radiogroup"] { gap:.18rem; }
            [data-testid="stSidebar"] div[role="radiogroup"] label { border-radius:9px; padding:.48rem .6rem; margin:0; transition:background .15s ease; }
            [data-testid="stSidebar"] div[role="radiogroup"] label:hover { background:#173b5e; }
            [data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) { background:#2563eb; box-shadow:0 4px 12px rgba(37,99,235,.22); }
            [data-testid="stSidebar"] div[role="radiogroup"] label > div:first-child { display:none; }
            [data-testid="stSidebar"] .stSelectbox, [data-testid="stSidebar"] .stTextInput { margin-bottom:.35rem; }
            [data-testid="stSidebar"] .stSelectbox label, [data-testid="stSidebar"] .stTextInput label { color:#cbd5e1 !important; font-size:.75rem; }
            [data-testid="stSidebar"] .stButton button { background:#2563eb; border:0; border-radius:8px; font-weight:700; }
            .block-container { padding-top: 1.6rem; padding-bottom: 2rem; }
            .dashboard-title { font-size: 2.35rem; line-height: 1.15; font-weight: 800; color: #102a43; text-align: center; letter-spacing: -.02em; margin: .2rem 0 .35rem; }
            .dashboard-subtitle { color: #64748b; text-align: center; font-size: .98rem; margin: 0 0 1.5rem; }
            .section-title { color: #173b61; font-size: 1.1rem; font-weight: 700; margin: 1.3rem 0 .45rem; }
            .ews-card { padding: 1rem 1.15rem; border-radius: 12px; min-height: 116px; border: 1px solid; }
            .ews-card .label { font-size: .87rem; font-weight: 650; opacity: .82; }
            .ews-card .number { font-size: 2rem; font-weight: 800; line-height: 1.25; }
            .ews-card .detail { font-size: .8rem; opacity: .8; }
            .red { background: #fff1f2; border-color: #fecdd3; color: #9f1239; }
            .yellow { background: #fefce8; border-color: #fde68a; color: #854d0e; }
            .orange { background: #fff7ed; border-color: #fed7aa; color: #9a3412; }
            .green { background: #ecfdf5; border-color: #a7f3d0; color: #065f46; }
            .legend { display: flex; gap: 16px; flex-wrap: wrap; color: #475569; font-size: .85rem; padding: .35rem 0 .8rem; }
            .legend span { display: inline-flex; align-items: center; gap: 6px; }
            .legend i { height: 10px; width: 10px; border-radius: 50%; display: inline-block; }
            .note { color: #64748b; font-size: .8rem; margin-top: -.3rem; }
            .stDataFrame { border: 1px solid #e2e8f0; border-radius: 8px; }
            .discipline-funnel { display: flex; flex-direction: column; align-items: center; gap: 7px; padding: .75rem 0; }
            .funnel-level { min-height: 62px; display: flex; align-items: center; justify-content: space-between; gap: .8rem; padding: .7rem 1rem; color: white; border-radius: 8px; box-sizing: border-box; }
            .funnel-level strong, .funnel-level span { color: white; }
            .funnel-level span { font-size: .86rem; text-align: right; }
            .funnel-light { background: #f59e0b; }
            .funnel-medium { background: #f97316; }
            .funnel-heavy { background: #dc2626; }
            .target-kpi-card { background: #111827; color: #f8fafc; border-radius: 10px; padding: 1.15rem 1.25rem; }
            .target-kpi-card .kpi-title { color: #f8fafc; font-size: 1.05rem; font-weight: 700; margin-bottom: .65rem; }
            .target-kpi-card p { color: #f8fafc; font-size: 1rem; margin: .3rem 0; }
            .target-kpi-card .kpi-gap { font-weight: 700; }
            .target-kpi-card .kpi-dot { display: inline-block; width: 14px; height: 14px; border-radius: 50%; margin-left: 6px; vertical-align: -1px; }
            .target-kpi-card .negative { background: #f43f5e; }
            .target-kpi-card .positive { background: #22c55e; }
            .composition-list { display: grid; grid-template-columns: repeat(4, minmax(130px, 1fr)); gap: .65rem; width: 100%; }
            .composition-row { display: flex; flex-direction: column; justify-content: center; min-height: 66px; padding: .65rem .8rem; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; }
            .composition-row .composition-label { color: #475569; font-size: .92rem; }
            .composition-row .composition-value { color: #102a43; font-size: 1rem; font-weight: 700; }
            .composition-bars { margin-top: .8rem; }
            .composition-bar-row { display: grid; grid-template-columns: 110px 1fr 55px; align-items: center; gap: .55rem; margin: .45rem 0; }
            .composition-bar-label, .composition-bar-value { color: #475569; font-size: .82rem; }
            .composition-bar-value { color: #102a43; font-weight: 700; text-align: right; }
            .composition-bar-track { height: 12px; background: #e2e8f0; border-radius: 99px; overflow: hidden; }
            .composition-bar-fill { height: 100%; border-radius: 99px; }
            .individual-kpi-grid { display: grid; grid-template-columns: repeat(5, minmax(130px, 1fr)); gap: .65rem; }
            .individual-kpi-card { min-width: 0; padding: .75rem .8rem; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; }
            .individual-kpi-card .label { color: #64748b; font-size: .78rem; margin-bottom: .3rem; }
            .individual-kpi-card .value { color: #102a43; font-size: 1rem; font-weight: 700; line-height: 1.25; overflow-wrap: anywhere; }
            .page-context-grid { display: grid; grid-template-columns: 1fr; justify-items: center; gap: .6rem; margin: .25rem 0 1.25rem; }
            .page-context-card { width: fit-content; max-width: 100%; box-sizing: border-box; padding: .8rem 1rem; border: 1px solid #dbe4ee; border-radius: 9px; background: #ffffff; color: #64748b; font-size: .92rem; text-align: center; white-space: nowrap; }
            .page-context-card.risk-context-card { color: #102a43; font-size: 1.05rem; font-weight: 750; }
            .hero-subtitle { color:#64748b; text-align:center; font-size:1rem; margin:-.15rem 0 .8rem; }
            .hero-filters { display:flex; justify-content:center; gap:.7rem; flex-wrap:wrap; margin:0 auto 1.15rem; }
            .hero-filter-chip { background:#fff; border:1px solid #dbe4ee; border-radius:8px; padding:.5rem .9rem; color:#334e68; font-size:.84rem; box-shadow:0 2px 7px rgba(15,41,66,.05); }
            .hero-filter-chip strong { color:#102a43; }
            .hero-kpi-grid { display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:.8rem; margin-bottom:1.25rem; }
            .hero-kpi-card { display:flex; align-items:center; gap:.65rem; min-width:0; padding:.9rem 1rem; background:#fff; border:1px solid #dbe4ee; border-radius:11px; box-shadow:0 3px 12px rgba(15,41,66,.06); }
            .hero-kpi-icon { font-size:1.35rem; line-height:1; }
            .hero-kpi-value { color:#102a43; font-size:1.42rem; font-weight:800; line-height:1.1; }
            .hero-kpi-label { color:#64748b; font-size:.78rem; margin-top:.2rem; white-space:nowrap; }
            .hero-kpi-card.warning { border-left:4px solid #f59e0b; }
            .hero-kpi-card.critical { border-left:4px solid #ef4444; }
            .trend-target-note { margin-top:.35rem; text-align:center; color:#64748b; font-size:.82rem; }
            .trend-target-note span { color:#f59e0b; margin:0 .35rem; }
            .trend-summary-grid { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:.65rem; margin:.2rem 0 .75rem; }
            .trend-summary-card { background:#fff; border:1px solid #dbe4ee; border-radius:9px; padding:.65rem .8rem; text-align:center; box-shadow:0 2px 8px rgba(15,41,66,.04); }
            .trend-summary-label { color:#64748b; font-size:.74rem; }
            .trend-summary-value { color:#173b5e; font-size:1.12rem; font-weight:800; margin-top:.15rem; }
            .trend-summary-value.warning { color:#c2410c; }
            .trend-summary-value.positive { color:#047857; }
            .trend-summary-value.negative { color:#dc2626; }
            .ews-page-title { display:block !important; visibility:visible !important; color:#173b63 !important; font-size:1.7rem !important; font-weight:800 !important; line-height:1.2; margin:.1rem 0 .15rem; text-align:left; }
            .ews-page-subtitle { color:#64748b; font-size:.92rem; margin:0 0 .7rem; }
            .ews-filter-row { display:flex; justify-content:space-between; align-items:center; gap:.7rem; flex-wrap:wrap; padding:.55rem .8rem; border-top:1px solid #dbe4ee; border-bottom:1px solid #dbe4ee; margin-bottom:1rem; color:#64748b; font-size:.84rem; }
            .ews-filter-chip { background:#fff; border:1px solid #dbe4ee; border-radius:7px; padding:.38rem .75rem; }
            .ews-status-banner { background:#fff7ed; border:1px solid #fed7aa; border-left:4px solid #f97316; border-radius:9px; padding:.75rem 1rem; margin:.25rem 0 1rem; }
            .ews-status-banner .status-label { color:#c2410c; font-size:.78rem; font-weight:800; letter-spacing:.06em; }
            .ews-status-banner .status-value { color:#9a3412; font-size:1.2rem; font-weight:800; margin:.15rem 0; }
            .ews-status-banner .status-detail { color:#7c2d12; font-size:.84rem; }
            .ews-header-risk { background:#ecfdf5; border:1px solid #a7f3d0; border-left:4px solid #10b981; border-radius:9px; padding:.7rem 1rem; margin:.2rem 0 .85rem; }
            .ews-header-risk .risk-label { color:#047857; font-size:.88rem; font-weight:800; }
            .ews-header-risk .risk-count { color:#065f46; font-size:1.12rem; font-weight:800; margin:.15rem 0; }
            .ews-header-risk .risk-change { color:#047857; font-size:.82rem; }
            .ews-risk-summary .ews-card { min-height:100px; background:#fff !important; }
            .ews-risk-summary .green { border-top:3px solid #10b981; }
            .ews-risk-summary .yellow { border-top:3px solid #f59e0b; }
            .ews-risk-summary .orange { border-top:3px solid #f97316; }
            .ews-risk-summary .red { border-top:3px solid #e11d48; }
            .ews-risk-summary .detail { font-size:.78rem; }
            .verified-badge { display:inline-block; padding:.35rem .75rem; border-radius:999px; background:#dbeafe; color:#1d4ed8; font-weight:800; font-size:.8rem; margin:.2rem 0 .55rem; }
            @media (max-width: 700px) { .trend-summary-grid { grid-template-columns:1fr; } }
            @media (max-width: 900px) { .hero-kpi-grid { grid-template-columns:repeat(2,minmax(0,1fr)); } }
            @media (max-width: 900px) { .individual-kpi-grid { grid-template-columns: repeat(2, minmax(130px, 1fr)); } .composition-list { grid-template-columns: repeat(2, minmax(130px, 1fr)); } }
        </style>
        """,
        unsafe_allow_html=True,
    )


def show_login_page() -> None:
    st.markdown(
        """
        <style>
            .stApp { background: linear-gradient(135deg, #0b2545, #1d4e75); }
            header[data-testid="stHeader"] { background: transparent; }
            .login-box { box-sizing: border-box; width: min(92vw, 440px); margin: 11vh auto 0; padding: 2.3rem 2.3rem 1rem; background: white; border-radius: 16px 16px 0 0; box-shadow: 0 16px 45px rgba(0,0,0,.2); }
            .login-box h1 { color: #102a43; font-size: 1.65rem; margin-bottom: .2rem; }
            .login-box p { color: #64748b; }
            div[data-testid="stForm"] { box-sizing: border-box; width: min(92vw, 440px); margin: 0 auto; padding: 1rem 2.3rem 2.3rem; border: 0; border-radius: 0 0 16px 16px; background: white; box-shadow: 0 16px 45px rgba(0,0,0,.2); }
            div[data-testid="stForm"] > div { border: 0; padding: 0; }
        </style>
        <div class="login-box"><h1>🛡️ EWS Kehadiran</h1><p>Masuk untuk memantau disiplin kehadiran pegawai.</p></div>
        """,
        unsafe_allow_html=True,
    )
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Kata sandi", type="password")
        submitted = st.form_submit_button("Masuk", use_container_width=True)
    if submitted:
        if login(username, password):
            st.session_state.is_logged_in = True
            st.session_state.username = username
            st.rerun()
        st.error("Username atau kata sandi salah.")
    st.caption("Akun demo: admin / admin123")


def show_dashboard_legacy() -> None:
    inject_dashboard_css()
    data = load_employee_data()
    month_order = ["Januari", "Februari", "Maret"]

    with st.sidebar:
        st.markdown("# 🛡️ EWS Kehadiran")
        st.caption("Sistem peringatan dini disiplin pegawai")
        st.divider()
        st.markdown("#### Filter Data")
        chosen_month = st.selectbox("Periode bulan", month_order)
        violation_options = {
            "Semua jenis": None,
            "Tanpa Keterangan (TK)": "TK",
            "Cuti": "Cuti",
            "Terlambat": "Terlambat",
        }
        chosen_violation = st.selectbox("Jenis ketidakhadiran", violation_options.keys())
        units = ["Semua Unit"] + sorted(data["Unit Kerja"].unique().tolist())
        chosen_unit = st.selectbox("Unit kerja", units)
        search_name = st.text_input("Cari nama atau NIP", placeholder="Ketik untuk mencari")
        st.divider()
        st.markdown("#### Keterangan Status")
        st.markdown("🔴 **Risiko Tinggi**  \\n+TK ≥ 6 hari")
        st.markdown("🟠 **Peringatan Dini**  \\n+TK 3–5 hari")
        st.markdown("🟢 **Aman**  \\n+TK 0–2 hari")
        st.divider()
        st.caption(f"Login sebagai: {st.session_state.username}")
        st.button("Keluar", on_click=logout, use_container_width=True)

    filtered = data[data["Bulan"] == chosen_month].copy()
    violation_column = violation_options[chosen_violation]
    if violation_column:
        filtered = filtered[filtered[violation_column] > 0]
    if chosen_unit != "Semua Unit":
        filtered = filtered[filtered["Unit Kerja"] == chosen_unit]
    if search_name:
        query = search_name.lower()
        filtered = filtered[
            filtered["Nama Pegawai"].str.lower().str.contains(query)
            | filtered["NIP"].str.lower().str.contains(query)
        ]

    filtered[["Status", "Ikon"]] = filtered["TK"].apply(lambda value: pd.Series(classify_ews(value)))
    filtered["Rekomendasi"] = filtered["TK"].apply(sanction_recommendation)

    st.markdown("<h1 class='dashboard-title' style='display:block!important;visibility:visible!important;color:#102a43!important;text-align:center!important;font-size:2.35rem!important;font-weight:800!important;'>Executive Dashboard</h1>", unsafe_allow_html=True)
    st.markdown(f"<p class='dashboard-subtitle'>Monitoring kehadiran pegawai • Periode: {chosen_month}</p>", unsafe_allow_html=True)

    total_employees = filtered["NIP"].nunique()
    total_workdays = int(filtered["Hari Kerja"].sum())
    total_tk = int(filtered["TK"].sum())
    total_leave = int(filtered["Cuti"].sum())
    attendance_rate = (
        max(total_workdays - total_tk - total_leave, 0) / total_workdays * 100
        if total_workdays
        else 0
    )
    total_late = int(filtered["Terlambat"].sum())
    at_risk = int(filtered["Status"].isin(["Risiko Tinggi", "Peringatan Dini"]).sum())

    st.markdown("<div class='section-title'>Ringkasan Eksekutif</div>", unsafe_allow_html=True)
    executive_1, executive_2, executive_3, executive_4, executive_5 = st.columns(5)
    executive_1.metric("Total Pegawai", f"{total_employees}")
    executive_2.metric("Persentase Kehadiran", f"{attendance_rate:.1f}%")
    executive_3.metric("TK", f"{total_tk} hari", help="Total hari tanpa keterangan pada data terfilter.")
    executive_4.metric("Keterlambatan", f"{total_late} kali")
    executive_5.metric("Pegawai Berisiko", f"{at_risk}", help="Pegawai berstatus Risiko Tinggi atau Peringatan Dini.")

    trend_source = data if chosen_unit == "Semua Unit" else data[data["Unit Kerja"] == chosen_unit]
    attendance_trend = trend_source.groupby("Bulan").apply(
        lambda group: max(group["Hari Kerja"].sum() - group["TK"].sum() - group["Cuti"].sum(), 0)
        / group["Hari Kerja"].sum()
        * 100,
        include_groups=False,
    ).reindex(month_order).rename("Persentase Kehadiran")
    opd_ranking = filtered.groupby("Unit Kerja").agg(
        Pegawai=("NIP", "nunique"),
        Hari_Kerja=("Hari Kerja", "sum"),
        TK_TB=("TK", "sum"),
        Cuti=("Cuti", "sum"),
    )
    opd_ranking["Kehadiran"] = (
        (opd_ranking["Hari_Kerja"] - opd_ranking["TK_TB"] - opd_ranking["Cuti"])
        / opd_ranking["Hari_Kerja"]
        * 100
    ).clip(lower=0)
    opd_ranking = opd_ranking.sort_values("Kehadiran", ascending=False).reset_index()
    opd_ranking.index = opd_ranking.index + 1
    opd_ranking.index.name = "Peringkat"

    executive_left, executive_right = st.columns([1.25, 1])
    with executive_left:
        st.caption("Tren Kehadiran — persentase kehadiran bulanan (semakin tinggi semakin baik)")
        st.line_chart(attendance_trend, color="#059669", height=260)
    with executive_right:
        st.caption("Ranking OPD — berdasarkan persentase kehadiran pada periode terfilter")
        st.dataframe(
            opd_ranking[["Unit Kerja", "Pegawai", "Kehadiran", "TK_TB"]],
            use_container_width=True,
            column_config={
                "Kehadiran": st.column_config.NumberColumn("Kehadiran", format="%.1f%%"),
                "TK_TB": st.column_config.NumberColumn("TK", format="%d hari"),
            },
        )

    successful_pages = EXTRACTION_TOTAL_PAGES - EXTRACTION_ANOMALY_PAGES
    success_rate = successful_pages / EXTRACTION_TOTAL_PAGES * 100
    anomaly_rate = EXTRACTION_ANOMALY_PAGES / EXTRACTION_TOTAL_PAGES * 100
    st.info(
        f"**Kualitas ekstraksi data:** Total {EXTRACTION_TOTAL_PAGES} halaman diproses — "
        f"**{success_rate:.0f}% berhasil diurai** ({successful_pages} halaman), "
        f"**{anomaly_rate:.0f}% terdapat anomali format** ({EXTRACTION_ANOMALY_PAGES} halaman)."
    )

    high = int((filtered["Status"] == "Risiko Tinggi").sum())
    warning = int((filtered["Status"] == "Peringatan Dini").sum())
    safe = int((filtered["Status"] == "Aman").sum())
    total_tk = int(filtered["TK"].sum())

    st.markdown("<div class='section-title'>Ringkasan Early Warning System</div>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(f"<div class='ews-card red'><div class='label'>🔴 RISIKO TINGGI</div><div class='number'>{high}</div><div class='detail'>Pegawai perlu ditindaklanjuti</div></div>", unsafe_allow_html=True)
    c2.markdown(f"<div class='ews-card orange'><div class='label'>🟠 PERINGATAN DINI</div><div class='number'>{warning}</div><div class='detail'>Perlu pembinaan segera</div></div>", unsafe_allow_html=True)
    c3.markdown(f"<div class='ews-card green'><div class='label'>🟢 STATUS AMAN</div><div class='number'>{safe}</div><div class='detail'>Pegawai sesuai ketentuan</div></div>", unsafe_allow_html=True)
    c4.metric("Total Hari Tanpa Keterangan", f"{total_tk} hari", help="Akumulasi hari tanpa keterangan pada data terfilter.")

    st.markdown("<div class='legend'><span><i style='background:#e11d48'></i>Risiko Tinggi (TK ≥ 6)</span><span><i style='background:#f97316'></i>Peringatan Dini (TK 3–5)</span><span><i style='background:#10b981'></i>Aman (TK 0–2)</span></div>", unsafe_allow_html=True)

    zone_counts = filtered["TK"].apply(discipline_zone).value_counts()
    zone_definitions = [
        ("Hukuman Disiplin Ringan", "3–10 hari", "funnel-light", "100%"),
        ("Hukuman Disiplin Sedang", "11–20 hari", "funnel-medium", "78%"),
        ("Hukuman Disiplin Berat", "≥ 21 hari", "funnel-heavy", "56%"),
    ]
    funnel_levels = "".join(
        f"<div class='funnel-level {style}' style='width:{width}'><strong>{name}</strong><span>{int(zone_counts.get(name, 0))} ASN<br>{range_label}</span></div>"
        for name, range_label, style, width in zone_definitions
    )
    st.markdown("<div class='section-title'>Zona Hukuman Disiplin ASN</div>", unsafe_allow_html=True)
    st.caption("Pembagian berdasarkan akumulasi hari tanpa keterangan (TK) pada data yang sedang difilter.")
    st.markdown(f"<div class='discipline-funnel'>{funnel_levels}</div>", unsafe_allow_html=True)
    st.caption("Klik salah satu zona untuk melihat daftar pegawai dan tindak lanjutnya.")
    light_tab, medium_tab, heavy_tab = st.tabs(
        ["Ringan (3–10 hari)", "Sedang (11–20 hari)", "Berat (≥ 21 hari)"]
    )
    for tab, zone_name in [
        (light_tab, "Hukuman Disiplin Ringan"),
        (medium_tab, "Hukuman Disiplin Sedang"),
        (heavy_tab, "Hukuman Disiplin Berat"),
    ]:
        with tab:
            zone_table = filtered[filtered["TK"].apply(discipline_zone) == zone_name].copy()
            zone_table["Tindak Lanjut"] = zone_table["TK"].apply(sanction_recommendation)
            zone_table = zone_table.sort_values(["TK", "Nama Pegawai"], ascending=[False, True])[
                ["NIP", "Nama Pegawai", "Unit Kerja", "TK", "Tindak Lanjut"]
            ]
            if zone_table.empty:
                st.info(f"Belum ada pegawai dalam zona {zone_name.lower()}.")
            else:
                st.dataframe(
                    zone_table,
                    hide_index=True,
                    use_container_width=True,
                    column_config={
                        "TK": st.column_config.NumberColumn("Hari Tidak Hadir", format="%d hari"),
                        "Tindak Lanjut": st.column_config.TextColumn("Tindak Lanjut", width="large"),
                    },
                )

    st.markdown("<div class='section-title'>Analisis Perilaku Kehadiran</div>", unsafe_allow_html=True)
    left, right = st.columns(2)
    weekdays = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat"]
    with left:
        st.caption("Day-of-Week Analysis — total keterlambatan per hari")
        day_chart = filtered.groupby("Hari Dominan")["Terlambat"].sum().reindex(weekdays, fill_value=0)
        st.bar_chart(day_chart, color="#2563eb", height=290)
    with right:
        st.caption("Peak Hour Distribution — distribusi jam kedatangan")
        arrival_bins = pd.cut(filtered["Jam Datang"], bins=[6.99, 7.29, 7.44, 7.59, 7.74, 7.89, 8.5], labels=["≤ 07.29", "07.30–07.44", "07.45–07.59", "08.00–08.14", "08.15–08.29", "≥ 08.30"])
        hour_chart = arrival_bins.value_counts().sort_index()
        st.bar_chart(hour_chart, color="#7c3aed", height=290)
    st.markdown("<p class='note'>Analisis ini membantu mengidentifikasi pola keterlambatan dan jam kedatangan yang paling sering terjadi.</p>", unsafe_allow_html=True)

    st.markdown("<div class='section-title'>Tren Kedisiplinan Unit Kerja</div>", unsafe_allow_html=True)
    trend_source = data if chosen_unit == "Semua Unit" else data[data["Unit Kerja"] == chosen_unit]
    trend_chart = (
        trend_source.groupby("Bulan")["TK"]
        .mean()
        .reindex(month_order)
        .rename("Rata-rata TK per Pegawai")
    )
    trend_name = "seluruh unit kerja" if chosen_unit == "Semua Unit" else chosen_unit
    first_value, last_value = trend_chart.iloc[0], trend_chart.iloc[-1]
    if last_value < first_value:
        trend_status = "membaik"
    elif last_value > first_value:
        trend_status = "memburuk"
    else:
        trend_status = "stabil"
    st.caption(
        f"Tren {trend_name}. Nilai rata-rata TK yang menurun menunjukkan kedisiplinan membaik; "
        f"tren saat ini: **{trend_status}**."
    )
    st.line_chart(trend_chart, color="#e11d48", height=300)

    st.markdown("<div class='section-title'>Antrian Tindak Lanjut</div>", unsafe_allow_html=True)
    queue_cols = st.columns(3)
    queue_cols[0].metric("🔴 Belum diproses", warning_total)
    queue_cols[1].metric("🟡 Dalam verifikasi", 0)
    queue_cols[2].metric("🟢 Selesai", 0)
    if st.button("Buka Action Center →", key="open_action_center_from_ews"):
        st.session_state["navigate_to_page"] = "Action Center"
        st.rerun()

    st.markdown("<div class='section-title'>Detail & Tindakan Warning</div>", unsafe_allow_html=True)
    tab_tk, tab_cuti, tab_terlambat = st.tabs(["Tanpa Keterangan", "Cuti", "Keterlambatan"])

    with tab_tk:
        st.caption("Diurutkan berdasarkan akumulasi hari tanpa keterangan (TK) tertinggi.")
        tk_table = filtered[filtered["TK"] > 0].sort_values(["TK", "Nama Pegawai"], ascending=[False, True])[
            ["NIP", "Nama Pegawai", "Unit Kerja", "TK", "Status", "Rekomendasi"]
        ]
        st.dataframe(
            tk_table,
            hide_index=True,
            use_container_width=True,
            column_config={
                "TK": st.column_config.NumberColumn("Hari TK", format="%d hari"),
                "Status": st.column_config.TextColumn("Status EWS", width="medium"),
                "Rekomendasi": st.column_config.TextColumn("Rekomendasi Tindak Lanjut", width="large"),
            },
        )

    with tab_cuti:
        st.caption("Cuti memerlukan verifikasi administrasi dan bukan sanksi otomatis.")
        cuti_table = filtered[filtered["Cuti"] > 0].copy()
        cuti_table["Tindak Lanjut Cuti"] = cuti_table["Cuti"].apply(leave_recommendation)
        cuti_table = cuti_table.sort_values(["Cuti", "Nama Pegawai"], ascending=[False, True])[
            ["NIP", "Nama Pegawai", "Unit Kerja", "Cuti", "Tindak Lanjut Cuti"]
        ]
        st.dataframe(
            cuti_table,
            hide_index=True,
            use_container_width=True,
            column_config={
                "Cuti": st.column_config.NumberColumn("Hari Cuti", format="%d hari"),
                "Tindak Lanjut Cuti": st.column_config.TextColumn("Tindak Lanjut", width="large"),
            },
        )

    with tab_terlambat:
        st.caption("Diurutkan berdasarkan frekuensi keterlambatan tertinggi.")
        tardy_table = filtered[filtered["Terlambat"] > 0].copy()
        tardy_table["Rekomendasi"] = tardy_table["Terlambat"].apply(tardiness_recommendation)
        tardy_table = tardy_table.sort_values(["Terlambat", "Nama Pegawai"], ascending=[False, True])[
            ["NIP", "Nama Pegawai", "Unit Kerja", "Terlambat", "Rekomendasi"]
        ]
        st.dataframe(
            tardy_table,
            hide_index=True,
            use_container_width=True,
            column_config={
                "Terlambat": st.column_config.NumberColumn("Jumlah Terlambat", format="%d kali"),
                "Rekomendasi": st.column_config.TextColumn("Rekomendasi Tindak Lanjut", width="large"),
            },
        )


def show_early_warning_page_legacy() -> None:
    inject_dashboard_css()
    data = load_employee_data()
    month_order = ["Januari", "Februari", "Maret"]

    with st.sidebar:
        st.markdown("# 🛡️ EWS Kehadiran")
        st.caption("Sistem peringatan dini disiplin pegawai")
        st.divider()
        st.markdown("#### Filter Early Warning")
        chosen_month = st.selectbox("Periode bulan", month_order, key="ews_month")
        absence_options = {
            "Semua jenis": None,
            "Tanpa Keterangan (TK)": "TK",
            "Cuti": "Cuti",
            "Terlambat": "Terlambat",
        }
        chosen_absence = st.selectbox("Jenis ketidakhadiran", absence_options.keys(), key="ews_absence")
        units = ["Semua Unit"] + sorted(data["Unit Kerja"].unique().tolist())
        chosen_unit = st.selectbox("Unit kerja", units, key="ews_unit")
        search_name = st.text_input("Cari nama atau NIP", placeholder="Ketik untuk mencari", key="ews_search")
        st.divider()
        st.caption(f"Login sebagai: {st.session_state.username}")
        st.button("Keluar", on_click=logout, use_container_width=True, key="ews_logout")

    filtered = data[data["Bulan"] == chosen_month].copy()
    absence_column = absence_options[chosen_absence]
    if absence_column:
        filtered = filtered[filtered[absence_column] > 0]
    if chosen_unit != "Semua Unit":
        filtered = filtered[filtered["Unit Kerja"] == chosen_unit]
    if search_name:
        query = search_name.lower()
        filtered = filtered[
            filtered["Nama Pegawai"].str.lower().str.contains(query)
            | filtered["NIP"].str.lower().str.contains(query)
        ]

    risk_data = filtered.copy()
    risk_data["Risk Score"] = risk_data.apply(
        lambda row: calculate_risk_score(row["TK"], row["Terlambat"]), axis=1
    )
    risk_data["Status Risiko"] = risk_data["Risk Score"].apply(risk_status)
    risk_data["Indikator Warning"] = risk_data.apply(
        lambda row: warning_indicators(row["TK"], row["Terlambat"]), axis=1
    )
    risk_data["Rekomendasi"] = risk_data["Status Risiko"].apply(risk_recommendation)

    status_order = ["Normal", "Waspada", "Tinggi", "Kritis"]
    status_counts = risk_data["Status Risiko"].value_counts().reindex(status_order, fill_value=0)
    average_risk = risk_data["Risk Score"].mean() if not risk_data.empty else 0

    st.markdown("<h1 class='dashboard-title'>Early Warning System</h1>", unsafe_allow_html=True)
    st.markdown(
        f"<p class='dashboard-subtitle'>Analisis risiko kehadiran pegawai • Periode: {chosen_month}</p>",
        unsafe_allow_html=True,
    )
    risk_metric, normal_metric, alert_metric, high_metric, critical_metric = st.columns(5)
    risk_metric.metric("Risk Score Rata-rata", f"{average_risk:.0f}/100")
    normal_metric.metric("Normal", int(status_counts["Normal"]))
    alert_metric.metric("Waspada", int(status_counts["Waspada"]))
    high_metric.metric("Tinggi", int(status_counts["Tinggi"]))
    critical_metric.metric("Kritis", int(status_counts["Kritis"]))

    st.markdown("<div class='section-title'>Jumlah Pegawai per Kategori Risiko</div>", unsafe_allow_html=True)
    st.bar_chart(status_counts.rename("Jumlah Pegawai"), color="#dc2626", height=240)

    cause_col, action_col = st.columns(2)
    with cause_col:
        st.markdown("<div class='section-title'>Indikator Penyebab Warning</div>", unsafe_allow_html=True)
        indicator_summary = pd.DataFrame(
            {
                "Indikator": ["TK ≥ 3 hari", "Terlambat ≥ 8 kali"],
                "Jumlah Pegawai": [
                    int((risk_data["TK"] >= 3).sum()),
                    int((risk_data["Terlambat"] >= 8).sum()),
                ],
            }
        )
        st.dataframe(indicator_summary, hide_index=True, use_container_width=True)
    with action_col:
        st.markdown("<div class='section-title'>Panduan Tindak Lanjut</div>", unsafe_allow_html=True)
        st.markdown("- **Kritis:** pemeriksaan disiplin segera.\n- **Tinggi:** teguran tertulis dan pembinaan.\n- **Waspada:** konseling serta monitoring mingguan.\n- **Normal:** monitoring rutin.")

    st.markdown("<div class='section-title'>Daftar Pegawai Berisiko</div>", unsafe_allow_html=True)
    st.caption("Pegawai berstatus Waspada, Tinggi, atau Kritis; diurutkan dari Risk Score tertinggi.")
    risk_table = risk_data[risk_data["Status Risiko"] != "Normal"].sort_values(
        ["Risk Score", "Nama Pegawai"], ascending=[False, True]
    )[
        ["NIP", "Nama Pegawai", "Unit Kerja", "Risk Score", "Status Risiko", "Indikator Warning", "Rekomendasi"]
    ]
    if risk_table.empty:
        st.success("Tidak ada pegawai berisiko pada filter yang dipilih.")
    else:
        st.dataframe(
            risk_table,
            hide_index=True,
            use_container_width=True,
            column_config={
                "Risk Score": st.column_config.NumberColumn("Risk Score", format="%d/100"),
                "Status Risiko": st.column_config.TextColumn("Status", width="medium"),
                "Indikator Warning": st.column_config.TextColumn("Penyebab Warning", width="large"),
                "Rekomendasi": st.column_config.TextColumn("Rekomendasi Tindak Lanjut", width="large"),
            },
        )


def show_attendance_analysis_page_legacy() -> None:
    inject_dashboard_css()
    data = load_employee_data()
    month_order = ["Januari", "Februari", "Maret"]

    with st.sidebar:
        st.markdown("# 🛡️ EWS Kehadiran")
        st.caption("Analisis presensi pegawai")
        st.divider()
        st.markdown("#### Filter Analisis")
        chosen_month = st.selectbox("Periode bulan", month_order, key="attendance_month")
        units = ["Semua Unit"] + sorted(data["Unit Kerja"].unique().tolist())
        chosen_unit = st.selectbox("Unit kerja", units, key="attendance_unit")
        search_name = st.text_input("Cari nama atau NIP", placeholder="Ketik untuk mencari", key="attendance_search")
        st.divider()
        st.caption(f"Login sebagai: {st.session_state.username}")
        st.button("Keluar", on_click=logout, use_container_width=True, key="attendance_logout")

    filtered = data[data["Bulan"] == chosen_month].copy()
    if chosen_unit != "Semua Unit":
        filtered = filtered[filtered["Unit Kerja"] == chosen_unit]
    if search_name:
        query = search_name.lower()
        filtered = filtered[
            filtered["Nama Pegawai"].str.lower().str.contains(query)
            | filtered["NIP"].str.lower().str.contains(query)
        ]

    filtered["Hadir"] = (
        filtered["Hari Kerja"] - filtered["TK"] - filtered["Cuti"] - filtered["WFH"] - filtered["DL"]
    ).clip(lower=0)

    st.markdown("<p class='dashboard-title'>Analisis Presensi</p>", unsafe_allow_html=True)
    st.markdown(
        f"<p class='dashboard-subtitle'>Ringkasan presensi pegawai • Periode: {chosen_month}</p>",
        unsafe_allow_html=True,
    )
    attendance_totals = {
        "Hadir": int(filtered["Hadir"].sum()),
        "TK": int(filtered["TK"].sum()),
        "WFH": int(filtered["WFH"].sum()),
        "DL": int(filtered["DL"].sum()),
        "Cuti": int(filtered["Cuti"].sum()),
        "Keterlambatan": int(filtered["Terlambat"].sum()),
    }
    metric_columns = st.columns(6)
    for column, (label, value) in zip(metric_columns, attendance_totals.items()):
        unit_label = "kali" if label == "Keterlambatan" else "hari"
        column.metric(label, f"{value} {unit_label}")

    day_col, peak_col = st.columns(2)
    with day_col:
        st.markdown("<div class='section-title'>Day-of-Week Analysis</div>", unsafe_allow_html=True)
        st.caption("Total TK dan keterlambatan berdasarkan hari yang paling dominan.")
        weekdays = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat"]
        day_analysis = filtered.groupby("Hari Dominan")[["TK", "Terlambat"]].sum().reindex(weekdays, fill_value=0)
        st.bar_chart(day_analysis, height=300)
    with peak_col:
        st.markdown("<div class='section-title'>Peak Hour Analysis</div>", unsafe_allow_html=True)
        st.caption("Distribusi jam kedatangan pegawai pada data terfilter.")
        arrival_bins = pd.cut(
            filtered["Jam Datang"],
            bins=[6.99, 7.29, 7.44, 7.59, 7.74, 7.89, 8.5],
            labels=["≤ 07.29", "07.30–07.44", "07.45–07.59", "08.00–08.14", "08.15–08.29", "≥ 08.30"],
        )
        peak_analysis = arrival_bins.value_counts().sort_index().rename("Jumlah Pegawai")
        st.bar_chart(peak_analysis, color="#7c3aed", height=300)

    st.markdown("<div class='section-title'>Rincian Data Presensi</div>", unsafe_allow_html=True)
    attendance_table = filtered.sort_values("Nama Pegawai")[
        ["NIP", "Nama Pegawai", "Unit Kerja", "Hadir", "TK", "WFH", "DL", "Cuti", "Terlambat"]
    ]
    st.dataframe(
        attendance_table,
        hide_index=True,
        use_container_width=True,
        column_config={
            "Hadir": st.column_config.NumberColumn("Hadir", format="%d hari"),
            "TK": st.column_config.NumberColumn("TK", format="%d hari"),
            "WFH": st.column_config.NumberColumn("WFH", format="%d hari"),
            "DL": st.column_config.NumberColumn("DL", format="%d hari"),
            "Cuti": st.column_config.NumberColumn("Cuti", format="%d hari"),
            "Terlambat": st.column_config.NumberColumn("Keterlambatan", format="%d kali"),
        },
    )


def show_attendance_analysis_page() -> None:
    inject_dashboard_css()
    data = load_employee_data()
    months = ["Januari", "Februari", "Maret"]
    weekdays = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat"]
    with st.sidebar:
        st.markdown("# 🛡️ EWS Kehadiran")
        st.caption("Analisis pola presensi")
        st.divider()
        chosen_month = st.selectbox("Periode bulan", ["Semua Bulan"] + months, key="attendance_page_month")
        units = ["Semua Unit"] + sorted(data["Unit Kerja"].unique().tolist())
        chosen_unit = st.selectbox("Unit kerja", units, key="attendance_page_unit")
        search_name = st.text_input("Cari nama atau NIP", key="attendance_page_search")
        st.divider()
        st.caption(f"Login sebagai: {st.session_state.username}")
        st.button("Keluar", on_click=logout, use_container_width=True, key="attendance_page_logout")

    filtered = data.copy()
    if chosen_month != "Semua Bulan":
        filtered = filtered[filtered["Bulan"] == chosen_month]
    if chosen_unit != "Semua Unit":
        filtered = filtered[filtered["Unit Kerja"] == chosen_unit]
    if search_name:
        query = search_name.lower()
        filtered = filtered[filtered["Nama Pegawai"].str.lower().str.contains(query) | filtered["NIP"].str.lower().str.contains(query)]
    filtered = filtered.copy()
    filtered["Hadir"] = (filtered["Hari Kerja"] - filtered["WFH"] - filtered["DL"] - filtered["Cuti"] - filtered["TK"]).clip(lower=0)

    composition = pd.Series({
        "Hadir": int(filtered["Hadir"].sum()), "WFH": int(filtered["WFH"].sum()), "DL": int(filtered["DL"].sum()),
        "Cuti": int(filtered["Cuti"].sum()), "TK": int(filtered["TK"].sum()),
        "Terlambat": int(filtered["Terlambat"].sum()),
    })
    day_analysis = filtered.groupby("Hari Dominan")["Terlambat"].sum().reindex(weekdays, fill_value=0)
    peak_bins = pd.cut(filtered["Jam Datang"], bins=[6.99, 7.30, 8.00, 8.30, 8.5], labels=["07.00–07.30", "07.31–08.00", "08.01–08.30", "≥ 08.31"])
    peak_analysis = peak_bins.value_counts().sort_index()
    peak_period = str(peak_analysis.idxmax()) if not peak_analysis.empty and peak_analysis.max() else "Belum tersedia"
    monthly = filtered.groupby("Bulan").agg(Hari_Kerja=("Hari Kerja", "sum"), TK=("TK", "sum"), Cuti=("Cuti", "sum"))
    monthly["Kehadiran"] = ((monthly["Hari_Kerja"] - monthly["TK"] - monthly["Cuti"]) / monthly["Hari_Kerja"] * 100).clip(lower=0)
    monthly = monthly.reindex(months)
    weekly = filtered.reset_index(drop=True).assign(Minggu=lambda frame: frame.index // 5 + 1).groupby("Minggu")["Terlambat"].sum().rename("Keterlambatan")
    heatmap = filtered.pivot_table(index="Bulan", columns="Hari Dominan", values="Terlambat", aggfunc="sum", fill_value=0).reindex(index=months, columns=weekdays, fill_value=0)

    st.markdown("<h1 class='dashboard-title'>Analisis Presensi</h1>", unsafe_allow_html=True)
    st.markdown(f"<div class='page-context-grid'><div class='page-context-card risk-context-card'>Komposisi dan pola presensi</div><div class='page-context-card'>Periode: {chosen_month}</div></div>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Komposisi Presensi</div>", unsafe_allow_html=True)
    composition_rows = "".join(
        f"<div class='composition-row'><span class='composition-label'>{label}</span><span class='composition-value'>{value} {'kali' if label == 'Terlambat' else 'hari'}</span></div>"
        for label, value in composition.items()
    )
    st.markdown(f"<div class='composition-list'>{composition_rows}</div>", unsafe_allow_html=True)
    composition_colors = {
        "Hadir": "#2563eb", "WFH": "#7c3aed", "DL": "#0891b2", "Cuti": "#16a34a",
        "TK": "#f59e0b", "Terlambat": "#dc2626",
    }
    maximum_composition = max(int(composition.max()), 1)
    composition_bar_rows = "".join(
        f"<div class='composition-bar-row'><span class='composition-bar-label'>{label}</span>"
        f"<div class='composition-bar-track'><div class='composition-bar-fill' style='width:{value / maximum_composition * 100:.1f}%;background:{composition_colors[label]}'></div></div>"
        f"<span class='composition-bar-value'>{int(value)}</span></div>"
        for label, value in composition.items()
    )
    st.markdown(f"<div class='composition-bars'>{composition_bar_rows}</div>", unsafe_allow_html=True)

    st.markdown("<div class='section-title'>Trend Analysis</div>", unsafe_allow_html=True)
    daily_col, weekly_col, monthly_col = st.columns(3)
    with daily_col:
        st.caption("Tren harian")
        st.bar_chart(day_analysis, color="#f97316", height=220)
    with weekly_col:
        st.caption("Tren mingguan")
        st.line_chart(weekly, color="#7c3aed", height=220)
    with monthly_col:
        st.caption("Tren bulanan")
        st.line_chart(monthly["Kehadiran"], color="#059669", height=220)

    st.markdown("<div class='section-title'>Calendar Heatmap</div>", unsafe_allow_html=True)
    st.dataframe(
        heatmap,
        use_container_width=True,
        column_config={weekday: st.column_config.NumberColumn(weekday, format="%d") for weekday in weekdays},
    )
    day_col, peak_col = st.columns(2)
    with day_col:
        st.markdown("<div class='section-title'>Day-of-Week Analysis</div>", unsafe_allow_html=True)
        day_table = day_analysis.rename("Keterlambatan").reset_index().rename(columns={"Hari Dominan": "Hari"})
        day_table["Ringkasan"] = day_table.apply(lambda row: f"{row['Hari']} → {int(row['Keterlambatan'])} keterlambatan", axis=1)
        st.dataframe(day_table, hide_index=True, use_container_width=True)
    with peak_col:
        st.markdown("<div class='section-title'>Peak Hour Analysis</div>", unsafe_allow_html=True)
        st.bar_chart(peak_analysis.rename("Jumlah Pegawai"), color="#dc2626", height=220)
        st.info(f"Periode keterlambatan tertinggi: **{peak_period}**")
    total_late = int(day_analysis.sum())
    monday_share = int(day_analysis.get("Senin", 0)) / total_late * 100 if total_late else 0
    st.markdown("<div class='section-title'>Pattern Analysis</div>", unsafe_allow_html=True)
    st.warning(f"⚠️ **{monday_share:.0f}%** kejadian keterlambatan terjadi pada hari Senin.")


def show_attendance_analysis_page() -> None:
    inject_dashboard_css()
    data = load_employee_data()
    months = ["Januari", "Februari", "Maret"]
    weekdays = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat"]
    with st.sidebar:
        chosen_month = st.selectbox("Periode bulan", ["Semua Bulan"] + months, key="attendance_page_month_v2")
        units = ["Semua Unit"] + sorted(data["Unit Kerja"].unique().tolist())
        chosen_unit = st.selectbox("Unit kerja", units, key="attendance_page_unit_v2")
        search_name = st.text_input("Cari nama atau NIP", key="attendance_page_search_v2")
    filtered = data.copy()
    if chosen_month != "Semua Bulan": filtered = filtered[filtered["Bulan"] == chosen_month]
    if chosen_unit != "Semua Unit": filtered = filtered[filtered["Unit Kerja"] == chosen_unit]
    if search_name:
        query = search_name.lower()
        filtered = filtered[filtered["Nama Pegawai"].str.lower().str.contains(query) | filtered["NIP"].str.lower().str.contains(query)]
    if filtered.empty:
        st.markdown("<h1 class='ews-page-title'>Analisis Presensi</h1>", unsafe_allow_html=True)
        st.info("Tidak terdapat data presensi pada periode yang dipilih.")
        return
    filtered = filtered.copy()
    filtered["Hadir"] = (filtered["Hari Kerja"] - filtered["WFH"] - filtered["DL"] - filtered["Cuti"] - filtered["TK"]).clip(lower=0)
    total_work = max(int(filtered["Hari Kerja"].sum()), 1)
    comp = filtered[["Hadir", "WFH", "DL", "Cuti", "TK"]].sum().astype(int)
    late_total = int(filtered["Terlambat"].sum())
    st.markdown("<h1 class='ews-page-title'>Analisis Presensi</h1>", unsafe_allow_html=True)
    st.markdown("<div class='ews-page-subtitle'>Analisis komposisi, tren, dan pola presensi pegawai berdasarkan periode yang dipilih.</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='ews-filter-row'><span>Periode: <strong>{chosen_month}</strong></span><span class='ews-filter-chip'>OPD: <strong>{'Semua OPD' if chosen_unit == 'Semua Unit' else chosen_unit}</strong></span></div>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Ringkasan Presensi</div>", unsafe_allow_html=True)
    cols = st.columns(4)
    for col, label, value in zip(cols, ["Tingkat Kehadiran", "Tanpa Keterangan (TK)", "Keterlambatan", "Cuti"], [f"{comp['Hadir'] / total_work * 100:.1f}%", f"{comp['TK']} hari", f"{late_total} kali", f"{comp['Cuti']} hari"]): col.metric(label, value)
    st.caption(f"WFH: {comp['WFH']} hari • DL: {comp['DL']} hari")
    st.markdown("<div class='section-title'>Komposisi Presensi</div>", unsafe_allow_html=True)
    st.bar_chart(comp, color="#2563eb", height=240)
    monthly = filtered.groupby("Bulan").agg(Kerja=("Hari Kerja", "sum"), TK=("TK", "sum"), Cuti=("Cuti", "sum"))
    monthly["Kehadiran"] = ((monthly["Kerja"] - monthly["TK"] - monthly["Cuti"]) / monthly["Kerja"] * 100).clip(lower=0)
    monthly = monthly.reindex(months)
    day_analysis = filtered.groupby("Hari Dominan")["Terlambat"].sum().reindex(weekdays, fill_value=0)
    day_chart = pd.DataFrame({"Hari": weekdays, "Keterlambatan": [int(day_analysis.get(day, 0)) for day in weekdays]})
    month_chart = pd.DataFrame({"Bulan": months, "Kehadiran": [monthly["Kehadiran"].get(month, float("nan")) for month in months]}).dropna()
    peak_bins = pd.cut(filtered["Jam Datang"], bins=[6.99, 7.30, 8.00, 8.30, 8.5], labels=["07.00–07.30", "07.31–08.00", "08.01–08.30", "≥ 08.31"])
    peak = peak_bins.value_counts().sort_index()
    st.markdown("<div class='section-title'>Tren Presensi</div>", unsafe_allow_html=True)
    trend_choice = st.radio("Pilih tren", ["Harian", "Mingguan", "Bulanan"], horizontal=True, key="attendance_trend_v2", label_visibility="collapsed")
    if trend_choice == "Bulanan": st.line_chart(month_chart, x="Bulan", y="Kehadiran", color="#2563eb", height=260)
    elif trend_choice == "Harian": st.line_chart(day_chart, x="Hari", y="Keterlambatan", color="#2563eb", height=260)
    else: st.line_chart(filtered.reset_index(drop=True).assign(Minggu=lambda x: x.index // 5 + 1).groupby("Minggu")["Terlambat"].sum(), color="#2563eb", height=260)
    day_col, peak_col = st.columns(2)
    with day_col:
        st.markdown("<div class='section-title'>Hari Rawan Keterlambatan</div>", unsafe_allow_html=True); st.bar_chart(day_chart, x="Hari", y="Keterlambatan", color="#f97316", height=240)
        if day_analysis.max() > 0: st.caption(f"{day_analysis.idxmax()} merupakan hari dengan keterlambatan tertinggi, yaitu {int(day_analysis.max())} kejadian.")
    with peak_col:
        st.markdown("<div class='section-title'>Distribusi Waktu Keterlambatan</div>", unsafe_allow_html=True); st.bar_chart(peak, color="#2563eb", height=240)
        if len(peak) and peak.max() > 0: st.caption(f"Periode tertinggi: {peak.idxmax()} WIB dengan {int(peak.max())} kejadian.")
    heatmap = filtered.pivot_table(index="Bulan", columns="Hari Dominan", values="Terlambat", aggfunc="sum", fill_value=0).reindex(index=months, columns=weekdays, fill_value=0)
    st.markdown("<div class='section-title'>Heatmap Pola Keterlambatan</div>", unsafe_allow_html=True)
    heat_max = max(int(heatmap.to_numpy().max()) if not heatmap.empty else 0, 1)
    heat_cells = "<div style='display:grid;grid-template-columns:130px repeat(5,1fr);gap:4px;background:#e2e8f0;padding:4px;border-radius:10px'>"
    heat_cells += "<div style='background:#fff;padding:8px;font-weight:700'>Bulan</div>" + "".join(f"<div style='background:#fff;padding:8px;text-align:center;font-weight:700'>{day}</div>" for day in weekdays)
    for month_name, row in heatmap.iterrows():
        heat_cells += f"<div style='background:#fff;padding:8px;font-weight:650'>{month_name}</div>"
        for day in weekdays:
            value = int(row.get(day, 0)); intensity = value / heat_max
            background = f"rgba(37,99,235,{0.08 + intensity * 0.82:.2f})"
            text_color = "#fff" if intensity > .48 else "#173b63"
            heat_cells += f"<div style='background:{background};color:{text_color};padding:8px;text-align:center;font-weight:700'>{value}</div>"
    heat_cells += "</div>"
    st.markdown(heat_cells, unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Insight Presensi</div>", unsafe_allow_html=True)
    if day_analysis.max() > 0: st.markdown(f"⚠️ {day_analysis.idxmax()} merupakan hari dengan keterlambatan tertinggi: {int(day_analysis.max())} kejadian.")
    if len(peak) and peak.max() > 0: st.markdown(f"🕘 Keterlambatan paling banyak terjadi pada pukul {peak.idxmax()}: {int(peak.max())} kejadian.")
    valid = monthly["Kehadiran"].dropna()
    if len(valid) > 1: st.markdown(f"📈 Kehadiran {valid.index[-1]} {'meningkat' if valid.iloc[-1] >= valid.iloc[-2] else 'menurun'} {abs(valid.iloc[-1] - valid.iloc[-2]):.1f} poin persentase dibanding {valid.index[-2]}.")

    st.markdown("<div class='section-title'>Analisis Pegawai</div>", unsafe_allow_html=True)
    st.caption("Identifikasi pegawai berdasarkan pola presensi pada periode yang dipilih.")
    ranking_type = st.selectbox("Analisis berdasarkan", ["Keterlambatan Tertinggi", "TK Tertinggi", "Kehadiran Terendah"], key="employee_ranking_type_v2")
    ranking_limit = st.selectbox("Tampilkan", [5, 10], format_func=lambda value: f"Top {value}", key="employee_ranking_limit_v2")
    employee_group = filtered.groupby(["NIP", "Nama Pegawai", "Unit Kerja"], as_index=False).agg(
        Terlambat=("Terlambat", "sum"), TK=("TK", "sum"), Cuti=("Cuti", "sum"), DL=("DL", "sum"), WFH=("WFH", "sum"), Hari_Kerja=("Hari Kerja", "sum"), Hadir=("Hadir", "sum")
    )
    employee_group["Kehadiran"] = (employee_group["Hadir"] / employee_group["Hari_Kerja"].replace(0, 1) * 100).clip(lower=0)
    sort_column = "Kehadiran" if ranking_type == "Kehadiran Terendah" else "Terlambat" if ranking_type == "Keterlambatan Tertinggi" else "TK"
    ranking = employee_group.sort_values(sort_column, ascending=(ranking_type == "Kehadiran Terendah")).head(ranking_limit).copy()
    if ranking.empty:
        st.info("Tidak terdapat data pegawai pada periode yang dipilih.")
    else:
        ranking.insert(0, "No", range(1, len(ranking) + 1))
        ranking_view = ranking[["No", "Nama Pegawai", "Unit Kerja", "Terlambat", "TK", "Kehadiran"]].copy()
        ranking_view["Terlambat"] = ranking_view["Terlambat"].map(lambda value: f"{int(value)} kali")
        ranking_view["TK"] = ranking_view["TK"].map(lambda value: f"{int(value)} hari")
        ranking_view["Kehadiran"] = ranking_view["Kehadiran"].map(lambda value: f"{value:.1f}%")
        st.dataframe(
            ranking_view,
            hide_index=True,
            use_container_width=True,
            column_config={
                "No": st.column_config.NumberColumn("No", width="small"),
                "Nama Pegawai": st.column_config.TextColumn("Nama Pegawai", width="large"),
                "Unit Kerja": st.column_config.TextColumn("Unit Kerja", width="medium"),
                "Terlambat": st.column_config.TextColumn("Terlambat", width="small"),
                "TK": st.column_config.TextColumn("TK", width="small"),
                "Kehadiran": st.column_config.TextColumn("Kehadiran", width="small"),
            },
        )
        chart_data = ranking.sort_values(sort_column, ascending=True if ranking_type != "Kehadiran Terendah" else False)
        chart_title = ranking_type
        st.caption(chart_title)
        ranking_chart = chart_data[["Nama Pegawai", sort_column]].set_index("Nama Pegawai")
        st.bar_chart(ranking_chart, color="#2563eb", height=300)
        lead = ranking.iloc[0]
        lead_value = f"{lead[sort_column]:.1f}%" if sort_column == "Kehadiran" else f"{int(lead[sort_column])} {'kali' if sort_column == 'Terlambat' else 'hari'}"
        st.info(f"{lead['Nama Pegawai']} merupakan pegawai dengan {ranking_type.lower()} pada periode ini, yaitu {lead_value}.")
        selected_employee = st.selectbox("Pilih pegawai untuk melihat detail", ranking["Nama Pegawai"].tolist(), key="employee_ranking_detail_v2")
        selected = employee_group[employee_group["Nama Pegawai"] == selected_employee].iloc[0]
        st.markdown(f"**Detail Presensi Pegawai — {selected_employee}**  \nUnit Kerja: {selected['Unit Kerja']}  \nKehadiran: {selected['Kehadiran']:.1f}% • TK: {int(selected['TK'])} hari • Terlambat: {int(selected['Terlambat'])} kali • Cuti: {int(selected['Cuti'])} hari • DL: {int(selected['DL'])} hari • WFH: {int(selected['WFH'])} hari")


def show_opd_analysis_page_legacy() -> None:
    inject_dashboard_css()
    data = load_employee_data()
    month_order = ["Januari", "Februari", "Maret"]

    with st.sidebar:
        st.markdown("# 🛡️ EWS Kehadiran")
        st.caption("Analisis presensi per OPD")
        st.divider()
        st.markdown("#### Filter Analisis OPD")
        chosen_month = st.selectbox("Periode bulan", month_order, key="opd_month")
        st.divider()
        st.caption(f"Login sebagai: {st.session_state.username}")
        st.button("Keluar", on_click=logout, use_container_width=True, key="opd_logout")

    monthly_data = data[data["Bulan"] == chosen_month].copy()
    opd_summary = monthly_data.groupby("Unit Kerja").agg(
        Pegawai=("NIP", "nunique"),
        Hari_Kerja=("Hari Kerja", "sum"),
        TK_TB=("TK", "sum"),
        Cuti=("Cuti", "sum"),
        Keterlambatan=("Terlambat", "sum"),
    )
    opd_summary["Persentase Kehadiran"] = (
        (opd_summary["Hari_Kerja"] - opd_summary["TK_TB"] - opd_summary["Cuti"])
        / opd_summary["Hari_Kerja"]
        * 100
    ).clip(lower=0)
    opd_summary = opd_summary.sort_values("Persentase Kehadiran", ascending=False)
    opd_ranking = opd_summary.reset_index()
    opd_ranking.index = opd_ranking.index + 1
    opd_ranking.index.name = "Peringkat"

    opd_trend_source = data.groupby(["Bulan", "Unit Kerja"]).agg(
        Hari_Kerja=("Hari Kerja", "sum"),
        TK_TB=("TK", "sum"),
        Cuti=("Cuti", "sum"),
    )
    opd_trend_source["Persentase Kehadiran"] = (
        (opd_trend_source["Hari_Kerja"] - opd_trend_source["TK_TB"] - opd_trend_source["Cuti"])
        / opd_trend_source["Hari_Kerja"]
        * 100
    ).clip(lower=0)
    opd_trend = opd_trend_source["Persentase Kehadiran"].unstack("Unit Kerja").reindex(month_order)

    st.markdown("<p class='dashboard-title'>Analisis OPD</p>", unsafe_allow_html=True)
    st.markdown(
        f"<div class='page-context-grid'><div class='page-context-card risk-context-card'>Perbandingan presensi antar OPD</div><div class='page-context-card'>Periode: {chosen_month}</div></div>",
        unsafe_allow_html=True,
    )
    overview_1, overview_2, overview_3 = st.columns(3)
    overview_1.metric("OPD Terbaik", opd_ranking.iloc[0]["Unit Kerja"], f"{opd_ranking.iloc[0]['Persentase Kehadiran']:.1f}% kehadiran")
    overview_2.metric("Rata-rata Kehadiran OPD", f"{opd_ranking['Persentase Kehadiran'].mean():.1f}%")
    overview_3.metric("Total TK", f"{int(opd_ranking['TK_TB'].sum())} hari")

    st.markdown("<div class='section-title'>Ranking OPD</div>", unsafe_allow_html=True)
    st.dataframe(
        opd_ranking[["Unit Kerja", "Pegawai", "Persentase Kehadiran", "TK_TB", "Keterlambatan"]],
        use_container_width=True,
        column_config={
            "Persentase Kehadiran": st.column_config.NumberColumn("Kehadiran", format="%.1f%%"),
            "TK_TB": st.column_config.NumberColumn("TK", format="%d hari"),
            "Keterlambatan": st.column_config.NumberColumn("Keterlambatan", format="%d kali"),
        },
    )

    attendance_col, absence_col, late_col = st.columns(3)
    with attendance_col:
        st.markdown("<div class='section-title'>Persentase Kehadiran per OPD</div>", unsafe_allow_html=True)
        st.bar_chart(opd_summary["Persentase Kehadiran"], color="#059669", height=270)
    with absence_col:
        st.markdown("<div class='section-title'>TK per OPD</div>", unsafe_allow_html=True)
        st.bar_chart(opd_summary["TK_TB"], color="#dc2626", height=270)
    with late_col:
        st.markdown("<div class='section-title'>Keterlambatan per OPD</div>", unsafe_allow_html=True)
        st.bar_chart(opd_summary["Keterlambatan"], color="#f97316", height=270)

    st.markdown("<div class='section-title'>Tren Presensi OPD</div>", unsafe_allow_html=True)
    st.caption("Perbandingan persentase kehadiran setiap OPD dari Januari hingga Maret.")
    st.line_chart(opd_trend, height=320)


def show_opd_analysis_page() -> None:
    inject_dashboard_css()
    data = load_employee_data()
    months = ["Januari", "Februari", "Maret"]
    with st.sidebar:
        st.markdown("# 🛡️ EWS Kehadiran")
        st.caption("Kinerja dan risiko OPD")
        st.divider()
        chosen_month = st.selectbox("Periode bulan", ["Semua Bulan"] + months, key="opd_page_month")
        st.divider()
        st.caption(f"Login sebagai: {st.session_state.username}")
        st.button("Keluar", on_click=logout, use_container_width=True, key="opd_page_logout")

    filtered = data if chosen_month == "Semua Bulan" else data[data["Bulan"] == chosen_month]
    filtered = filtered.copy()
    filtered["Risk Score"] = filtered.apply(lambda row: calculate_risk_score(row["TK"], row["Terlambat"]), axis=1)
    filtered["Status"] = filtered["Risk Score"].apply(risk_status)
    filtered["Penyebab"] = filtered.apply(lambda row: warning_indicators(row["TK"], row["Terlambat"]), axis=1)
    status_icons = {"Normal": "🟢", "Waspada": "🟡", "Tinggi": "🟠", "Kritis": "🔴"}

    opd = filtered.groupby("Unit Kerja").agg(
        Pegawai=("NIP", "nunique"),
        Hari_Kerja=("Hari Kerja", "sum"),
        TK_TB=("TK", "sum"),
        Keterlambatan=("Terlambat", "sum"),
        Risk_Score=("Risk Score", "mean"),
    )
    opd["Kehadiran"] = ((opd["Hari_Kerja"] - opd["TK_TB"] - filtered.groupby("Unit Kerja")["Cuti"].sum()) / opd["Hari_Kerja"] * 100).clip(lower=0)
    opd["Pegawai Berisiko"] = filtered.groupby("Unit Kerja")["Status"].apply(lambda values: (values != "Normal").sum())
    opd = opd.sort_values("Risk_Score", ascending=False).reset_index()
    opd["Risk Score"] = opd["Risk_Score"].round(0).astype(int)
    opd["Status"] = opd["Risk Score"].apply(risk_status)
    opd["Status"] = opd["Status"].map(lambda value: f"{status_icons[value]} {value}")
    opd["Gap"] = opd["Kehadiran"] - 95

    st.markdown("<h1 class='dashboard-title'>Analisis OPD</h1>", unsafe_allow_html=True)
    st.markdown(f"<div class='page-context-grid'><div class='page-context-card risk-context-card'>Analisis kinerja OPD</div><div class='page-context-card'>Periode: {chosen_month}</div></div>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>OPD dengan Risiko Tertinggi</div>", unsafe_allow_html=True)
    st.dataframe(
        opd[["Unit Kerja", "Risk Score", "Status", "Pegawai Berisiko"]],
        hide_index=True,
        use_container_width=True,
        column_config={"Risk Score": st.column_config.NumberColumn("Risk Score", format="%d"), "Status": st.column_config.TextColumn("Status", width="medium")},
    )

    st.markdown("<div class='section-title'>Perbandingan Kinerja OPD</div>", unsafe_allow_html=True)
    st.dataframe(
        opd[["Unit Kerja", "Kehadiran", "TK_TB", "Keterlambatan", "Risk Score"]],
        hide_index=True,
        use_container_width=True,
        column_config={
            "Kehadiran": st.column_config.NumberColumn("Kehadiran", format="%.1f%%"),
            "TK_TB": st.column_config.NumberColumn("TK", format="%d hari"),
            "Keterlambatan": st.column_config.NumberColumn("Keterlambatan", format="%d kali"),
            "Risk Score": st.column_config.NumberColumn("Risk Score", format="%d"),
        },
    )

    st.markdown("<div class='section-title'>Target vs Realisasi OPD</div>", unsafe_allow_html=True)
    target_table = opd[["Unit Kerja", "Kehadiran", "Gap"]].rename(columns={"Kehadiran": "Realisasi"})
    target_table.insert(1, "Target", 95.0)
    st.dataframe(
        target_table,
        hide_index=True,
        use_container_width=True,
        column_config={
            "Target": st.column_config.NumberColumn("Target", format="%.1f%%"),
            "Realisasi": st.column_config.NumberColumn("Realisasi", format="%.1f%%"),
            "Gap": st.column_config.NumberColumn("Gap", format="%+.1f%%"),
        },
    )

    st.markdown("<div class='section-title'>Pegawai Berisiko per OPD</div>", unsafe_allow_html=True)
    chosen_opd = st.selectbox("Pilih OPD untuk melihat pegawai berisiko", opd["Unit Kerja"].tolist(), key="opd_drilldown")
    drilldown = filtered[(filtered["Unit Kerja"] == chosen_opd) & (filtered["Status"] != "Normal")].sort_values("Risk Score", ascending=False)
    if drilldown.empty:
        st.success("Tidak ada pegawai berisiko pada OPD ini.")
    else:
        st.dataframe(
            drilldown[["Nama Pegawai", "NIP", "Risk Score", "TK", "Terlambat", "Penyebab", "Status"]],
            hide_index=True,
            use_container_width=True,
            column_config={
                "Risk Score": st.column_config.NumberColumn("Risk Score", format="%d"),
            "TK": st.column_config.NumberColumn("TK", format="%d hari"),
                "Terlambat": st.column_config.NumberColumn("Terlambat", format="%d kali"),
                "Penyebab": st.column_config.TextColumn("Penyebab", width="large"),
            },
        )


def show_opd_analysis_page() -> None:
    inject_dashboard_css()
    data = load_employee_data()
    months = ["Januari", "Februari", "Maret"]
    threshold = 85.0
    with st.sidebar:
        chosen_month = st.selectbox("Periode bulan", ["Semua Bulan"] + months, key="opd_page_month_v2")
        units = ["Semua Unit"] + sorted(data["Unit Kerja"].unique().tolist())
        chosen_unit = st.selectbox("OPD", units, key="opd_page_unit_v2")
    filtered = data.copy()
    if chosen_month != "Semua Bulan": filtered = filtered[filtered["Bulan"] == chosen_month]
    if chosen_unit != "Semua Unit": filtered = filtered[filtered["Unit Kerja"] == chosen_unit]
    st.markdown("<h1 class='ews-page-title'>Analisis OPD</h1>", unsafe_allow_html=True)
    st.markdown("<div class='ews-page-subtitle'>Perbandingan dan evaluasi presensi antar perangkat daerah berdasarkan periode yang dipilih.</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='ews-filter-row'><span>Periode: <strong>{chosen_month}</strong></span><span class='ews-filter-chip'>OPD: <strong>{'Semua OPD' if chosen_unit == 'Semua Unit' else chosen_unit}</strong></span></div>", unsafe_allow_html=True)
    if filtered.empty:
        st.info("Tidak terdapat data presensi OPD pada periode yang dipilih."); return
    filtered = filtered.copy(); filtered["Hadir"] = (filtered["Hari Kerja"] - filtered["TK"] - filtered["Cuti"]).clip(lower=0)
    opd = filtered.groupby("Unit Kerja").agg(Pegawai=("NIP", "nunique"), Hadir=("Hadir", "sum"), Hari_Kerja=("Hari Kerja", "sum"), TK=("TK", "sum"), Terlambat=("Terlambat", "sum"), Cuti=("Cuti", "sum"), WFH=("WFH", "sum"), DL=("DL", "sum")).reset_index()
    opd["Kehadiran"] = (opd["Hadir"] / opd["Hari_Kerja"].replace(0, 1) * 100).clip(lower=0)
    st.markdown("<div class='section-title'>Ringkasan OPD</div>", unsafe_allow_html=True)
    best = opd.loc[opd["Kehadiran"].idxmax()]; attention = int((opd["Kehadiran"] < threshold).sum())
    summary_cols = st.columns(4)
    summary_cols[0].metric("Jumlah OPD", len(opd)); summary_cols[1].metric("Rata-rata Kehadiran", f"{opd['Kehadiran'].mean():.1f}%"); summary_cols[2].metric("Kehadiran Tertinggi", f"{best['Kehadiran']:.1f}%", best["Unit Kerja"]); summary_cols[3].metric("OPD Perlu Perhatian", attention)
    st.markdown("<div class='section-title'>Perbandingan OPD</div>", unsafe_allow_html=True)
    ranking_type = st.selectbox("Urutkan berdasarkan", ["Kehadiran Tertinggi", "Kehadiran Terendah", "TK Tertinggi", "Keterlambatan Tertinggi"], key="opd_rank_type_v2")
    limit_label = st.selectbox("Tampilkan", ["Top 10", "Top 5", "Semua OPD"], key="opd_rank_limit_v2")
    metric = "Kehadiran" if "Kehadiran" in ranking_type else "TK" if ranking_type == "TK Tertinggi" else "Terlambat"
    ranked = opd.sort_values(metric, ascending=(ranking_type == "Kehadiran Terendah"))
    if limit_label != "Semua OPD": ranked = ranked.head(int(limit_label.split()[1]))
    chart_data = ranked.sort_values(metric, ascending=True).set_index("Unit Kerja")[[metric]]
    st.bar_chart(chart_data, color="#2563eb", height=300)
    table = ranked.reset_index(drop=True); table.insert(0, "No", range(1, len(table) + 1)); table = table[["No", "Unit Kerja", "Pegawai", "Kehadiran", "TK", "Terlambat"]].copy(); table["Kehadiran"] = table["Kehadiran"].map(lambda v: f"{v:.1f}%"); table["TK"] = table["TK"].map(lambda v: f"{int(v)} hari"); table["Terlambat"] = table["Terlambat"].map(lambda v: f"{int(v)} kali")
    st.dataframe(table, hide_index=True, use_container_width=True, column_config={"No": st.column_config.NumberColumn(width="small"), "Unit Kerja": st.column_config.TextColumn(width="large"), "Pegawai": st.column_config.NumberColumn(width="small"), "Kehadiran": st.column_config.TextColumn(width="medium"), "TK": st.column_config.TextColumn(width="small"), "Terlambat": st.column_config.TextColumn(width="medium")})
    attention_df = opd[opd["Kehadiran"] < threshold].copy()
    st.markdown("<div class='section-title'>OPD yang Memerlukan Perhatian</div>", unsafe_allow_html=True)
    if attention_df.empty: st.success("Tidak ada OPD di bawah ambang perhatian.")
    else:
        attention_df["Indikasi"] = attention_df.apply(lambda row: "Kehadiran rendah + keterlambatan tinggi" if row["Kehadiran"] < threshold and row["Terlambat"] >= opd["Terlambat"].median() else "Kehadiran rendah", axis=1)
        st.dataframe(attention_df[["Unit Kerja", "Kehadiran", "TK", "Terlambat", "Indikasi"]], hide_index=True, use_container_width=True)
    st.markdown("<div class='section-title'>Tren Presensi OPD</div>", unsafe_allow_html=True)
    trend_mode = st.selectbox("Tampilan Tren", ["Pilih Satu OPD", "Top 5 Kehadiran", "Bottom 5 Kehadiran"], key="opd_trend_mode_v2")
    if trend_mode == "Pilih Satu OPD": selected_units = [st.selectbox("Pilih OPD", sorted(opd["Unit Kerja"].tolist()), key="opd_trend_unit_v2")]
    else:
        base = opd.sort_values("Kehadiran", ascending=trend_mode.startswith("Bottom")).head(5); selected_units = base["Unit Kerja"].tolist()
    trend_source = data[data["Unit Kerja"].isin(selected_units)].copy(); trend_source["Hadir"] = (trend_source["Hari Kerja"] - trend_source["TK"] - trend_source["Cuti"]).clip(lower=0); trend_source["Kehadiran"] = trend_source["Hadir"] / trend_source["Hari Kerja"].replace(0, 1) * 100
    trend = trend_source.groupby(["Bulan", "Unit Kerja"])["Kehadiran"].mean().unstack("Unit Kerja").reindex(months)
    trend_chart = trend.reset_index(); trend_chart["Bulan"] = pd.Categorical(trend_chart["Bulan"], categories=months, ordered=True); trend_chart = trend_chart.sort_values("Bulan"); st.line_chart(trend_chart, x="Bulan", y=selected_units, height=280)
    st.markdown("<div class='section-title'>Detail OPD</div>", unsafe_allow_html=True)
    detail_unit = st.selectbox("Pilih OPD", sorted(opd["Unit Kerja"].tolist()), key="opd_detail_unit_v2"); detail = opd[opd["Unit Kerja"] == detail_unit].iloc[0]
    detail_cols = st.columns(5)
    for col, label, value in zip(detail_cols, ["Jumlah Pegawai", "Kehadiran", "TK", "Terlambat", "Cuti"], [int(detail["Pegawai"]), f"{detail['Kehadiran']:.1f}%", f"{int(detail['TK'])} hari", f"{int(detail['Terlambat'])} kali", f"{int(detail['Cuti'])} hari"]): col.metric(label, value)
    st.caption(f"WFH: {int(detail['WFH'])} hari • DL: {int(detail['DL'])} hari")
    detail_source = data[data["Unit Kerja"] == detail_unit].copy(); detail_source["Hadir"] = (detail_source["Hari Kerja"] - detail_source["TK"] - detail_source["Cuti"]).clip(lower=0); detail_source["Kehadiran"] = detail_source["Hadir"] / detail_source["Hari Kerja"].replace(0, 1) * 100
    detail_trend = detail_source.groupby("Bulan")["Kehadiran"].mean().reindex(months).dropna().rename("Kehadiran").reset_index(); detail_trend["Bulan"] = pd.Categorical(detail_trend["Bulan"], categories=months, ordered=True); detail_trend = detail_trend.sort_values("Bulan"); st.line_chart(detail_trend, x="Bulan", y="Kehadiran", height=220)
    st.markdown("<div class='section-title'>Insight OPD</div>", unsafe_allow_html=True)
    lowest = opd.loc[opd["Kehadiran"].idxmin()]; highest_late = opd.loc[opd["Terlambat"].idxmax()]
    st.markdown(f"🏆 Kehadiran tertinggi: **{best['Unit Kerja']}** ({best['Kehadiran']:.1f}%).")
    st.markdown(f"⚠️ Kehadiran terendah: **{lowest['Unit Kerja']}** ({lowest['Kehadiran']:.1f}%).")
    st.markdown(f"🕘 Keterlambatan tertinggi: **{highest_late['Unit Kerja']}** ({int(highest_late['Terlambat'])} kali).")


def show_employee_detail_page_legacy() -> None:
    inject_dashboard_css()
    data = load_employee_data()
    month_order = ["Januari", "Februari", "Maret"]
    employees = data.drop_duplicates("NIP").sort_values("Nama Pegawai")
    employee_options = {
        f"{row['Nama Pegawai']} — {row['NIP']}": row["NIP"]
        for _, row in employees.iterrows()
    }

    with st.sidebar:
        st.markdown("# 🛡️ EWS Kehadiran")
        st.caption("Detail presensi pegawai")
        st.divider()
        selected_employee_label = st.selectbox("Pilih pegawai", employee_options.keys(), key="detail_employee")
        selected_nip = employee_options[selected_employee_label]
        employee_history = data[data["NIP"] == selected_nip].copy()
        available_months = [month for month in month_order if month in employee_history["Bulan"].values]
        selected_month = st.selectbox("Periode detail", available_months, key="detail_month")
        st.divider()
        st.caption(f"Login sebagai: {st.session_state.username}")
        st.button("Keluar", on_click=logout, use_container_width=True, key="detail_logout")

    employee_history["Bulan"] = pd.Categorical(employee_history["Bulan"], categories=month_order, ordered=True)
    employee_history = employee_history.sort_values("Bulan")
    selected_record = employee_history[employee_history["Bulan"] == selected_month].iloc[0]
    employee_history["Hadir"] = (
        employee_history["Hari Kerja"]
        - employee_history["TK"]
        - employee_history["Cuti"]
        - employee_history["WFH"]
        - employee_history["DL"]
    ).clip(lower=0)
    employee_history["Risk Score"] = employee_history.apply(
        lambda row: calculate_risk_score(row["TK"], row["Terlambat"]), axis=1
    )
    employee_history["Status Risiko"] = employee_history["Risk Score"].apply(risk_status)
    employee_history["Indikator Warning"] = employee_history.apply(
        lambda row: warning_indicators(row["TK"], row["Terlambat"]), axis=1
    )
    employee_history["Rekomendasi"] = employee_history["Status Risiko"].apply(risk_recommendation)

    score = calculate_risk_score(selected_record["TK"], selected_record["Terlambat"])
    status = risk_status(score)
    recommendation = risk_recommendation(status)
    attendance_calendar = build_attendance_calendar(selected_record)

    st.markdown("<p class='dashboard-title'>Detail Pegawai</p>", unsafe_allow_html=True)
    st.markdown(
        f"<p class='dashboard-subtitle'>Profil dan riwayat presensi • Periode: {selected_month}</p>",
        unsafe_allow_html=True,
    )

    st.markdown("<div class='section-title'>Identitas Pegawai</div>", unsafe_allow_html=True)
    identity_1, identity_2, identity_3, identity_4 = st.columns(4)
    identity_1.metric("NIP", selected_record["NIP"])
    identity_2.metric("Nama Pegawai", selected_record["Nama Pegawai"])
    identity_3.metric("Unit Kerja", selected_record["Unit Kerja"])
    identity_4.metric("Hari Kerja", f"{int(selected_record['Hari Kerja'])} hari")

    risk_col, recommendation_col = st.columns([1, 2])
    with risk_col:
        st.markdown("<div class='section-title'>Risk Score</div>", unsafe_allow_html=True)
        st.metric("Status Risiko", f"{score}/100", status)
        st.progress(score / 100)
    with recommendation_col:
        st.markdown("<div class='section-title'>Rekomendasi Tindak Lanjut</div>", unsafe_allow_html=True)
        st.info(f"**Status {status}:** {recommendation}")

    st.markdown("<div class='section-title'>Kalender Presensi</div>", unsafe_allow_html=True)
    st.caption("Status per hari kerja pada periode terpilih. Legenda: Hadir, TK, WFH, DL, dan Cuti.")
    st.dataframe(attendance_calendar, hide_index=True, use_container_width=True)

    history_col, late_history_col = st.columns(2)
    with history_col:
        st.markdown("<div class='section-title'>Riwayat Kehadiran</div>", unsafe_allow_html=True)
        st.dataframe(
            employee_history[["Bulan", "Hadir", "TK", "WFH", "DL", "Cuti"]],
            hide_index=True,
            use_container_width=True,
            column_config={
                "Hadir": st.column_config.NumberColumn("Hadir", format="%d hari"),
                "TK": st.column_config.NumberColumn("TK", format="%d hari"),
                "WFH": st.column_config.NumberColumn("WFH", format="%d hari"),
                "DL": st.column_config.NumberColumn("DL", format="%d hari"),
                "Cuti": st.column_config.NumberColumn("Cuti", format="%d hari"),
            },
        )
    with late_history_col:
        st.markdown("<div class='section-title'>Riwayat Keterlambatan</div>", unsafe_allow_html=True)
        st.dataframe(
            employee_history[["Bulan", "Terlambat", "Jam Datang", "Hari Dominan"]],
            hide_index=True,
            use_container_width=True,
            column_config={
                "Terlambat": st.column_config.NumberColumn("Keterlambatan", format="%d kali"),
                "Jam Datang": st.column_config.NumberColumn("Rata-rata Jam Datang", format="%.2f"),
            },
        )

    st.markdown("<div class='section-title'>Riwayat Warning</div>", unsafe_allow_html=True)
    st.dataframe(
        employee_history[["Bulan", "Risk Score", "Status Risiko", "Indikator Warning", "Rekomendasi"]],
        hide_index=True,
        use_container_width=True,
        column_config={
            "Risk Score": st.column_config.NumberColumn("Risk Score", format="%d/100"),
            "Status Risiko": st.column_config.TextColumn("Status", width="medium"),
            "Indikator Warning": st.column_config.TextColumn("Penyebab Warning", width="large"),
            "Rekomendasi": st.column_config.TextColumn("Rekomendasi", width="large"),
        },
    )


def show_employee_detail_page() -> None:
    inject_dashboard_css()
    data = load_employee_data()
    months = ["Januari", "Februari", "Maret"]
    employees = data.drop_duplicates("NIP").sort_values("Nama Pegawai")
    options = {f"{row['Nama Pegawai']} — {row['NIP']}": row["NIP"] for _, row in employees.iterrows()}

    with st.sidebar:
        st.markdown("# 🛡️ EWS Kehadiran")
        st.caption("Profil dan riwayat individu")
        st.divider()
        selected_label = st.selectbox("Pilih pegawai", options.keys(), key="employee_page_select")
        selected_nip = options[selected_label]
        history = data[data["NIP"] == selected_nip].copy()
        selected_month = st.selectbox("Periode", months, key="employee_page_month")
        st.divider()
        st.caption(f"Login sebagai: {st.session_state.username}")
        st.button("Keluar", on_click=logout, use_container_width=True, key="employee_page_logout")

    history["Bulan"] = pd.Categorical(history["Bulan"], categories=months, ordered=True)
    history = history.sort_values("Bulan")
    selected_rows = history[history["Bulan"] == selected_month]
    has_period_data = not selected_rows.empty
    if has_period_data:
        record = selected_rows.iloc[0]
    else:
        record = history.iloc[0].copy()
        record["Bulan"] = selected_month
        for field in ["TK", "Cuti", "Terlambat", "Hari Kerja", "WFH", "DL"]:
            record[field] = 0
    history["Hadir"] = (history["Hari Kerja"] - history["TK"] - history["WFH"] - history["DL"] - history["Cuti"]).clip(lower=0)
    history["Kehadiran"] = (history["Hadir"] / history["Hari Kerja"] * 100).round(1)
    history["Risk Score"] = history.apply(lambda row: calculate_risk_score(row["TK"], row["Terlambat"]), axis=1)
    history["Status"] = history["Risk Score"].apply(risk_status)
    history["Status Ikon"] = history["Status"].map({"Normal": "🟢 NORMAL", "Waspada": "🟡 WASPADA", "Tinggi": "🟠 TINGGI", "Kritis": "🔴 KRITIS"})
    score = calculate_risk_score(record["TK"], record["Terlambat"])
    status = risk_status(score)
    attendance = (max(record["Hari Kerja"] - record["TK"] - record["Cuti"], 0) / record["Hari Kerja"] * 100) if record["Hari Kerja"] else 0
    calendar = build_attendance_calendar(record)
    pattern_days = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat"]
    pattern_summary = history.groupby("Hari Dominan")["TK"].sum().reindex(pattern_days, fill_value=0)
    peak_pattern_day = pattern_summary.idxmax() if pattern_summary.sum() else "Belum tersedia"
    peak_pattern_count = int(pattern_summary.max()) if pattern_summary.sum() else 0

    st.markdown("<h1 class='dashboard-title'>Detail Pegawai</h1>", unsafe_allow_html=True)
    st.markdown(f"<div class='page-context-grid'><div class='page-context-card risk-context-card'>Profil individu dan pola presensi</div><div class='page-context-card'>Periode: {selected_month}</div></div>", unsafe_allow_html=True)
    if not has_period_data:
        st.info(f"Belum ada data presensi {record['Nama Pegawai']} untuk periode {selected_month}.")
    st.markdown("<div class='section-title'>Identitas Pegawai</div>", unsafe_allow_html=True)
    identity_table = pd.DataFrame(
        {
            "Informasi": ["Nama", "NIP", "Jabatan", "Pangkat/Golongan", "OPD"],
            "Data": [
                record["Nama Pegawai"],
                record["NIP"],
                record["Jabatan"],
                record["Pangkat/Golongan"],
                record["Unit Kerja"],
            ],
        }
    )
    st.dataframe(identity_table, hide_index=True, use_container_width=True)

    st.markdown("<div class='section-title'>KPI Individu</div>", unsafe_allow_html=True)
    kpi_values = {
        "Kehadiran": f"{attendance:.1f}%",
        "TK": f"{int(record['TK'])} hari",
        "Terlambat": f"{int(record['Terlambat'])} kali",
        "Risk Score": f"{score}/100",
        "Status": {"Normal": "🟢 NORMAL", "Waspada": "🟡 WASPADA", "Tinggi": "🟠 TINGGI", "Kritis": "🔴 KRITIS"}[status],
    }
    kpi_cards = "".join(
        f"<div class='individual-kpi-card'><div class='label'>{label}</div><div class='value'>{value}</div></div>"
        for label, value in kpi_values.items()
    )
    st.markdown(f"<div class='individual-kpi-grid'>{kpi_cards}</div>", unsafe_allow_html=True)

    st.markdown("<div class='section-title'>Calendar Heatmap</div>", unsafe_allow_html=True)
    st.caption("Status presensi individu berdasarkan urutan hari kerja pada periode terpilih.")
    st.dataframe(calendar, hide_index=True, use_container_width=True)

    st.markdown("<div class='section-title'>Riwayat Presensi</div>", unsafe_allow_html=True)
    st.dataframe(
        history[["Bulan", "Hadir", "TK", "Terlambat", "WFH", "DL", "Cuti"]],
        hide_index=True,
        use_container_width=True,
        column_config={
            "Kehadiran": st.column_config.NumberColumn("Kehadiran", format="%.1f%%"),
            "Hadir": st.column_config.NumberColumn("Hadir", format="%d hari"),
            "TK": st.column_config.NumberColumn("TK", format="%d hari"),
            "Terlambat": st.column_config.NumberColumn("Terlambat", format="%d kali"),
            "WFH": st.column_config.NumberColumn("WFH", format="%d hari"),
            "DL": st.column_config.NumberColumn("DL", format="%d hari"),
            "Cuti": st.column_config.NumberColumn("Cuti", format="%d hari"),
        },
    )

    st.markdown("<div class='section-title'>Pattern</div>", unsafe_allow_html=True)
    st.dataframe(
        pattern_summary.rename("Kejadian TK").reset_index().rename(columns={"Hari Dominan": "Hari"}),
        hide_index=True,
        use_container_width=True,
    )
    st.warning(f"⚠️ Pola TK tertinggi terjadi pada **{peak_pattern_day}** ({peak_pattern_count} kejadian) dalam riwayat yang tersedia.")
    st.markdown("<div class='section-title'>Riwayat Warning</div>", unsafe_allow_html=True)
    warning_history = history[history["Status"] != "Normal"][["Bulan", "Risk Score", "Status Ikon"]]
    if warning_history.empty:
        st.success("Pegawai belum masuk kategori Waspada, Tinggi, atau Kritis.")
    else:
        st.dataframe(warning_history, hide_index=True, use_container_width=True)


def show_audit_trail_page() -> None:
    inject_dashboard_css()
    audit_events = st.session_state.setdefault(
        "audit_trail",
        [
            {"Waktu": "22/08 09:10", "User": "Admin", "Aktivitas": "Login ke sistem"},
            {"Waktu": "22/08 09:10", "User": "Admin", "Aktivitas": "Import data Agustus"},
            {"Waktu": "22/08 09:15", "User": "System", "Aktivitas": "Data berhasil diproses — 500 halaman"},
            {"Waktu": "22/08 09:15", "User": "System", "Aktivitas": "18 warning dibuat"},
            {"Waktu": "22/08 10:30", "User": "Operator", "Aktivitas": "Warning Pegawai A diverifikasi"},
            {"Waktu": "22/08 11:20", "User": "Operator", "Aktivitas": "Status diubah menjadi selesai"},
            {"Waktu": "22/08 11:35", "User": "Admin", "Aktivitas": "Data diperbaiki"},
            {"Waktu": "22/08 11:45", "User": "Operator", "Aktivitas": "Warning ditutup"},
        ],
    )
    with st.sidebar:
        st.markdown("# 🛡️ EWS Kehadiran")
        st.caption("Log aktivitas administrator dan operator")
        st.divider()
        user_filter = st.selectbox("Filter user", ["Semua User"] + sorted({event["User"] for event in audit_events}), key="audit_user")
        st.divider()
        st.caption(f"Login sebagai: {st.session_state.username}")
        st.button("Keluar", on_click=logout, use_container_width=True, key="audit_logout")

    visible_events = audit_events if user_filter == "Semua User" else [event for event in audit_events if event["User"] == user_filter]
    audit_table = pd.DataFrame(visible_events, columns=["Waktu", "User", "Aktivitas"])
    st.markdown("<h1 class='dashboard-title'>Audit Trail</h1>", unsafe_allow_html=True)
    st.markdown("<div class='page-context-grid'><div class='page-context-card risk-context-card'>Riwayat aktivitas administrator, operator, dan sistem</div></div>", unsafe_allow_html=True)
    total_events, system_events, operator_events = st.columns(3)
    total_events.metric("Total Aktivitas", len(visible_events))
    system_events.metric("Aktivitas System", sum(event["User"] == "System" for event in visible_events))
    operator_events.metric("Aktivitas Operator", sum(event["User"] == "Operator" for event in visible_events))
    st.markdown("<div class='section-title'>Log Aktivitas</div>", unsafe_allow_html=True)
    st.dataframe(audit_table, hide_index=True, use_container_width=True)


def show_action_center_page() -> None:
    inject_dashboard_css()
    data = load_employee_data()
    months = ["Januari", "Februari", "Maret"]
    with st.sidebar:
        st.markdown("# 🛡️ EWS Kehadiran")
        st.caption("Pusat tindak lanjut warning")
        st.divider()
        chosen_month = st.selectbox("Periode bulan", ["Semua Bulan"] + months, key="action_month")
        units = ["Semua Unit"] + sorted(data["Unit Kerja"].unique().tolist())
        chosen_unit = st.selectbox("PIC/OPD", units, key="action_unit")
        st.divider()
        st.caption(f"Login sebagai: {st.session_state.username}")
        st.button("Keluar", on_click=logout, use_container_width=True, key="action_logout")

    filtered = data if chosen_month == "Semua Bulan" else data[data["Bulan"] == chosen_month]
    if chosen_unit != "Semua Unit":
        filtered = filtered[filtered["Unit Kerja"] == chosen_unit]
    filtered = filtered.copy()
    filtered["Risk Score"] = filtered.apply(lambda row: calculate_risk_score(row["TK"], row["Terlambat"]), axis=1)
    actions = filtered[(filtered["TK"] >= 3) | (filtered["Terlambat"] >= 8)].copy()
    actions["Warning"] = actions.apply(
        lambda row: "TK + Terlambat" if row["TK"] >= 3 and row["Terlambat"] >= 8 else ("TK" if row["TK"] >= 3 else "Terlambat"),
        axis=1,
    )
    month_number = {"Januari": "01", "Februari": "02", "Maret": "03"}
    actions["Tanggal"] = [f"{20 - (index % 10):02d}/{month_number.get(str(month), '08')}" for index, month in enumerate(actions["Bulan"])]
    actions["Status"] = actions["Risk Score"].apply(lambda score: "🔴 Belum ditindaklanjuti" if score >= 75 else "🟡 Verifikasi")
    actions["PIC"] = actions["Unit Kerja"]

    saved_status = st.session_state.setdefault("action_status", {})
    for nip, status in saved_status.items():
        actions.loc[actions["NIP"] == nip, "Status"] = status
    status_counts = actions["Status"].value_counts()
    st.markdown("<h1 class='dashboard-title'>Action Center</h1>", unsafe_allow_html=True)
    st.markdown(f"<div class='page-context-grid'><div class='page-context-card risk-context-card'>Tindak lanjut warning presensi</div><div class='page-context-card'>Periode: {chosen_month}</div></div>", unsafe_allow_html=True)
    card_1, card_2, card_3 = st.columns(3)
    card_1.metric("Belum ditindaklanjuti", int(status_counts.get("🔴 Belum ditindaklanjuti", 0)))
    card_2.metric("Verifikasi", int(status_counts.get("🟡 Verifikasi", 0)))
    card_3.metric("Selesai", int(status_counts.get("🟢 Selesai", 0)))

    st.markdown("<div class='section-title'>Daftar Action Center</div>", unsafe_allow_html=True)
    if actions.empty:
        st.success("Tidak ada warning yang perlu ditindaklanjuti pada filter ini.")
    else:
        st.dataframe(
            actions[["Nama Pegawai", "Warning", "Tanggal", "Status", "PIC"]].sort_values("Tanggal", ascending=False),
            hide_index=True,
            use_container_width=True,
        )
        selected_action = st.selectbox("Pilih pegawai untuk tindakan", actions["Nama Pegawai"].tolist(), key="action_employee")
        selected_nip = actions.loc[actions["Nama Pegawai"] == selected_action, "NIP"].iloc[0]
        action_buttons = st.columns(3)
        if action_buttons[0].button("Verifikasi", use_container_width=True, key="action_verify"):
            saved_status[selected_nip] = "🟡 Verifikasi"
            st.rerun()
        if action_buttons[1].button("Tindak Lanjut", use_container_width=True, key="action_followup"):
            saved_status[selected_nip] = "🔴 Belum ditindaklanjuti"
            st.rerun()
        if action_buttons[2].button("Tandai Selesai", use_container_width=True, key="action_done"):
            saved_status[selected_nip] = "🟢 Selesai"
            st.rerun()


def show_early_warning_page() -> None:
    inject_dashboard_css()
    data = load_employee_data()
    month_order = ["Januari", "Februari", "Maret"]

    with st.sidebar:
        st.markdown("# 🛡️ EWS Kehadiran")
        st.caption("Prioritas dan tindak lanjut risiko")
        st.divider()
        st.markdown("#### Filter Risiko")
        chosen_month = st.selectbox("Periode bulan", ["Semua Bulan"] + month_order, key="risk_page_month")
        units = ["Semua Unit"] + sorted(data["Unit Kerja"].unique().tolist())
        chosen_unit = st.selectbox("Unit kerja", units, key="risk_page_unit")
        search_name = st.text_input("Cari nama atau NIP", placeholder="Ketik untuk mencari", key="risk_page_search")
        st.divider()
        st.caption(f"Login sebagai: {st.session_state.username}")
        st.button("Keluar", on_click=logout, use_container_width=True, key="risk_page_logout")

    risk_data = data.copy()
    if chosen_month != "Semua Bulan":
        risk_data = risk_data[risk_data["Bulan"] == chosen_month]
    if chosen_unit != "Semua Unit":
        risk_data = risk_data[risk_data["Unit Kerja"] == chosen_unit]
    if search_name:
        query = search_name.lower()
        risk_data = risk_data[
            risk_data["Nama Pegawai"].str.lower().str.contains(query)
            | risk_data["NIP"].str.lower().str.contains(query)
        ]

    risk_data = risk_data.copy()
    risk_data["Risk Score"] = risk_data.apply(
        lambda row: calculate_risk_score(row["TK"], row["Terlambat"]), axis=1
    )
    risk_data["Status"] = risk_data["Risk Score"].apply(risk_status)
    risk_data["Penyebab"] = risk_data.apply(
        lambda row: warning_indicators(row["TK"], row["Terlambat"]), axis=1
    )
    risk_data["Prioritas"] = risk_data["Status"].map(
        {"Kritis": "P1", "Tinggi": "P2", "Waspada": "P3", "Normal": "P4"}
    )
    risk_data["Rekomendasi"] = risk_data["Status"].apply(risk_recommendation)

    previous_average_score = None
    if chosen_month in month_order and month_order.index(chosen_month) > 0:
        previous_month = month_order[month_order.index(chosen_month) - 1]
        previous_data = data[data["Bulan"] == previous_month].copy()
        if chosen_unit != "Semua Unit":
            previous_data = previous_data[previous_data["Unit Kerja"] == chosen_unit]
        if search_name:
            query = search_name.lower()
            previous_data = previous_data[
                previous_data["Nama Pegawai"].str.lower().str.contains(query)
                | previous_data["NIP"].str.lower().str.contains(query)
            ]
        if not previous_data.empty:
            previous_average_score = previous_data.apply(
                lambda row: calculate_risk_score(row["TK"], row["Terlambat"]), axis=1
            ).mean()

    status_order = ["Normal", "Waspada", "Tinggi", "Kritis"]
    status_icons = {"Normal": "🟢", "Waspada": "🟡", "Tinggi": "🟠", "Kritis": "🔴"}
    status_counts = risk_data["Status"].value_counts().reindex(status_order, fill_value=0)
    total_risk_employees = len(risk_data)
    high_critical = int(status_counts["Tinggi"] + status_counts["Kritis"])
    overall_status = "Normal" if high_critical == 0 else "Perlu Perhatian" if high_critical <= max(1, total_risk_employees // 3) else "Risiko Tinggi"
    overall_icon = "🟢" if overall_status == "Normal" else "🟠" if overall_status == "Perlu Perhatian" else "🔴"
    st.markdown("<h1 class='ews-page-title'>EARLY WARNING SYSTEM</h1>", unsafe_allow_html=True)
    st.markdown("<div class='ews-page-subtitle'>Monitoring risiko presensi dan deteksi dini pegawai</div>", unsafe_allow_html=True)
    display_unit = "Semua OPD" if chosen_unit == "Semua Unit" else chosen_unit
    period_label = "Januari–Maret 2026" if chosen_month == "Semua Bulan" else f"{chosen_month} 2026"
    st.markdown(f"<div class='ews-filter-row'><span>Periode: <strong>{period_label}</strong></span><span class='ews-filter-chip'>OPD: <strong>{display_unit}</strong></span></div>", unsafe_allow_html=True)
    header_risk_source = data.copy()
    if chosen_unit != "Semua Unit":
        header_risk_source = header_risk_source[header_risk_source["Unit Kerja"] == chosen_unit]
    if search_name:
        header_query = search_name.lower()
        header_risk_source = header_risk_source[
            header_risk_source["Nama Pegawai"].str.lower().str.contains(header_query)
            | header_risk_source["NIP"].str.lower().str.contains(header_query)
        ]
    header_risk_source["Risk Score"] = header_risk_source.apply(lambda row: calculate_risk_score(row["TK"], row["Terlambat"]), axis=1)
    header_risk_counts = header_risk_source.assign(Berisiko=header_risk_source["Risk Score"] >= 25).groupby("Bulan")["Berisiko"].sum().reindex(month_order).fillna(0)
    header_previous = int(header_risk_counts.iloc[0]) if len(header_risk_counts) else 0
    header_current = int(header_risk_counts.iloc[-1]) if len(header_risk_counts) else 0
    header_change = header_current - header_previous
    header_change_pct = (header_change / header_previous * 100) if header_previous else 0
    header_icon = "🟢" if header_change <= 0 else "🔴"
    header_label = "Risiko Menurun" if header_change <= 0 else "Risiko Meningkat"
    header_arrow = "↓" if header_change <= 0 else "↑"
    if chosen_month != "Semua Bulan":
        st.markdown(f"<div class='ews-header-risk'><div class='risk-label'>{header_icon} {header_label}</div><div class='risk-count'>{header_previous} → {header_current} pegawai</div><div class='risk-change'>{header_arrow} {abs(header_change)} pegawai ({header_change_pct:+.1f}%) dibanding {month_order[0]}</div></div>", unsafe_allow_html=True)
    warning_total = int((risk_data["Status"] != "Normal").sum())
    st.markdown(f"<div class='ews-status-banner'><div class='status-label'>STATUS EWS</div><div class='status-value'>{overall_icon} {overall_status.upper()}</div><div class='status-detail'>{high_critical} dari {total_risk_employees} pegawai memerlukan perhatian<br><span style='opacity:.85'>{warning_total} warning aktif • {warning_total} belum ditindaklanjuti</span></div></div>", unsafe_allow_html=True)

    st.markdown("<div class='section-title'>Risk Summary</div>", unsafe_allow_html=True)
    summary_columns = st.columns(4)
    summary_styles = {"Normal": "green", "Waspada": "yellow", "Tinggi": "orange", "Kritis": "red"}
    for column, status_name in zip(summary_columns, status_order):
        column.markdown(
            f"<div class='ews-risk-summary'><div class='ews-card {summary_styles[status_name]}'><div class='label'>{status_icons[status_name]} {status_name.upper()}</div><div class='number'>{int(status_counts[status_name])}</div><div class='detail'>{(int(status_counts[status_name]) / total_risk_employees * 100) if total_risk_employees else 0:.1f}% pegawai</div></div></div>",
            unsafe_allow_html=True,
        )

    trend_col = st.container()
    with trend_col:
        st.markdown("<div class='section-title'>Tren Risiko</div>", unsafe_allow_html=True)
        risk_trend_source = data.copy()
        if chosen_unit != "Semua Unit":
            risk_trend_source = risk_trend_source[risk_trend_source["Unit Kerja"] == chosen_unit]
        if search_name:
            trend_query = search_name.lower()
            risk_trend_source = risk_trend_source[
                risk_trend_source["Nama Pegawai"].str.lower().str.contains(trend_query)
                | risk_trend_source["NIP"].str.lower().str.contains(trend_query)
            ]
        risk_trend_source["Risk Score"] = risk_trend_source.apply(lambda row: calculate_risk_score(row["TK"], row["Terlambat"]), axis=1)
        visible_months = month_order[: month_order.index(chosen_month) + 1] if chosen_month in month_order else month_order
        risk_counts = risk_trend_source.assign(Berisiko=risk_trend_source["Risk Score"] >= 25).groupby("Bulan")["Berisiko"].sum().reindex(visible_months).fillna(0)
        current_risk = int(risk_counts.iloc[-1]) if len(risk_counts) else 0
        previous_risk = int(risk_counts.iloc[-2]) if len(risk_counts) > 1 else current_risk
        risk_change = current_risk - previous_risk
        risk_change_pct = (risk_change / previous_risk * 100) if previous_risk else 0
        risk_peak_month = str(risk_counts.idxmax()) if len(risk_counts) else "-"
        improving = risk_change <= 0
        risk_direction = "↓" if improving else "↑"
        risk_status_text = "MEMBAIK" if improving else "MEMBURUK"
        risk_status_color = "#047857" if improving else "#dc2626"
        st.markdown(
            f"<div class='trend-summary-grid'><div class='trend-summary-card'><div class='trend-summary-label'>Risiko Saat Ini</div><div class='trend-summary-value'>{current_risk} pegawai</div></div><div class='trend-summary-card'><div class='trend-summary-label'>Perubahan</div><div class='trend-summary-value {'positive' if improving else 'negative'}'>{risk_direction} {abs(risk_change)} pegawai</div><div class='trend-summary-label'>{risk_change_pct:+.1f}%</div></div></div><div style='color:{risk_status_color};font-weight:800;font-size:.82rem;margin:.1rem 0 .35rem;'>{'🟢' if improving else '🔴'} {risk_status_text}</div><div class='note'>Perkembangan jumlah pegawai berisiko</div>",
            unsafe_allow_html=True,
        )
        risk_chart_data = pd.DataFrame({"Bulan": visible_months, "Risiko": risk_counts.values, "Batas Waspada": [30] * len(visible_months), "Batas Kritis": [40] * len(visible_months)})
        risk_base = alt.Chart(risk_chart_data).encode(
            x=alt.X("Bulan:N", sort=month_order, title=None, axis=alt.Axis(labelAngle=0)),
            y=alt.Y("Risiko:Q", scale=alt.Scale(domain=[0, max(45, int(risk_counts.max()) + 5)]), title="Pegawai berisiko"),
            tooltip=[alt.Tooltip("Bulan:N", title="Periode"), alt.Tooltip("Risiko:Q", title="Pegawai berisiko")],
        )
        risk_line = risk_base.mark_line(color="#173b63", strokeWidth=3, point=alt.OverlayMarkDef(size=65, filled=True, fill="#173b63", stroke="#ffffff", strokeWidth=2))
        critical_rule = alt.Chart(risk_chart_data).mark_rule(color="#e11d48", strokeDash=[5, 4]).encode(y="Batas Kritis:Q")
        warning_rule = alt.Chart(risk_chart_data).mark_rule(color="#f97316", strokeDash=[5, 4]).encode(y="Batas Waspada:Q")
        st.altair_chart((risk_line + critical_rule + warning_rule).properties(height=240), use_container_width=True)
        st.caption("Batas Waspada: 30 pegawai  •  Batas Kritis: 40 pegawai")

    st.markdown("<div class='section-title'>⚠ Peringatan Prioritas</div>", unsafe_allow_html=True)
    top_risk = risk_data[risk_data["Status"] != "Normal"].sort_values(
        ["Risk Score", "Nama Pegawai"], ascending=[False, True]
    ).head(10).copy()
    top_risk["Status"] = top_risk["Status"].map(lambda value: f"{status_icons[value]} {value}")
    if top_risk.empty:
        st.success("Tidak ada pegawai yang memerlukan perhatian pada filter ini.")
    else:
        st.dataframe(
            top_risk[["Nama Pegawai", "Unit Kerja", "Risk Score", "Penyebab", "Status"]],
            hide_index=True,
            use_container_width=True,
            column_config={
                "Risk Score": st.column_config.NumberColumn("Risk Score", format="%d"),
                "Penyebab": st.column_config.TextColumn("Penyebab", width="large"),
                "Status": st.column_config.TextColumn("Status", width="medium"),
            },
        )

    if not top_risk.empty:
        priority_record = risk_data.sort_values("Risk Score", ascending=False).iloc[0]
        priority_icon = status_icons[priority_record["Status"]]
        verification_records = st.session_state.get("verification_records", {})
        verified = priority_record["NIP"] in verification_records
        handling_status = "🔵 Terverifikasi" if verified else "⚪ Belum Diverifikasi"
        verification_detail = "<br><strong>Diverifikasi:</strong><br>22 Agustus 2026 • 19:20 WIB<br>oleh Admin" if verified else ""
        st.markdown(
            f"<div class='ews-status-banner' style='background:#fff;border-left-color:#e11d48;border-color:#fecdd3'><div class='status-value' style='color:#9f1239'>{priority_record['Nama Pegawai']} &nbsp; {priority_icon} {priority_record['Status'].upper()}</div><div class='status-detail' style='color:#475569'>TK {int(priority_record['TK'])} hari • Terlambat {int(priority_record['Terlambat'])} kali<br><br><strong>Status Penanganan:</strong><br>{handling_status}{verification_detail}</div></div>",
            unsafe_allow_html=True,
        )
        if verified:
            st.markdown("<span class='verified-badge'>✓ TERVERIFIKASI</span>", unsafe_allow_html=True)
        elif st.button("✓ Verifikasi Data", use_container_width=True, key="priority_verify_action"):
            st.session_state["verification_nip"] = priority_record["NIP"]
            st.rerun()
        if st.button("📋 Tindak Lanjut", use_container_width=True, key="priority_process_action"):
            st.session_state["navigate_to_page"] = "Action Center"
            st.rerun()
        if verified:
            priority_attendance = max(priority_record["Hari Kerja"] - priority_record["TK"] - priority_record["Cuti"], 0) / priority_record["Hari Kerja"] * 100 if priority_record["Hari Kerja"] else 0
            st.markdown(f"**{priority_record['Unit Kerja']}**  \nTK {int(priority_record['TK'])} hari • Terlambat {int(priority_record['Terlambat'])}× • Kehadiran {priority_attendance:.1f}%")
            st.info("**Rekomendasi**\n\nWarning telah diverifikasi. Lanjutkan proses tindak lanjut.")
            st.markdown("<div class='section-title'>Riwayat Penanganan</div>", unsafe_allow_html=True)
            st.markdown(
                "<div class='ews-status-banner' style='background:#fff;border-left-color:#2563eb;border-color:#dbeafe'>22 Agustus 2026 • 19:20 WIB<br><strong>✓ Warning diverifikasi oleh Admin</strong></div>",
                unsafe_allow_html=True,
            )

    analysis_left, analysis_right = st.columns(2)
    if False:
        st.markdown("<div class='section-title'>Risk Score & Warning Level</div>", unsafe_allow_html=True)
        average_score = risk_data["Risk Score"].mean() if not risk_data.empty else 0
        maximum_score = risk_data["Risk Score"].max() if not risk_data.empty else 0
        st.metric("Risk Score rata-rata", f"{average_score:.0f}/100")
        st.progress(min(average_score / 100, 1.0))
        st.caption(f"Warning level tertinggi: {status_icons[risk_status(maximum_score)]} {risk_status(maximum_score)}")
        if previous_average_score is not None:
            risk_delta = average_score - previous_average_score
            risk_arrow = "↑" if risk_delta >= 0 else "↓"
            st.metric("Rata-rata Risk Score", f"{risk_arrow} {abs(risk_delta):.0f} poin", "dibanding bulan sebelumnya")
    with analysis_right:
        with st.expander("Rule Engine — Info & Detail"):
            st.dataframe(
            pd.DataFrame(
                {
                    "Rule": ["TK", "Keterlambatan", "Risk Score"],
                    "Kondisi": ["≥ 3 hari", "≥ 8 kali", "TK × 8 + terlambat × 2"],
                    "Dampak": ["Warning", "Warning", "Status risiko"],
                }
            ),
                hide_index=True,
                use_container_width=True,
            )

    anomaly_count = int(((risk_data["TK"] >= 6) | (risk_data["Terlambat"] >= 12)).sum())
    pattern_summary = pd.DataFrame(
        {
            "Pattern Warning": ["TK ≥ 3 hari", "Keterlambatan ≥ 8 kali", "Anomali ekstrem"],
            "Jumlah Pegawai": [
                int((risk_data["TK"] >= 3).sum()),
                int((risk_data["Terlambat"] >= 8).sum()),
                anomaly_count,
            ],
        }
    )
    with st.container():
        st.markdown("<div class='section-title'>Indikator Warning</div>", unsafe_allow_html=True)
        anomaly_cols = st.columns(3)
        anomaly_labels = ["TK ≥ 3 hari", "Terlambat ≥ 8 kali", "Anomali ekstrem"]
        for anomaly_col, anomaly_label, anomaly_value in zip(anomaly_cols, anomaly_labels, pattern_summary["Jumlah Pegawai"].tolist()):
            anomaly_col.metric(anomaly_label, int(anomaly_value), "pegawai")
        st.caption("Anomali ekstrem ditandai oleh TK ≥ 6 hari atau keterlambatan ≥ 12 kali.")
    st.markdown("", unsafe_allow_html=True)
    if top_risk.empty or not st.session_state.get("verification_nip"):
        st.empty()
    else:
        top_record = risk_data.sort_values("Risk Score", ascending=False).iloc[0]
        icon = status_icons[top_record["Status"]]
        st.warning(
            f"{icon} **{top_record['Status'].upper()} WARNING**\n\n"
            f"Pegawai **{top_record['Nama Pegawai']}** mengalami {int(top_record['TK'])} TK "
            f"dan {int(top_record['Terlambat'])} keterlambatan dalam periode berjalan.\n\n"
            f"**Rekomendasi:** {top_record['Rekomendasi']}"
        )
        action_1, action_2 = st.columns(2)
        if action_1.button("✓ Verifikasi Data", use_container_width=True, key="risk_verify_action"):
            st.session_state["verification_nip"] = top_record["NIP"]
            st.rerun()
        if action_2.button("📋 Tindak Lanjut", use_container_width=True, key="risk_process_action"):
            st.session_state["navigate_to_page"] = "Action Center"
            st.rerun()

        detail_nip = st.session_state.get("warning_detail_nip")
        if detail_nip:
            detail_rows = risk_data[risk_data["NIP"] == detail_nip]
            if not detail_rows.empty:
                detail = detail_rows.iloc[0]
                detail_attendance = (
                    max(detail["Hari Kerja"] - detail["TK"] - detail["Cuti"], 0) / detail["Hari Kerja"] * 100
                    if detail["Hari Kerja"]
                    else 0
                )
                monday_tk = int(detail["TK"]) if detail["Hari Dominan"] == "Senin" else 0
                late_change_text = None
                if chosen_month in month_order and month_order.index(chosen_month) > 0:
                    previous_month = month_order[month_order.index(chosen_month) - 1]
                    previous_rows = data[(data["NIP"] == detail_nip) & (data["Bulan"] == previous_month)]
                    if not previous_rows.empty:
                        previous_late = int(previous_rows["Terlambat"].iloc[0])
                        if previous_late:
                            late_change_text = f"{(detail['Terlambat'] - previous_late) / previous_late * 100:+.0f}% dari bulan sebelumnya"
                        elif detail["Terlambat"]:
                            late_change_text = "meningkat dari 0 menjadi ada kejadian"
                with st.expander("Lihat Detail Analisis", expanded=True):
                    st.markdown(
                        f"**{detail['Status'].upper()} — {detail['Nama Pegawai']}**\n\n"
                        f"Risk Score: **{calculate_risk_score(detail['TK'], detail['Terlambat'])}/100**\n\n"
                        f"- TK: **{int(detail['TK'])} hari**\n"
                        f"- Keterlambatan: **{int(detail['Terlambat'])} kali**\n"
                        f"- Kehadiran: **{detail_attendance:.1f}%**\n"
                        f"- Pola dominan: **TK pada hari {detail['Hari Dominan']}**\n\n"
                        f"**Rekomendasi:** Verifikasi data presensi dan lakukan tindak lanjut sesuai ketentuan."
                    )

        verification_nip = st.session_state.get("verification_nip")
        if verification_nip:
            verification_rows = risk_data[risk_data["NIP"] == verification_nip]
            if not verification_rows.empty:
                verification_record = verification_rows.iloc[0]
                st.markdown("<div class='section-title'>Verifikasi Warning</div>", unsafe_allow_html=True)
                st.markdown(
                    f"**Pegawai**\n\n### {verification_record['Nama Pegawai']}\n\n**Data yang diverifikasi:**\n\n- TK: **{int(verification_record['TK'])} hari**\n- Keterlambatan: **{int(verification_record['Terlambat'])} kali**\n- Status Risiko: **{verification_record['Status'].upper()}**"
                )
                st.warning(
                    f"🔴 TK: **{int(verification_record['TK'])} hari** — "
                    "silakan cocokkan dengan dokumen cuti atau bukti kehadiran."
                )
                verification_status = "Data Valid"
                verification_note = st.text_area(
                    "Catatan Verifikasi",
                    value="Data telah diperiksa dan sesuai",
                    key="verification_note",
                )
                verify_save, verify_close = st.columns(2)
                if verify_save.button("✓ Konfirmasi Verifikasi", use_container_width=True, key="save_verification"):
                    st.session_state.setdefault("verification_records", {})[verification_nip] = {
                        "Status": verification_status,
                        "Catatan": verification_note,
                    }
                    st.success("Verifikasi data berhasil dikonfirmasi.")
                if verify_close.button("Batal", use_container_width=True, key="close_verification"):
                    st.session_state.pop("verification_nip", None)
                    st.rerun()


def show_dashboard() -> None:
    inject_dashboard_css()
    data = load_employee_data()
    month_order = ["Januari", "Februari", "Maret"]

    with st.sidebar:
        st.markdown("# 🛡️ EWS Kehadiran")
        st.caption("Ringkasan eksekutif presensi pegawai")
        st.divider()
        st.markdown("#### Filter Dashboard")
        chosen_month = st.selectbox("Periode bulan", ["Semua Bulan"] + month_order, key="executive_month")
        units = ["Semua Unit"] + sorted(data["Unit Kerja"].unique().tolist())
        chosen_unit = st.selectbox("Unit kerja", units, key="executive_unit")
        search_name = st.text_input("Cari nama atau NIP", placeholder="Ketik untuk mencari", key="executive_search")
        st.divider()
        st.caption(f"Login sebagai: {st.session_state.username}")
        st.button("Keluar", on_click=logout, use_container_width=True, key="executive_logout")

    def filter_data(source: pd.DataFrame, month: str | None = None) -> pd.DataFrame:
        result = source.copy()
        if month and month != "Semua Bulan":
            result = result[result["Bulan"] == month]
        if chosen_unit != "Semua Unit":
            result = result[result["Unit Kerja"] == chosen_unit]
        if search_name:
            query = search_name.lower()
            result = result[
                result["Nama Pegawai"].str.lower().str.contains(query)
                | result["NIP"].str.lower().str.contains(query)
            ]
        return result

    def attendance_rate(source: pd.DataFrame) -> float:
        workdays = source["Hari Kerja"].sum()
        if not workdays:
            return 0.0
        present_days = (source["Hari Kerja"] - source["TK"] - source["Cuti"]).clip(lower=0).sum()
        return present_days / workdays * 100

    filtered = filter_data(data, chosen_month)
    total_employees = filtered["NIP"].nunique()
    attendance = attendance_rate(filtered)
    total_tk_tb = int(filtered["TK"].sum())
    total_late = int(filtered["Terlambat"].sum())
    total_at_risk = int((filtered["TK"] >= 3).sum())
    risk_scores = filtered.apply(lambda row: calculate_risk_score(row["TK"], row["Terlambat"]), axis=1)
    total_critical = int((risk_scores >= 75).sum())
    month_index = month_order.index(chosen_month) if chosen_month in month_order else None
    previous_month = month_order[month_index - 1] if month_index else None
    previous_attendance = attendance_rate(filter_data(data, previous_month)) if previous_month else None
    attendance_delta = attendance - previous_attendance if previous_attendance is not None else None

    trend_source = filter_data(data)
    attendance_trend = pd.Series(
        {month: attendance_rate(trend_source[trend_source["Bulan"] == month]) for month in month_order},
        name="Persentase Kehadiran",
    )
    trend_df = pd.DataFrame({"Bulan": month_order, "Kehadiran": [attendance_trend.get(month, 0.0) for month in month_order]})
    trend_df["Kondisi"] = trend_df["Kehadiran"].apply(
        lambda value: "Sangat Baik" if value >= 95 else "Baik" if value >= 90 else "Perlu Perhatian" if value >= 80 else "Risiko"
    )
    opd_summary = filtered.groupby("Unit Kerja").agg(
        Pegawai=("NIP", "nunique"),
        Hari_Kerja=("Hari Kerja", "sum"),
        TK_TB=("TK", "sum"),
        Keterlambatan=("Terlambat", "sum"),
    )
    opd_summary["Kehadiran"] = (
        (opd_summary["Hari_Kerja"] - opd_summary["TK_TB"]) / opd_summary["Hari_Kerja"] * 100
    ).clip(lower=0)
    opd_summary["Pegawai Berisiko"] = filtered.groupby("Unit Kerja")["TK"].apply(lambda values: (values >= 3).sum())
    opd_summary = opd_summary.sort_values("Kehadiran", ascending=False).reset_index()

    attendance_target = 95.0
    attendance_gap = attendance - attendance_target
    gap_style = "positive" if attendance_gap >= 0 else "negative"
    formatted_gap = f"{attendance_gap:+.1f}".replace(".", ",")
    formatted_attendance = f"{attendance:.1f}".replace(".", ",")
    formatted_total_employees = f"{total_employees:,}".replace(",", ".")

    st.markdown("<h1 class='dashboard-title' style='display:block!important;visibility:visible!important;color:#102a43!important;text-align:center!important;font-size:2.35rem!important;font-weight:800!important;'>Executive Dashboard</h1>", unsafe_allow_html=True)
    st.markdown("<div class='hero-subtitle'>Ringkasan kondisi presensi pegawai</div>", unsafe_allow_html=True)
    display_unit = "Semua OPD" if chosen_unit == "Semua Unit" else chosen_unit
    st.markdown(
        f"<div class='hero-filters'><div class='hero-filter-chip'>Periode: <strong>{chosen_month}</strong></div><div class='hero-filter-chip'>OPD: <strong>{display_unit}</strong></div></div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<div class='hero-kpi-grid'><div class='hero-kpi-card'><div class='hero-kpi-icon'>👥</div><div><div class='hero-kpi-value'>{formatted_total_employees}</div><div class='hero-kpi-label'>Pegawai</div></div></div><div class='hero-kpi-card'><div class='hero-kpi-icon'>✅</div><div><div class='hero-kpi-value'>{attendance:.1f}%</div><div class='hero-kpi-label'>Kehadiran</div></div></div><div class='hero-kpi-card warning'><div class='hero-kpi-icon'>⚠️</div><div><div class='hero-kpi-value'>{total_at_risk}</div><div class='hero-kpi-label'>Warning</div></div></div><div class='hero-kpi-card critical'><div class='hero-kpi-icon'>🔴</div><div><div class='hero-kpi-value'>{total_critical}</div><div class='hero-kpi-label'>Critical</div></div></div></div>",
        unsafe_allow_html=True,
    )

    compare_col, change_col = st.columns(2)
    with compare_col:
        st.markdown("<div class='section-title'>Target vs Realisasi</div>", unsafe_allow_html=True)
        st.metric("Target Kehadiran", f"{attendance_target:.0f}%", f"Realisasi {attendance:.1f}%")
        st.progress(min(attendance / attendance_target, 1.0))
    with change_col:
        st.markdown("<div class='section-title'>Perubahan Dibanding Bulan Sebelumnya</div>", unsafe_allow_html=True)
        if attendance_delta is None:
            st.info("Data bulan sebelumnya belum tersedia untuk periode Januari.")
        else:
            direction = "naik" if attendance_delta >= 0 else "turun"
            arrow = "↑" if attendance_delta >= 0 else "↓"
            st.metric(
                "Perubahan Kehadiran",
                f"{arrow} {abs(attendance_delta):.1f}%",
                f"{direction} dibanding {previous_month}",
            )

    st.markdown("<div class='section-title'>Tren Kehadiran</div>", unsafe_allow_html=True)
    st.caption("Perkembangan tingkat kehadiran pegawai selama periode berjalan.")
    trend_margin_left, trend_center, trend_margin_right = st.columns([0.1, 0.8, 0.1])
    with trend_center:
        latest_value = float(trend_df.iloc[-1]["Kehadiran"])
        prior_value = float(trend_df.iloc[-2]["Kehadiran"]) if len(trend_df) > 1 else latest_value
        trend_change = latest_value - prior_value
        trend_status = "Sangat Baik" if latest_value >= 95 else "Baik" if latest_value >= 90 else "Perlu Perhatian" if latest_value >= 80 else "Risiko"
        trend_status_icon = "🟢" if latest_value >= 95 else "🔵" if latest_value >= 90 else "🟠" if latest_value >= 80 else "🔴"
        change_class = "positive" if trend_change >= 0 else "negative"
        change_arrow = "↑" if trend_change >= 0 else "↓"
        st.markdown(
            f"<div class='trend-summary-grid'><div class='trend-summary-card'><div class='trend-summary-label'>Kehadiran {month_order[-1]}</div><div class='trend-summary-value'>{latest_value:.1f}%</div></div><div class='trend-summary-card'><div class='trend-summary-label'>Perubahan</div><div class='trend-summary-value {change_class}'>{change_arrow} {abs(trend_change):.1f}%</div></div><div class='trend-summary-card'><div class='trend-summary-label'>Status</div><div class='trend-summary-value warning'>{trend_status_icon} {trend_status}</div></div></div>",
            unsafe_allow_html=True,
        )
        chart_data = trend_df.set_index("Bulan")[["Kehadiran"]].reindex(month_order)
        tooltip_data = chart_data.reset_index()
        trend_chart = (
            alt.Chart(tooltip_data)
            .mark_line(point=alt.OverlayMarkDef(size=85, filled=True, fill="#2563eb", stroke="#ffffff", strokeWidth=2), color="#2563eb", strokeWidth=3)
            .encode(
                x=alt.X("Bulan:N", sort=month_order, title=None, axis=alt.Axis(labelAngle=0)),
                y=alt.Y("Kehadiran:Q", scale=alt.Scale(domain=[70, 100]), title="Kehadiran (%)"),
                tooltip=[alt.Tooltip("Bulan:N", title="Periode"), alt.Tooltip("Kehadiran:Q", title="Persentase Kehadiran", format=".1f")],
            )
            .properties(height=270)
        )
        st.altair_chart(trend_chart, use_container_width=True)
        st.markdown(
            f"<div class='trend-target-note'>Target 95% <span>•</span> Rata-rata periode: <strong>{trend_df['Kehadiran'].mean():.1f}%</strong></div>",
            unsafe_allow_html=True,
        )
        st.markdown("<div class='legend'><span>🟢 ≥95% Sangat Baik</span><span>🔵 90–94,99% Baik</span><span>🟠 80–89,99% Perlu Perhatian</span><span>🔴 &lt;80% Risiko</span></div>", unsafe_allow_html=True)

    st.markdown("<div class='section-title'>Ringkasan Kondisi OPD</div>", unsafe_allow_html=True)
    st.dataframe(
        opd_summary[["Unit Kerja", "Pegawai", "Kehadiran", "TK_TB", "Keterlambatan", "Pegawai Berisiko"]],
        hide_index=True,
        use_container_width=True,
        column_config={
            "Kehadiran": st.column_config.NumberColumn("Kehadiran", format="%.1f%%"),
            "TK_TB": st.column_config.NumberColumn("TK", format="%d hari"),
            "Keterlambatan": st.column_config.NumberColumn("Terlambat", format="%d kali"),
        },
    )

    st.markdown("<div class='section-title'>Target dan KPI</div>", unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="target-kpi-card">
            <p>Target Kehadiran: <strong>&ge; {attendance_target:.0f}%</strong></p>
            <p>Realisasi: <strong>{formatted_attendance}%</strong></p>
            <p class="kpi-gap">Gap: {formatted_gap}% <span class="kpi-dot {gap_style}"></span></p>
        </div>
        """,
        unsafe_allow_html=True,
    )


initialize_session()
if not st.session_state.is_logged_in:
    show_login_page()
    st.stop()

navigation_target = st.session_state.pop("navigate_to_page", None)
if navigation_target:
    st.session_state["page_navigation"] = navigation_target

with st.sidebar:
    st.markdown(
        "<div class='sidebar-brand'><div class='brand-icon'>🛡️</div><div><div class='brand-name'>EWS PRESENSI</div><div class='brand-subtitle'>Early Warning System Kehadiran Pegawai</div></div></div>",
        unsafe_allow_html=True,
    )
    st.markdown("<div class='sidebar-nav-title'>Menu Utama</div>", unsafe_allow_html=True)
    page_options = {
        "🏠 Executive Dashboard": "Executive Dashboard",
        "🚨 Early Warning System": "Early Warning System",
        "📊 Analisis Presensi": "Analisis Presensi",
        "🏢 Analisis OPD": "Analisis OPD",
        "👤 Detail Pegawai": "Detail Pegawai",
        "✅ Action Center": "Action Center",
        "🕒 Audit Trail": "Audit Trail",
    }
    if navigation_target:
        navigation_target = next((label for label, value in page_options.items() if value == navigation_target), navigation_target)
        st.session_state["page_navigation"] = navigation_target
    selected_page_label = st.radio(
        "Pilih halaman",
        list(page_options),
        label_visibility="collapsed",
        key="page_navigation",
    )
selected_page = page_options[selected_page_label]

if selected_page == "Executive Dashboard":
    show_dashboard()
elif selected_page == "Early Warning System":
    show_early_warning_page()
elif selected_page == "Analisis Presensi":
    show_attendance_analysis_page()
elif selected_page == "Analisis OPD":
    show_opd_analysis_page()
elif selected_page == "Detail Pegawai":
    show_employee_detail_page()
elif selected_page == "Action Center":
    show_action_center_page()
else:
    show_audit_trail_page()
