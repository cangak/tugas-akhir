import pandas as pd

from modules.excel_parser import load_semua_presensi


def test_source_has_no_duplicate_employee_date():
    data = load_semua_presensi()
    assert not data.duplicated(["NIP", "Tanggal"]).any()
    assert data.attrs["etl_quality"]["records_valid"] == len(data)
