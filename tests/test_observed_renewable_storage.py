import pandas as pd
import pytest
from energy_transition.observed_renewable_storage import prepare_injections
from energy_transition.seasonal_storage_sensitivity import SEASON_WEEKS

def test_signed_injections_preserved_by_hour_and_ba():
    rows=[]
    for season,start in SEASON_WEEKS.items():
        for period in pd.date_range(pd.Timestamp(start),periods=168,freq="h"):
            for ba in ("CISO","BPAT"):
                for fuel in ("SUN","WND"):
                    rows.append({"season":season,"period":period,"respondent":ba,
                                 "fueltype":fuel,"reported_signed_net_mwh":-2 if fuel=="SUN" else 9})
    frame=pd.DataFrame(rows)
    result=prepare_injections(frame)
    assert set(result)==set(SEASON_WEEKS)
    assert result["summer"].iloc[0]==14
    with pytest.raises(ValueError,match="Missing or unexpected"):
        prepare_injections(frame.iloc[1:])

def test_duplicate_renewable_hour_rejected():
    frame=pd.DataFrame([{"season":"winter","period":"2024-01-08T00:00:00Z",
      "respondent":"CISO","fueltype":"SUN","reported_signed_net_mwh":-1}])
    with pytest.raises(ValueError,match="Duplicate"):
        prepare_injections(pd.concat([frame,frame]))

def test_cost_attribution_and_peaker_displacement(monkeypatch,tmp_path):
    from energy_transition.observed_renewable_storage import compare
    from energy_transition.seasonal_storage_sensitivity import SEASON_WEEKS
    rows=[]
    demand=[]
    for season,start in SEASON_WEEKS.items():
        for period in pd.date_range(pd.Timestamp(start),periods=168,freq="h"):
            demand.append({"period":period,"respondent":"CISO","value":100.})
            for ba in ("CISO","BPAT"):
                for fuel in ("SUN","WND"):
                    rows.append({"season":season,"period":period,"respondent":ba,
                      "fueltype":fuel,"reported_signed_net_mwh":2.})
    def fake_solve(window,path,*,duration_h,require_activity,renewable_net_mw):
        return {"observed_signed_renewable_mwh":None if renewable_net_mw is None else float(renewable_net_mw.sum()),
          "unserved_mwh":0.,"unserved_mwh_without_storage":0.,
          "battery_charge_mwh":10.,"battery_discharge_mwh":9.,
          "peaker_generation_mwh":20.,"peaker_generation_mwh_without_storage":29.,
          "firm_generation_mwh_with_storage":100.,"firm_generation_mwh_without_storage":90.,
          "assumed_voll_usd_per_mwh":10000.,"operating_savings_usd_assumed":100.,
          "max_storage_conservation_error_mwh":0.}
    monkeypatch.setattr("energy_transition.observed_renewable_storage.solve_window",fake_solve)
    result=compare(pd.DataFrame(demand),pd.DataFrame(rows),tmp_path)
    assert len(result)==8
    assert (result.peaker_avoided_mwh==9).all()
    assert (result.firm_extra_mwh==10).all()
    assert (result.avoided_unserved_penalty_usd==0).all()
    assert (result.other_dispatch_savings_usd==100).all()
