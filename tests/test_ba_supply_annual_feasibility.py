import pandas as pd
from energy_transition.ba_supply_annual_feasibility import screen

def test_ba_technology_annual_feasibility_and_qualification():
    capacity=pd.DataFrame([
      {"ba_code":"CISO","fuel":"NG","capacity_mw":10.},
      {"ba_code":"CISO","fuel":"OG","capacity_mw":5.},
      {"ba_code":"BPAT","fuel":"WAT","capacity_mw":20.}])
    observed=pd.DataFrame([
      {"ba_code":"CISO","fuel":"NG","qualified_annual_mwh":10000.,"withheld_reported_annual_mwh":100.,"source_rows":10,"qualified_rows":8},
      {"ba_code":"CISO","fuel":"OG","qualified_annual_mwh":1000.,"withheld_reported_annual_mwh":0.,"source_rows":2,"qualified_rows":2},
      {"ba_code":"BPAT","fuel":"WAT","qualified_annual_mwh":200000.,"withheld_reported_annual_mwh":0.,"source_rows":3,"qualified_rows":3}])
    result=screen(capacity,observed)
    gas=result[(result.ba_code=="CISO")&(result.technology=="gas")].iloc[0]
    hydro=result[(result.ba_code=="BPAT")&(result.technology=="hydro")].iloc[0]
    assert gas.nameplate_mw==15
    assert gas.qualified_mwh==11000
    assert not bool(gas.qualified_rows_complete)
    assert bool(hydro.energy_exceeds_nameplate)
    assert not result.ready_for_hourly_calibration.any()
