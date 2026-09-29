import numpy as np
import pandas as pd

from modules.display import format_percentage_exact, safe_display


def test_safe_display_normalizes_technical_nulls():
    expected = "Tidak ada indikasi tindak lanjut"
    for value in (np.nan, pd.NA, None, "", "  nan  ", "None", "N/A", "<NA>"):
        assert safe_display(value) == expected


def test_safe_display_preserves_real_value():
    assert safe_display("Teguran / Verifikasi") == "Teguran / Verifikasi"


def test_percentage_format_uses_two_decimals_for_exact_hundred():
    assert format_percentage_exact(100.0) == "100,00%"


def test_percentage_format_does_not_round_sub_hundred_to_hundred():
    assert format_percentage_exact(99.96) == "99,96%"
    assert format_percentage_exact(99.995) == "99,995%"
    assert format_percentage_exact(97.642) == "97,64%"
