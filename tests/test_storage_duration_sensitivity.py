import pandas as pd
import pytest
from energy_transition.storage_duration_sensitivity import run_sensitivity

def test_duration_sensitivity_consistent_baselines(monkeypatch,tmp_path):
    def mock_solver(hourly,path,*,duration_h):
        return {
            "battery_mw_assumed":1000,
            "capacity_mwh_assumed":1000*duration_h,
            "battery_charge_mwh":10*duration_h,
            "battery_discharge_mwh":9*duration_h,
            "peaker_generation_mwh":100-duration_h,
            "peaker_generation_mwh_without_storage":100,
            "objective_usd_with_storage_assumed":1000-10*duration_h,
            "objective_usd_without_storage_assumed":1000,
            "operating_savings_usd_assumed":10*duration_h,
            "unserved_mwh":0,
            "max_storage_conservation_error_mwh":0,
        }
    monkeypatch.setattr("energy_transition.storage_duration_sensitivity.solve_window",mock_solver)
    df=run_sensitivity(pd.DataFrame(),tmp_path,durations=(2.,4.,6.,8.))
    assert df.duration_h.tolist()==[2,4,6,8]
    assert df.operating_savings_usd.tolist()==[20,40,60,80]
    assert (tmp_path/"storage_duration_sensitivity.csv").is_file()

def test_duration_sensitivity_rejects_duplicate_durations(tmp_path):
    with pytest.raises(ValueError,match="unique"):
        run_sensitivity(pd.DataFrame(),tmp_path,durations=(4.,4.))
