import pandas as pd
import pytest
from energy_transition.paper_s_soc_tiebreak_figures import validate,plot,PROBES,MODES

def fixture():
    rows=[]
    for grp,state in ((1,"Arizona"),(7,"Wyoming")):
        for shape,p,e in PROBES:
            for mode in MODES:
                rows.append({"source_shape_group":grp,"state":state,"reeds_zone":"p28" if grp==1 else "p24",
                    "synthetic_supply_shape":shape,"battery_power_peak_ratio":p,
                    "battery_energy_peak_hours":e,"perturbation_mode":mode,
                    "original_objective_gap_usd":0.,
                    "soc_bound_hours_delta":0 if mode=="baseline" else 3,
                    "max_abs_hourly_soc_change_mwh":0. if mode=="baseline" else 10.,
                    "near_optimal_within_1ppm":True})
    return pd.DataFrame(rows)

def test_original_audited_population_and_plot(tmp_path):
    result=plot(fixture(),tmp_path)
    assert result["candidate_schedules"]==32
    assert (tmp_path/"Figure_S15_SOC_schedule_sensitivity.png").stat().st_size>1000

def test_nonmatching_case_fails_closed():
    with pytest.raises(ValueError,match="32-case"):
        validate(fixture().iloc[:-1])

def test_large_source_objective_gap_rejected():
    a=fixture();a.loc[0,"original_objective_gap_usd"]=5.
    with pytest.raises(ValueError,match="too large"):validate(a)
