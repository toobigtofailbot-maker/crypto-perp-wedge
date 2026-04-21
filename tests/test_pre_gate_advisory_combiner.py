import pytest

from tools.mappers.pre_gate_advisory_combiner import combine_pre_gate_advisory_bucket


@pytest.mark.parametrize(
    ("macro_window_flag", "mapped_bucket", "expected"),
    [
        (False, "ALLOW", "ALLOW"),
        (False, "ALLOW_REDUCED", "ALLOW_REDUCED"),
        (False, "BLOCK", "BLOCK"),
        (True, "ALLOW", "ALLOW_REDUCED"),
        (True, "ALLOW_REDUCED", "ALLOW_REDUCED"),
        (True, "BLOCK", "BLOCK"),
    ],
)
def test_macro_aware_floor_rule_matrix(macro_window_flag, mapped_bucket, expected):
    assert combine_pre_gate_advisory_bucket(mapped_bucket, macro_window_flag) == expected


def test_macro_aware_floor_rejects_unknown_bucket():
    with pytest.raises(ValueError):
        combine_pre_gate_advisory_bucket("PAUSE", True)
