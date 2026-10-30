import pandas as pd
import pytest
from energy_transition.summer_voll_sensitivity import run

def test_voll_sensitivity_reoptimizes_each_case(monkeypatch,tmp_path):
    observed=[]
    def fake_solver(hourly,path,*,duration_h,require_activity,voll_usd_per_mwh):
        observed.append(voll_usd_per_mwh)
        return {
            "unserved_mwh":10,"unserved_mwh_without_storage":15,
            "operating_savings_usd_assumed":5*voll_usd_per_mwh+100,
            "battery_discharge_mwh":20,"max_storage_conservation_error_mwh":0,
        }
    monkeypatch.setattr("energy_transition.summer_voll_sensitivity.solve_window",fake_solver)
    data=run(pd.DataFrame(),tmp_path,volls=(1000.,5000.))
    assert observed==[1000.,5000.]
    assert data.penalty_benefit_usd.tolist()==[5000.,25000.]
    assert data.other_dispatch_savings_usd.tolist()==[100.,100.]
    assert (tmp_path/"summer_voll_sensitivity.csv").is_file()

def test_voll_rejects_invalid_penalties(tmp_path):
    with pytest.raises(ValueError,match="unique"):
        run(pd.DataFrame(),tmp_path,volls=(1000.,1000.))
