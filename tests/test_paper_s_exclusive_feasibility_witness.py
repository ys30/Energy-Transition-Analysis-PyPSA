import numpy as np
import pandas as pd
import pytest
from energy_transition.paper_s_exclusive_feasibility_witness import certify

def source():
    rows=[]
    sums=[]
    for mode in ("baseline","min","max"):
        for hour in range(1,8761):
            charge=5. if (mode=="max" and hour==4035) else 0.
            discharge=3.6 if charge else 0.
            rows.append({"solution":mode,"local_hour_id":hour,
                "storage_charge_input_mwh":charge,
                "storage_discharge_to_load_mwh":discharge,
                "soc_end_mwh":0.,"firm_generation_mwh":0.,
                "unused_renewable_mwh":0.})
        sums.append({"solution":mode,"window_discharge_mwh":3.6 if mode=="max" else 0.,
             "annual_discharge_mwh":discharge if mode=="max" else 0.,
             "original_cost_usd":100000.,"allowed_extra_cost_usd":1.})
    return pd.DataFrame(rows),pd.DataFrame(sums)

def test_exclusive_transformation_and_feasible_bounds():
    x,y=source()
    certificate,bounds=certify(x,y,"toy")
    assert len(certificate)==3
    assert certificate.simultaneous_hours_after.eq(0).all()
    assert bounds["exclusive_interval_width_at_least_mwh"]==0.
    assert bounds["retained_relaxed_interval_width_at_least_percent"]==0.

def test_incomplete_hourly_population_fails_closed():
    a,b=source()
    with pytest.raises(ValueError,match="26280"):
        certify(a.iloc[:-1],b,"toy")
