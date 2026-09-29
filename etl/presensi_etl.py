"""Jalankan dengan: python -m etl.presensi_etl"""

from __future__ import annotations

import logging

from sqlalchemy.exc import SQLAlchemyError

from database.connection import get_engine
from database.repository import save_daily_attendance_to_db
from modules.excel_parser import load_semua_presensi


logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
LOGGER = logging.getLogger(__name__)


def run() -> dict[str, object]:
    clean_daily = load_semua_presensi()
    LOGGER.info("Record hasil cleaning: %s", len(clean_daily))
    engine = get_engine()
    try:
        report = save_daily_attendance_to_db(clean_daily, engine)
    finally:
        engine.dispose()
    LOGGER.info(
        "Processed: %s | Valid: %s | Insert: %s | Update: %s | Ditolak: %s",
        report["processed"], report["valid"], report["inserted"],
        report["updated"], report["rejected"],
    )
    if report["rejected"]:
        LOGGER.warning("Validation report: %s", report["rejection_reasons"])
    return report


if __name__ == "__main__":
    try:
        run()
    except (RuntimeError, SQLAlchemyError) as exc:
        LOGGER.debug("Detail kegagalan database", exc_info=True)
        raise SystemExit(
            "Koneksi PostgreSQL gagal. Periksa konfigurasi DATABASE_URL dan status server database."
        ) from None
