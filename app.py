import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="Aplikasi Streamlit",
    page_icon="📊",
    layout="wide",
)


def load_sample_data() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Bulan": ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun"],
            "Penjualan": [120, 150, 180, 130, 210, 260],
            "Target": [100, 140, 160, 170, 190, 230],
        }
    )


st.title("Aplikasi Streamlit")
st.caption("Template awal untuk proyek tugas akhir Python.")

with st.sidebar:
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
