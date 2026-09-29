# Early Warning System Presensi

Dashboard Streamlit untuk monitoring kepatuhan presensi, Early Warning System (EWS), verifikasi tindak lanjut, dan laporan TK.

## Menjalankan aplikasi

```powershell
cd D:\tugas-akhir-phyton
.\.venv\Scripts\activate
streamlit run app.py
```

Akun demo: `admin` / `admin123`.

## Sumber data

Sumber aktif default adalah file Excel rekap presensi di folder `data/`. Semua halaman memakai bentuk data harian canonical yang sama sehingga dashboard, EWS, dan laporan TK tidak menghitung dari sumber berbeda.

```env
DATA_SOURCE=excel
ALLOW_EXCEL_FALLBACK=false
```

PostgreSQL merupakan backend opsional. Aktifkan secara eksplisit:

```env
DATA_SOURCE=postgres
DATABASE_URL=postgresql+psycopg2://USER:PASSWORD@localhost:5432/presensi_db
ALLOW_EXCEL_FALLBACK=false
```

Jika koneksi PostgreSQL gagal, aplikasi tidak berpindah diam-diam ke Excel. Fallback hanya terjadi bila `ALLOW_EXCEL_FALLBACK=true`.

ETL PostgreSQL dijalankan terpisah dan tidak dijalankan pada setiap rerun Streamlit:

```powershell
python -m etl.presensi_etl
```

ETL menggunakan UPSERT dengan identitas unik NIP + tanggal. Modul ePresensi masih bersifat eksperimental/future development dan bukan sumber aktif default.

## Logika analitik

KPI organisasi adalah **Tingkat Kepatuhan Presensi**:

```text
(Hari Kerja - TK) / Hari Kerja × 100%
```

Cuti, WFH, dan DL merupakan kondisi sah sehingga tidak mengurangi kepatuhan.

Status EWS berasal dari `modules.analytics`:

- TK 0: Normal
- TK 1–2: Perlu Perhatian
- TK 3–5: Perlu Verifikasi
- TK ≥6: Prioritas Tindak Lanjut

Keterlambatan merupakan indikator tambahan dan tidak menentukan status EWS. PP 94/2021 hanya dipetakan untuk PNS setelah hari tanpa alasan sah diverifikasi di Action Center; hasil sistem merupakan indikasi pendukung, bukan keputusan hukuman.

## Pengujian

```powershell
python -m pytest -q
```
