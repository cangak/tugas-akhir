import pandas as pd

from modules.employee_type import (
    UNKNOWN_EMPLOYEE_TYPE,
    add_employee_type_columns,
    detect_employee_type_from_nip,
    normalize_nip,
    resolve_employee_type,
)


def test_detect_valid_synthetic_pns():
    assert detect_employee_type_from_nip("199001012020031001") == "PNS"


def test_detect_valid_synthetic_pppk():
    assert detect_employee_type_from_nip("199001012020211001") == "PPPK"


def test_invalid_nips_are_unknown():
    invalid = [None, "", "12345", "1" * 19, "19900101202003A001", "199013012020031001", "199001012020001001", "1.9900101202003E17"]
    assert all(detect_employee_type_from_nip(value) == UNKNOWN_EMPLOYEE_TYPE for value in invalid)


def test_normalize_nip_removes_safe_separators_without_numeric_conversion():
    assert normalize_nip(" 19900101-2020 031001 ") == "199001012020031001"


def test_master_overrides_detection_and_source_is_recorded():
    assert resolve_employee_type("199001012020211001", "PNS") == ("PNS", "MASTER")


def test_unique_nip_mapping_is_consistent_on_all_rows():
    frame = pd.DataFrame({"NIP": ["199001012020031001"] * 3 + ["invalid"]})
    result = add_employee_type_columns(frame)
    assert result.groupby("NIP", dropna=False)["Jenis Pegawai"].nunique().max() == 1
    assert result["Jenis Pegawai"].tolist() == ["PNS", "PNS", "PNS", UNKNOWN_EMPLOYEE_TYPE]
    assert result["Jenis Pegawai Source"].tolist() == ["NIP_DETECTION"] * 3 + ["UNKNOWN"]
