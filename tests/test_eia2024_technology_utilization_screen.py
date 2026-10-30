import pandas as pd
import pytest
from energy_transition.eia2024_technology_utilization_screen import calculate

def test_two_ba_aggregate_screen_no_fake_ba_calibration():
    c=pd.DataFrame([{"ba_code":"CISO","fuel":"NG","capacity_mw":100.},
      {"ba_code":"BPAT","fuel":"NG","capacity_mw":100.},
      {"ba_code":"BPAT","fuel":"WAT","capacity_mw":200.}])
    q=pd.DataFrame([{"carrier":"gas","observed_eia923_net_generation_mwh":87840.}])
    out=calculate(c,q)
    gas=out[out.carrier.eq("gas")].iloc[0]
    assert gas.capacity_mw==200
    assert gas.qualified_generation_over_nameplate_hours==.05
    assert not out.capacity_calibrated.any()
    assert out[out.carrier.eq("hydro")].qualified_generation_over_nameplate_hours.isna().all()

def test_duplicate_ba_fuel_rejected():
    c=pd.DataFrame([{"ba_code":"CISO","fuel":"NG","capacity_mw":100.}]*2)
    q=pd.DataFrame(columns=["carrier","observed_eia923_net_generation_mwh"])
    with pytest.raises(ValueError,match="Duplicate"):
        calculate(c,q)
