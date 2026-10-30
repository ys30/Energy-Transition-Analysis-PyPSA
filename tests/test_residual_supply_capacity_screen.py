import pandas as pd
import pytest
from energy_transition.residual_supply_capacity_screen import audit

def test_nameplate_not_misclassified_as_calibrated_firm_power():
    d=pd.DataFrame([{"ba_code":"CISO","fuel":"NG","capacity_mw":30000},
                    {"ba_code":"BPAT","fuel":"WAT","capacity_mw":18000},
                    {"ba_code":"CISO","fuel":"SUN","capacity_mw":20000}])
    detail,report=audit(d)
    assert report["capacity_calibrated"] is False
    assert report["thermal_nuclear_nameplate_mw"]==30000
    assert report["thermal_nuclear_hydro_geo_nameplate_mw"]==48000
    assert report["wind_solar_nameplate_mw"]==20000
    assert report["assumed_dispatchable_supply_mw"]==75000

def test_missing_ba_rejected():
    with pytest.raises(ValueError,match="BAs absent"):
        audit(pd.DataFrame([{"ba_code":"CISO","fuel":"NG","capacity_mw":10}]))
