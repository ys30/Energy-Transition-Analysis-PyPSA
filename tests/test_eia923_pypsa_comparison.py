import pandas as pd
from energy_transition.eia923_pypsa_comparison import compare

class FakeNetwork:
    def __init__(self):
        idx=pd.date_range("2024-01-01",periods=2,freq="h")
        self.generators=pd.DataFrame({"bus":["CISO","CISO"]},index=["CISO_gas","CISO_unserved"])
        self.generators_t=type("Series",(),{})()
        self.generators_t.p=pd.DataFrame({"CISO_gas":[10.,20.],"CISO_unserved":[0.,0.]},index=idx)
        self.snapshot_weightings=pd.DataFrame({"generators":[1.,2.]},index=idx)

def test_compare_qualified_observation_and_weighted_dispatch():
    q=pd.DataFrame({"ba_code":["CISO"],"fuel":["NG"],
        "qualified_annual_mwh":[45.],"withheld_reported_annual_mwh":[2.],
        "source_rows":[3],"qualified_rows":[2]})
    out=compare(q,FakeNetwork()).iloc[0]
    assert out.tech=="gas"
    assert out.pypsa_dispatch_mwh==50.
    assert out.model_minus_qualified_observed_mwh==5.
    assert not bool(out.full_source_row_coverage)


def test_annual_discrepancy_requires_positive_observed_denominator():
    qualified = pd.DataFrame({
        "ba_code": ["CISO", "BPAT"], "fuel": ["NG", "WND"],
        "qualified_annual_mwh": [45.0, -5.0],
        "withheld_reported_annual_mwh": [2.0, 0.0],
        "source_rows": [3, 1], "qualified_rows": [2, 1],
    })
    out = compare(qualified, FakeNetwork())
    gas = out[(out.ba_code == "CISO") & (out.tech == "gas")].iloc[0]
    wind = out[(out.ba_code == "BPAT") & (out.tech == "wind")].iloc[0]
    assert gas.absolute_difference_mwh == 5.0
    assert abs(gas.absolute_percentage_difference - (5.0 / 45.0)) < 1e-12
    assert gas.benchmark_evidence_status == "partial_source_coverage"
    assert wind.benchmark_evidence_status == "unmatched_source_boundary"
    assert pd.isna(wind.absolute_percentage_difference)
    assert not bool(out.validated_hourly_calibration.any())


def test_nonpositive_observed_net_generation_is_not_percentage_accuracy():
    qualified = pd.DataFrame({
        "ba_code": ["CISO"], "fuel": ["NG"],
        "qualified_annual_mwh": [-2.0],
        "withheld_reported_annual_mwh": [0.0],
        "source_rows": [1], "qualified_rows": [1],
    })
    out = compare(qualified, FakeNetwork()).iloc[0]
    assert out.benchmark_evidence_status == "nonpositive_net_generation"
    assert pd.isna(out.absolute_percentage_difference)
    assert pd.isna(out.relative_difference_vs_qualified_observed)


def test_annual_comparison_rejects_misaligned_snapshots_and_bad_weights():
    import pytest
    qualified = pd.DataFrame({
        "ba_code": ["CISO"], "fuel": ["NG"], "qualified_annual_mwh": [45.0],
        "withheld_reported_annual_mwh": [0.0], "source_rows": [1], "qualified_rows": [1],
    })
    shifted = FakeNetwork()
    shifted.snapshot_weightings.index = shifted.snapshot_weightings.index + pd.Timedelta(hours=1)
    with pytest.raises(ValueError, match="snapshots and generator weights"):
        compare(qualified, shifted)
    invalid = FakeNetwork()
    invalid.snapshot_weightings.loc[invalid.snapshot_weightings.index[0], "generators"] = float("inf")
    with pytest.raises(ValueError, match="finite"):
        compare(qualified, invalid)
    negative = FakeNetwork()
    negative.snapshot_weightings.loc[negative.snapshot_weightings.index[0], "generators"] = 0.0
    with pytest.raises(ValueError, match="positive"):
        compare(qualified, negative)


def test_observed_only_when_network_has_no_supported_generators():
    network = FakeNetwork()
    network.generators = network.generators.loc[["CISO_unserved"]].copy()
    network.generators_t.p = network.generators_t.p[["CISO_unserved"]].copy()
    qualified = pd.DataFrame({
        "ba_code": ["CISO"], "fuel": ["NG"],
        "qualified_annual_mwh": [100.0],
        "withheld_reported_annual_mwh": [0.0],
        "source_rows": [1], "qualified_rows": [1],
    })
    out = compare(qualified, network)
    assert len(out) == 1
    row = out.iloc[0]
    assert row.comparison_status == "observed_only"
    assert row.benchmark_evidence_status == "unmatched_source_boundary"
    assert pd.isna(row.pypsa_dispatch_mwh)
    assert pd.isna(row.absolute_percentage_difference)


def test_ambiguous_generator_ba_prefix_fails_loudly():
    import pytest
    network = FakeNetwork()
    network.generators = network.generators.rename(index={"CISO_gas": "gas"})
    qualified = pd.DataFrame({
        "ba_code": ["CISO"], "fuel": ["NG"],
        "qualified_annual_mwh": [45.0],
        "withheld_reported_annual_mwh": [0.0], "source_rows": [1], "qualified_rows": [1],
    })
    with pytest.raises(ValueError, match="BA prefix"):
        compare(qualified, network)


def test_missing_generator_dispatch_column_fails_loudly():
    import pytest
    network = FakeNetwork()
    network.generators_t.p = network.generators_t.p.drop(columns=["CISO_gas"])
    qualified = pd.DataFrame({
        "ba_code": ["CISO"], "fuel": ["NG"],
        "qualified_annual_mwh": [45.0],
        "withheld_reported_annual_mwh": [0.0], "source_rows": [1], "qualified_rows": [1],
    })
    with pytest.raises(ValueError, match="Missing dispatch series"):
        compare(qualified, network)


def test_ba_coverage_summary_excludes_partial_and_unmatched_annual_totals():
    from energy_transition.eia923_pypsa_comparison import summarize_comparison
    q = pd.DataFrame({
        "ba_code": ["CISO", "CISO", "BPAT"],
        "fuel": ["NG", "WND", "WAT"],
        "qualified_annual_mwh": [45.0, 20.0, 100.0],
        "withheld_reported_annual_mwh": [0.0, 5.0, 0.0],
        "source_rows": [1, 2, 1],
        "qualified_rows": [1, 1, 1],
    })
    # CISO gas is comparable, while CISO wind and BPAT hydro
    # have no modeled counterpart.
    result = summarize_comparison(compare(q, FakeNetwork()))
    ciso = result[result.ba_code == "CISO"].iloc[0]
    bpat = result[result.ba_code == "BPAT"].iloc[0]
    assert ciso.qualified_annual_comparison_rows == 1
    assert ciso.matched_technology_fraction == 0.5
    assert ciso.qualified_annual_fraction == 0.5
    assert ciso.observed_only_rows == 1
    assert ciso.matched_qualified_eia923_mwh == 45.0
    assert ciso.matched_pypsa_mwh == 50.0
    assert bpat.observed_only_rows == 1
    assert bpat.matched_technology_fraction == 0.0
    assert bpat.qualified_annual_fraction == 0.0
    assert bpat.matched_qualified_eia923_mwh == 0.0
    assert not bool(result.validated_hourly_calibration.any())
