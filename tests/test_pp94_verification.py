import pytest

from modules.pp94 import evaluate_pp94_indicator


def test_pp94_requires_verification_and_is_not_applicable_to_pppk():
    pending = evaluate_pp94_indicator(year=2026, recorded_tk_days=21, employee_type="PNS")
    assert pending["verification_status"] == "NEEDS_VERIFICATION"
    assert pending["discipline_level"] is None
    pppk = evaluate_pp94_indicator(year=2026, recorded_tk_days=21, employee_type="PPPK", verified_unexcused_days=21)
    assert pppk["verification_status"] == "NOT_APPLICABLE"


@pytest.mark.parametrize(("days", "level"), [(3, "Ringan"), (11, "Sedang"), (21, "Berat")])
def test_pp94_verified_boundaries(days, level):
    result = evaluate_pp94_indicator(year=2026, recorded_tk_days=days, employee_type="PNS", verified_unexcused_days=days)
    assert result["discipline_level"] == level
    assert result["is_final_decision"] is False


def test_verified_days_cannot_exceed_recorded_tk():
    with pytest.raises(ValueError, match="melebihi"):
        evaluate_pp94_indicator(year=2026, recorded_tk_days=3, employee_type="PNS", verified_unexcused_days=4)
