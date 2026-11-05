import pytest
from energy_transition.efs_pinned_ordinal_bijection import SHIFTS, N, audit, forward, inverse


def test_eleven_states_and_pinned_offsets():
    report = audit()
    assert report["state_count"] == 11
    assert {x["pinned_fixed_offset_hours"] for x in report["states"]} == {7, 8}
    assert not report["actual_UTC_hourly_source_provenance_verified"]
    assert not report["synchronous_OPF_admitted"]


def test_wrap_and_inverse_for_all_source_hours():
    for shift in set(SHIFTS.values()):
        for source_hour in range(1, N + 1):
            transformed = forward(source_hour, shift)
            assert inverse(transformed, shift) == source_hour
        assert forward(N - shift + 1, shift) == 1
        assert forward(N, shift) == shift


@pytest.mark.parametrize("value", [0, -1, 8761])
def test_reject_out_of_range(value):
    with pytest.raises(ValueError):
        forward(value, 7)
    with pytest.raises(ValueError):
        inverse(value, 8)
