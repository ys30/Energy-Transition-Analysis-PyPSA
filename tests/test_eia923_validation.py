import pandas as pd
import pytest

from energy_transition.eia923_validation import compare_generation


def _fixtures():
    generation = pd.DataFrame({
        "plant_id": ["101", "102", "101"],
        "report_year": [2024] * 3,
        "month": [1, 1, 2],
        "fuel": ["gas", "wind", "gas"],
        "net_generation_mwh": [100, 40, -5],
    })
    mapping = pd.DataFrame({
        "plant_id": ["101", "102"],
        "ba_code": ["CISO", "CISO"],
        "mapping_year": [2024, 2024],
    })
    metrics = {"dispatch_mwh_by_carrier": {"gas": 110, "wind": 35}}
    return generation, mapping, metrics


def test_eia923_validation_preserves_negative_net_generation():
    g, x, m = _fixtures()
    result, audit = compare_generation(g, x, m, year=2024, bas=("CISO",))
    gas = result.set_index("carrier").loc["gas"]
    assert gas.observed_eia923_net_generation_mwh == 95
    assert gas.model_minus_observed_mwh == 15
    assert audit["negative_net_generation_rows"] == 1


def test_eia923_rejects_wrong_crosswalk_year():
    g, x, m = _fixtures()
    x["mapping_year"] = 2023
    with pytest.raises(ValueError, match="match analysis year"):
        compare_generation(g, x, m, year=2024, bas=("CISO",))


def test_eia923_audits_unmapped_national_plant():
    g, x, m = _fixtures()
    result, audit = compare_generation(g, x.iloc[:1], m, year=2024, bas=("CISO",))
    assert audit["unmapped_national_plant_count"] == 1
    assert audit["selected_ba_completeness"].startswith("unverified")
    assert result.set_index("carrier").loc["gas", "observed_eia923_net_generation_mwh"] == 95


def test_eia923_audits_observed_only_fuel_without_false_zero_comparison():
    g, x, m = _fixtures()
    g.loc[0, "fuel"] = "biomass"
    result, audit = compare_generation(g, x, m, year=2024, bas=("CISO",))
    assert "biomass" not in result.carrier.tolist()
    assert audit["observed_only_fuels_excluded_from_comparison_mwh"] == {"biomass": 100.0}
    assert "gas" in result.carrier.tolist()


def test_reject_duplicate_plant_month_fuel():
    g, x, m = _fixtures()
    repeated = pd.concat([g, g.iloc[[0]]], ignore_index=True)
    with pytest.raises(ValueError, match='Duplicate normalized'):
        compare_generation(repeated, x, m, year=2024, bas=('CISO',))


def test_reject_no_common_model_fuel():
    g, x, m = _fixtures()
    g['fuel'] = 'biomass'
    with pytest.raises(ValueError, match='No common observed/model carriers'):
        compare_generation(g, x, m, year=2024, bas=('CISO',))


@pytest.mark.parametrize('bad_value', [float('nan'), float('inf'), -1.0, 'invalid'])
def test_reject_invalid_modeled_dispatch(bad_value):
    g, x, m = _fixtures()
    m['dispatch_mwh_by_carrier']['gas'] = bad_value
    with pytest.raises(ValueError, match='model dispatch'):
        compare_generation(g, x, m, year=2024, bas=('CISO',))


def test_reject_blank_observed_fuel():
    g, x, m = _fixtures()
    g.loc[0, 'fuel'] = '  '
    with pytest.raises(ValueError, match='Blank EIA-923 fuel'):
        compare_generation(g, x, m, year=2024, bas=('CISO',))


def test_strip_observed_fuel_whitespace_before_comparison():
    g, x, m = _fixtures()
    g.loc[0, 'fuel'] = ' gas '
    result, audit = compare_generation(g, x, m, year=2024, bas=('CISO',))
    assert result.set_index('carrier').loc['gas', 'observed_eia923_net_generation_mwh'] == 95
