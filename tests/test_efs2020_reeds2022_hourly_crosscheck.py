import numpy as np
import pytest
from energy_transition.efs2020_reeds2022_hourly_crosscheck import compare_arrays

def reference():
    h=np.arange(8760)
    return 100+12*np.sin(2*np.pi*h/24)+0.008*h

def test_perfect_original_source_ordinal_alignment():
    a=reference()
    r=compare_arrays(a,a.copy())
    assert r["direct_ordinal_all_8760_match"]
    assert r["direct_ordinal_matching_hours"]==8760
    assert r["best_offset_hours"]==0
    assert r["shift_uniquely_identified"]

def test_hour_shift_recognized_even_if_annual_total_identical():
    a=reference()
    b=np.roll(a,7)
    r=compare_arrays(a,b)
    assert r["annual_energy_match_under_numeric_tolerance"]
    assert not r["direct_ordinal_all_8760_match"]
    assert r["best_offset_hours"]==-7
    assert r["best_offset_all_8760_match"]

def test_nonshifted_same_annual_energy_but_wrong_hourly_shape_rejected():
    a=reference()
    b=a[::-1]
    r=compare_arrays(a,b)
    assert r["annual_energy_match_under_numeric_tolerance"]
    assert not r["direct_ordinal_all_8760_match"]
    assert not r["best_offset_all_8760_match"]

def test_corrupted_single_source_hour_not_mislabeled_exact():
    a=reference()
    b=a.copy()
    b[100]+=1.
    r=compare_arrays(a,b)
    assert r["direct_ordinal_matching_hours"]==8759
    assert not r["direct_ordinal_all_8760_match"]

def test_nonfinite_source_fails_closed():
    a=reference()
    a[3]=np.nan
    with pytest.raises(ValueError,match="Invalid"):
        compare_arrays(a,reference())

def test_missing_source_hour_fails_closed():
    with pytest.raises(ValueError,match="8760"):
        compare_arrays(reference()[:-1],reference())

def test_integer_mw_publisher_rounding_recognized_after_fixed_shift():
    source=reference()+0.137
    publisher=np.roll(np.round(source),2)
    r=compare_arrays(source,publisher)
    assert not r["direct_ordinal_all_8760_match"]
    assert r["best_offset_hours"]==-2
    assert r["best_offset_all_8760_rounding_equivalent"]
    assert r["best_offset_hours_within_half_MW_rounding"]==8760
    assert r["best_offset_max_abs_error_mw"]<=0.500001


def test_large_residual_still_distinguished_from_half_mw_rounding():
    source=reference()+0.137
    publisher=np.roll(np.round(source),3)
    publisher[400]+=35
    r=compare_arrays(source,publisher)
    assert not r["best_offset_all_8760_rounding_equivalent"]
    assert r["best_offset_hours_above_1_MW_error"]>=1

def test_exploratory_mixture_of_two_shifted_sequences_is_identifiable_numerically():
    independent=reference()
    a=0.4*np.roll(independent,-2)+0.6*np.roll(independent,-3)
    r=compare_arrays(a,independent)
    assert r["exploratory_two_shift_minus2_weight"]==pytest.approx(0.4,abs=1e-9)
    assert r["exploratory_two_shift_mix_mae_mw"]<1e-8
    assert r["exploratory_two_shift_mix_is_physical_timezone_attribution"] is False
