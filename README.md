# Early Warning System Kehadiran Pegawai

Dashboard Streamlit untuk memantau disiplin kehadiran pegawai, menampilkan status peringatan dini, analisis perilaku kedatangan, dan rekomendasi tindak lanjut administratif.

## Menjalankan aplikasi

```powershell
cd D:\tugas-akhir-phyton
.\.venv\Scripts\activate
streamlit run app.py
```

Jika virtual environment belum tersedia, buat dan pasang dependensi terlebih dahulu:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

## Akun demo

- Username: `admin`
- Kata sandi: `admin123`

## Fitur

- Sidebar untuk filter periode, unit kerja, serta pencarian pegawai.
- Indikator EWS berwarna: risiko tinggi, peringatan dini, dan aman.
- Grafik keterlambatan berdasarkan hari serta distribusi jam kedatangan.
- Tabel rekomendasi yang diurutkan otomatis dari akumulasi hari tanpa keterangan (TK) tertinggi.
- Contoh rekomendasi tindak lanjut mengacu pada PP No. 94 Tahun 2021.

## Sumber data ePresensi

Konfigurasi endpoint dilakukan pada layer sumber data tanpa menambahkan komponen
ke dashboard. Tahun dapat diatur melalui environment variable berikut:

```powershell
$env:EPRESENSI_TAHUN="2026"
streamlit run app.py
```

Daftar pegawai diambil otomatis untuk lima ID `OPD_TARGET`. Endpoint pegawai
memerlukan autentikasi resmi. Sediakan salah satu kredensial sesi yang sah:

```powershell
$env:EPRESENSI_BEARER_TOKEN="token-resmi"
# atau
$env:EPRESENSI_COOKIE="nama_cookie=nilai_cookie"
```

Untuk tahap uji, `OPD_AKTIF` berisi tepat 10 OPD. Ganti nama placeholder dengan
nama OPD yang sama persis seperti pada master pegawai. Sumber aktif dashboard
adalah ePresensi; data lama tidak menjadi fallback otomatis.
