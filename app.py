import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="Aplikasi Streamlit",
    page_icon="APP",
    layout="wide",
)

VALID_USERNAME = "admin"
VALID_PASSWORD = "admin123"


def load_sample_data() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Bulan": ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun"],
            "Penjualan": [120, 150, 180, 130, 210, 260],
            "Target": [100, 140, 160, 170, 190, 230],
        }
    )


def initialize_session() -> None:
    if "is_logged_in" not in st.session_state:
        st.session_state.is_logged_in = False
    if "username" not in st.session_state:
        st.session_state.username = ""
    if "login_dark_mode" not in st.session_state:
        st.session_state.login_dark_mode = False


def login(username: str, password: str) -> bool:
    return username == VALID_USERNAME and password == VALID_PASSWORD


def get_password_level(password: str) -> str:
    if not password:
        return "-"
    score = sum(
        [
            len(password) >= 8,
            any(char.islower() for char in password),
            any(char.isupper() for char in password),
            any(char.isdigit() for char in password),
            any(not char.isalnum() for char in password),
        ]
    )
    if score <= 2:
        return "Lemah"
    if score <= 4:
        return "Cukup"
    return "Kuat"


def render_login_styles(is_dark_mode: bool) -> None:
    palette = {
        "bg": "#0f172a" if is_dark_mode else "#1199ed",
        "left": "#172554" if is_dark_mode else "#5bb7ef",
        "panel": "#111827" if is_dark_mode else "#1199ed",
        "text": "#f8fafc" if is_dark_mode else "#ffffff",
        "muted": "#cbd5e1" if is_dark_mode else "#eef7ff",
        "input": "#1f2937" if is_dark_mode else "#e8f1ff",
        "input_text": "#f8fafc" if is_dark_mode else "#111827",
        "accent": "#38bdf8" if is_dark_mode else "#ffffff",
        "button": "#22c55e" if is_dark_mode else "#7dd3fc",
        "button_text": "#052e16" if is_dark_mode else "#082f49",
        "line": "#38bdf8" if is_dark_mode else "#ffffff",
    }
    st.markdown(
        f"""
        <style>
            .stApp {{
                background: {palette["bg"]};
            }}

            header[data-testid="stHeader"],
            div[data-testid="stToolbar"],
            footer {{
                display: none;
            }}

            .block-container {{
                padding: 0 !important;
                max-width: 100% !important;
            }}

            div[data-testid="stHorizontalBlock"] {{
                gap: 0 !important;
            }}

            div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:first-child {{
                background: {palette["left"]};
                min-height: 100vh;
            }}

            div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:last-child {{
                background: {palette["panel"]};
                min-height: 100vh;
                padding: 34px clamp(34px, 8vw, 120px) !important;
            }}

            .login-art {{
                display: flex;
                align-items: center;
                justify-content: center;
                min-height: 100vh;
                padding: 40px 24px;
            }}

            .login-art svg {{
                width: min(74%, 420px);
                height: auto;
            }}

            div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:last-child > div[data-testid="stVerticalBlock"] {{
                max-width: 410px;
                margin: 0;
                padding-top: min(10vh, 58px);
            }}

            .login-brand {{
                color: {palette["text"]};
                font-size: 21px;
                font-weight: 400;
                margin-bottom: 36px;
            }}

            .login-title {{
                color: {palette["text"]};
                font-size: 18px;
                font-weight: 700;
                margin-bottom: 8px;
                text-transform: uppercase;
            }}

            .login-rule {{
                width: 110px;
                height: 2px;
                background: {palette["line"]};
                margin-bottom: 28px;
            }}

            div[data-testid="stForm"] {{
                border: 0;
                padding: 0;
                background: transparent;
                width: min(100%, 460px);
            }}

            div[data-testid="stForm"] div[data-testid="stVerticalBlock"] {{
                gap: .75rem;
            }}

            div[data-testid="stForm"] label,
            div[data-testid="stForm"] [data-testid="stMarkdownContainer"] p {{
                color: {palette["text"]};
                font-size: 16px;
            }}

            div[data-testid="stForm"] input {{
                background: {palette["input"]} !important;
                color: {palette["input_text"]} !important;
                border: 0 !important;
                border-radius: 7px !important;
                min-height: 46px;
                font-size: 16px !important;
            }}

            div[data-testid="stForm"] input:focus {{
                box-shadow: 0 0 0 2px {palette["accent"]} !important;
            }}

            div[data-testid="stFormSubmitButton"] {{
                width: fit-content !important;
            }}

            div[data-testid="stFormSubmitButton"] button {{
                background: {palette["button"]} !important;
                color: {palette["button_text"]} !important;
                border: 0 !important;
                border-radius: 7px !important;
                font-weight: 700 !important;
                min-height: 44px !important;
                width: fit-content !important;
                padding: 0 28px !important;
            }}

            div[data-testid="stFormSubmitButton"] button:hover {{
                border: 0 !important;
                filter: brightness(0.96);
            }}

            .password-level {{
                color: {palette["text"]};
                display: flex;
                justify-content: space-between;
                font-weight: 700;
                margin: 2px 0 18px;
            }}

            .password-level span:last-child {{
                color: #4ade80;
            }}

            div[data-testid="stCheckbox"] label,
            div[data-testid="stCheckbox"] p,
            div[data-testid="stToggle"] label,
            div[data-testid="stToggle"] p {{
                color: {palette["text"]} !important;
                font-weight: 600;
            }}

            .stAlert {{
                border-radius: 7px;
            }}

            @media (max-width: 820px) {{
                div[data-testid="stHorizontalBlock"] {{
                    flex-direction: column;
                }}

                .login-art {{
                    min-height: 34vh;
                    padding: 22px;
                }}

                .login-art svg {{
                    width: min(58%, 280px);
                }}

                div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:last-child {{
                    min-height: 66vh;
                    padding: 28px 22px 42px !important;
                }}

                div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:last-child > div[data-testid="stVerticalBlock"] {{
                    padding-top: 0;
                }}

                .login-brand {{
                    font-size: 18px;
                    margin-bottom: 26px;
                }}
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_login_art() -> None:
    st.markdown(
        """
        <div class="login-art" aria-hidden="true">
            <svg viewBox="0 0 520 380" role="img" aria-label="Ilustrasi tugas kerja">
                <rect x="88" y="64" width="340" height="218" rx="0" fill="#f8fafc"/>
                <rect x="88" y="64" width="340" height="28" fill="#d9d9d9"/>
                <circle cx="103" cy="78" r="3.5" fill="#263238"/>
                <circle cx="116" cy="78" r="3.5" fill="#263238"/>
                <circle cx="129" cy="78" r="3.5" fill="#263238"/>
                <rect x="244" y="111" width="118" height="3" fill="#9ca3af"/>
                <rect x="244" y="155" width="118" height="3" fill="#9ca3af"/>
                <rect x="244" y="199" width="118" height="3" fill="#9ca3af"/>
                <rect x="122" y="104" width="76" height="14" fill="#ff735f"/>
                <rect x="122" y="130" width="62" height="2" fill="#9ca3af"/>
                <rect x="122" y="150" width="48" height="2" fill="#9ca3af"/>
                <text x="214" y="118" font-family="Arial" font-size="9" font-weight="700" fill="#111827">MANAGE TASKS</text>
                <text x="214" y="141" font-family="Arial" font-size="9" fill="#6b7280">Task</text>
                <rect x="346" y="134" width="66" height="24" rx="5" fill="#ff735f"/>
                <rect x="346" y="178" width="66" height="24" rx="5" fill="#ff735f"/>
                <rect x="346" y="222" width="66" height="24" rx="5" fill="#ff735f"/>
                <text x="367" y="149" font-family="Arial" font-size="9" font-weight="700" fill="#ffffff">Accept</text>
                <text x="367" y="193" font-family="Arial" font-size="9" font-weight="700" fill="#ffffff">Accept</text>
                <text x="367" y="237" font-family="Arial" font-size="9" font-weight="700" fill="#ffffff">Accept</text>
                <path d="M406 153 L439 178 L424 182 L431 205 L418 209 L411 186 L399 197 Z" fill="#263238"/>
                <circle cx="116" cy="190" r="34" fill="#ffffff" stroke="#9ca3af"/>
                <path d="M101 188 L113 200 L136 176" fill="none" stroke="#ff735f" stroke-width="7"/>
                <path d="M98 382 C117 281 154 248 220 248 C285 248 315 292 328 382 Z" fill="#ff735f"/>
                <path d="M146 312 C185 288 233 289 272 312" fill="none" stroke="#ffffff" opacity=".55"/>
                <path d="M171 250 C178 225 205 214 228 225 C248 235 251 262 237 281 C219 305 174 292 171 250 Z" fill="#263238"/>
                <circle cx="213" cy="243" r="32" fill="#ffc38b"/>
                <path d="M188 231 C195 214 221 212 236 226 C222 227 204 222 188 231 Z" fill="#263238"/>
                <circle cx="201" cy="246" r="2.8" fill="#263238"/>
                <circle cx="224" cy="246" r="2.8" fill="#263238"/>
                <path d="M212 251 L208 264 L217 263" fill="none" stroke="#8f5138" stroke-width="2"/>
                <path d="M199 273 C209 281 223 279 231 269" fill="none" stroke="#8f5138" stroke-width="2"/>
                <rect x="158" y="314" width="102" height="68" rx="8" fill="#d1d5db" stroke="#374151"/>
                <rect x="163" y="319" width="92" height="58" rx="4" fill="#e5e7eb"/>
                <rect x="199" y="338" width="20" height="25" rx="6" fill="#16a34a"/>
                <path d="M209 341 L216 345 L216 357 L209 362 L202 357 L202 345 Z" fill="#f8fafc"/>
                <rect x="358" y="286" width="32" height="66" fill="#ef654d"/>
                <rect x="329" y="352" width="90" height="17" rx="7" fill="#f8fafc" opacity=".9"/>
                <rect x="337" y="333" width="82" height="12" rx="6" fill="#f8fafc" opacity=".9"/>
                <path d="M373 286 C354 240 341 221 329 204" stroke="#1f4b5b" stroke-width="6" fill="none"/>
                <path d="M374 286 C379 242 390 216 402 198" stroke="#1f4b5b" stroke-width="6" fill="none"/>
                <path d="M374 286 C365 240 367 219 371 198" stroke="#1f4b5b" stroke-width="6" fill="none"/>
                <line x1="86" y1="382" x2="455" y2="382" stroke="#6b7280" stroke-width="2"/>
            </svg>
        </div>
        """,
        unsafe_allow_html=True,
    )


def show_login_page() -> None:
    render_login_styles(st.session_state.login_dark_mode)
    left_col, right_col = st.columns([0.95, 1.65], gap="small")

    with left_col:
        render_login_art()

    with right_col:
        st.markdown(
            """
            <div class="login-brand"></div>
            <div class="login-title">Login</div>
            <div class="login-rule"></div>
            """,
            unsafe_allow_html=True,
        )

        st.toggle("Dark Mode", key="login_dark_mode")

        with st.form("login_form"):
            username = st.text_input("Silakan Masukkan Username Anda")
            password = st.text_input("Silahkan Masukan Kata Sandi Anda", type="password")
            st.markdown(
                f"""
                <div class="password-level">
                    <span>Level Password:</span>
                    <span>{get_password_level(password)}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.checkbox("AutoLogin Selama 7 Hari")
            submitted = st.form_submit_button("Masuk", use_container_width=False)

        if submitted:
            if login(username, password):
                st.session_state.is_logged_in = True
                st.session_state.username = username
                st.rerun()
            else:
                st.error("Username atau password salah.")

    # st.info("Demo akun: username admin, password admin123")


def logout() -> None:
    st.session_state.is_logged_in = False
    st.session_state.username = ""
    st.rerun()


initialize_session()

if not st.session_state.is_logged_in:
    show_login_page()
    st.stop()

st.title("Aplikasi Streamlit")
st.caption("Template awal untuk proyek tugas akhir Python.")

with st.sidebar:
    st.success(f"Login sebagai {st.session_state.username}")
    st.button("Logout", on_click=logout, use_container_width=True)
    st.divider()
    st.header("Pengaturan")
    show_table = st.toggle("Tampilkan tabel", value=True)
    selected_metric = st.selectbox("Metrik grafik", ["Penjualan", "Target"])

data = load_sample_data()

total_penjualan = int(data["Penjualan"].sum())
total_target = int(data["Target"].sum())
selisih = total_penjualan - total_target

col1, col2, col3 = st.columns(3)
col1.metric("Total Penjualan", f"{total_penjualan:,}")
col2.metric("Total Target", f"{total_target:,}")
col3.metric("Selisih", f"{selisih:+,}")

st.subheader("Grafik Bulanan")
st.line_chart(data, x="Bulan", y=selected_metric)

if show_table:
    st.subheader("Data")
    st.dataframe(data, use_container_width=True, hide_index=True)

st.info("Edit file app.py untuk menyesuaikan aplikasi dengan kebutuhan tugas akhir.")
