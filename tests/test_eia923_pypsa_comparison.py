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
