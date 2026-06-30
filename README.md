# Proyek Streamlit

Template awal aplikasi Streamlit untuk tugas akhir Python.

## Menjalankan aplikasi

1. Buat virtual environment:

   ```bash
   python -m venv .venv
   ```

2. Aktifkan virtual environment:

   Windows PowerShell:

   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

   Command Prompt:

   ```cmd
   .venv\Scripts\activate.bat
   ```

3. Install dependency:

   ```bash
   pip install -r requirements.txt
   ```

4. Jalankan Streamlit:

   ```bash
   streamlit run app.py
   ```

## Struktur

```text
.
├── app.py
├── requirements.txt
├── README.md
└── .streamlit/
    └── config.toml
```

## Catatan

Ubah isi `app.py` untuk menambahkan fitur, membaca dataset, atau membuat halaman dashboard sesuai kebutuhan.
