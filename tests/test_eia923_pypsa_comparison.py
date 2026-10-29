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
