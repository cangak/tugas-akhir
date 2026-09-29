import pytest

from modules.monitoring_rules import evaluate_attendance_monitoring_rule


@pytest.mark.parametrize(("days", "band", "status", "article"), [
    (0, "0–2 hari", "Monitoring", None),
    (2, "0–2 hari", "Monitoring", None),
    (3, "3 hari", "Perlu Perhatian", "Pasal 10 ayat (1) huruf c"),
    (5, "4–6 hari", "Perlu Verifikasi", "Pasal 10 ayat (1) huruf c"),
    (8, "7–10 hari", "Prioritas Tindak Lanjut", "Pasal 10 ayat (1) huruf c"),
    (12, "11–13 hari", "Prioritas Tindak Lanjut", "Pasal 11"),
    (15, "14–16 hari", "Prioritas Tindak Lanjut", "Pasal 11"),
    (18, "17–20 hari", "Prioritas Tindak Lanjut", "Pasal 11"),
    (21, "≥21 hari", "Prioritas Verifikasi", "Pasal 12"),
    (99, "≥21 hari", "Prioritas Verifikasi", "Pasal 12"),
])
def test_reference_bands(days, band, status, article):
    result = evaluate_attendance_monitoring_rule(days)
    assert result["reference_band"] == band
    assert result["reference_status"] == status
    assert result["reference_article"] == article


def test_consecutive_monitoring_has_priority():
    result = evaluate_attendance_monitoring_rule(10, 10, True)
    assert result["special_monitoring_flag"] is True
    assert result["reference_status"] == "Prioritas Verifikasi"
    assert result["reference_article"] == "Pasal 12"
    assert "Memerlukan verifikasi lebih lanjut" in result["monitoring_note"]


def test_output_contract_has_no_punishment_fields_or_descriptions():
    forbidden_keys = {"discipline_level", "punishment", "sanction", "penalty", "hukuman"}
    forbidden_text = ["teguran", "pemotongan", "penurunan jabatan", "pembebasan", "pemberhentian"]
    for days in [0, 3, 5, 8, 12, 15, 18, 22, 28]:
        result = evaluate_attendance_monitoring_rule(days)
        assert forbidden_keys.isdisjoint(result)
        rendered = " ".join(str(value).lower() for value in result.values())
        assert not any(term in rendered for term in forbidden_text)


def test_employee_type_is_metadata_only():
    pns = evaluate_attendance_monitoring_rule(12, employee_type="PNS")
    pppk = evaluate_attendance_monitoring_rule(12, employee_type="PPPK")
    assert pns["reference_band"] == pppk["reference_band"]
    assert pns["reference_status"] == pppk["reference_status"]
