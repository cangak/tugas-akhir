"""Koneksi PostgreSQL berbasis environment variable."""

from __future__ import annotations

import os

from dotenv import load_dotenv
from sqlalchemy import Engine, create_engine


def get_engine(database_url: str | None = None) -> Engine:
    """Buat engine sekali per proses tanpa mengekspos credential ke log."""
    load_dotenv()
    url = database_url or os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL belum dikonfigurasi.")
    if not url.startswith(("postgresql://", "postgresql+psycopg2://")):
        raise RuntimeError("DATABASE_URL harus menggunakan PostgreSQL.")
    return create_engine(url, pool_pre_ping=True)

