"""Cost-capped minimum-throughput dispatch versus window-service extrema.

The secondary minimization of total yearly discharge penalizes unnecessary
battery cycling. It is a *selection convention*, not empirical battery cost.
All computed traces are evaluated under the original unperturbed LP objective.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd
from .efs_cyclic_storage_lp import solve_zone
from .efs_ordinal_storage_sensitivity import shape_cf
from .paper_s_window_discharge_envelope import SHAPE,POWER,ENERGY,WINDOWS
from .paper_s_soc_optimal_envelope import RELATIVE_BUDGET,MINIMUM_BUDGET_USD,COST_NUMERICAL_SLACK_USD

SELECTED="middle_4001_4168"
def compare(hourly,accepted_source,accepted_annual,accepted_window,group):
    if group not in (1,7):raise ValueError("Only preregistered original demand groups 1 and 7")
    s=hourly[(hourly.synthetic_supply_shape=="flat_50pct")&
             (hourly.battery_duration_h==0)].sort_values("local_hour_id")
    if len(s)!=8760 or not np.array_equal(s.local_hour_id.to_numpy(),np.arange(1,8761)):
        raise ValueError("Missing exact original 8760-source-hour chronology")
    if s[["planning_year","state","reeds_zone"]].drop_duplicates().shape[0]!=1 or int(s.planning_year.iloc[0])!=2030:
        raise ValueError("Source group identity/year mismatch")
    demand=s.demand_mwh.to_numpy(dtype=float)
    if not np.isfinite(demand).all() or (demand<0).any() or demand.max()<=0:
        raise ValueError("Invalid source projected demand")
    kw=dict(battery_power_peak_ratio=POWER,storage_energy_peak_hours=ENERGY)
    cf=shape_cf(np.arange(1,8761),SHAPE)
    original,base=solve_zone(demand,cf,4,return_trace=True,**kw)
    optimum=float(original["objective_illustrative_variable_usd"])
    prior=accepted_source[(accepted_source.synthetic_supply_shape==SHAPE)&
                          (accepted_source.battery_duration_h==4)]
    if len(prior)!=1 or not np.isclose(optimum,float(prior.annual_toy_cost_usd.iloc[0]),atol=.03,rtol=1e-9):
        raise ValueError("Original archived 4h cyclic optimal objective changed")
    cap_budget=max(MINIMUM_BUDGET_USD,RELATIVE_BUDGET*optimum)
    start,end=WINDOWS[SELECTED]
    mask=np.zeros(8760);mask[start-1:end]=1.
    selected=solve_zone(demand,cf,4,return_trace=True,
        discharge_extremum="min",original_cost_ceiling_usd=optimum+cap_budget,**kw)
    archival=accepted_annual[(accepted_annual.synthetic_supply_shape==SHAPE)&
           (accepted_annual.battery_power_peak_ratio==POWER)&
           (accepted_annual.battery_energy_peak_hours==ENERGY)&
           (accepted_annual.solution=="min")]
    if len(archival)!=1:raise ValueError("Accepted annual min-throughput case missing")
    original_window=accepted_window[(accepted_window.window==SELECTED)&
                                   (accepted_window.source_shape_group==group)]
    if len(original_window)!=3 or set(original_window.solution)!={"baseline","min","max"}:
        raise ValueError("Accepted original window extrema missing")
    result,trace=selected
    annual=float(trace.storage_discharge_to_load_mwh.sum())
    window=float(trace.storage_discharge_to_load_mwh.to_numpy()@mask)
    cost=float(result["objective_illustrative_variable_usd"])
    if abs(annual-float(archival.annual_discharge_mwh.iloc[0]))>.1 or abs(cost-float(archival.original_cost_candidate_usd.iloc[0]))>.05:
        raise ValueError("Canonical minimum-throughput does not reproduce archived LP")
    if cost>optimum+cap_budget+COST_NUMERICAL_SLACK_USD or result["max_equality_residual_mwh"]>1e-5:
        raise ValueError("Canonical solution fails original objective/energy constraints")
    old=original_window.set_index("solution")
    lower=float(old.loc["min","window_discharge_mwh"])
    upper=float(old.loc["max","window_discharge_mwh"])
    if window<lower-.1 or window>upper+.1:
        raise ValueError("Canonical minimum-throughput is outside accepted window range")
    baseline_window=float(base.storage_discharge_to_load_mwh.to_numpy()@mask)
    summary=pd.DataFrame([dict(source_shape_group=group,state=str(s.state.iloc[0]),
        reeds_zone=str(s.reeds_zone.iloc[0]),canonical_rule="minimize annual delivered battery MWh",
        original_optimal_cost_usd=optimum,allowed_extra_cost_usd=cap_budget,
        canonical_original_cost_usd=cost,canonical_original_cost_gap_usd=cost-optimum,
        canonical_annual_discharge_mwh=annual,
        canonical_window_discharge_mwh=window,
        original_window_discharge_mwh=baseline_window,
        accepted_window_min_mwh=lower,accepted_window_max_mwh=upper,
        normalized_canonical_window_position=(
            (window-lower)/(upper-lower) if upper-lower>1e-4 else float("nan")),
        canonical_mean_soc_mwh=float(trace.soc_end_mwh.mean()),
        original_mean_soc_mwh=float(base.soc_end_mwh.mean()),
        canonical_annual_charge_mwh=float(trace.storage_charge_input_mwh.sum()),
        full_source_hours=8760,independent_hourly_conservation_verified=True)])
    out=trace[["local_hour_id","storage_charge_input_mwh",
               "storage_discharge_to_load_mwh","soc_end_mwh",
               "firm_generation_mwh","unused_renewable_mwh"]].copy()
    out.insert(0,"source_shape_group",group)
    out["in_selected_window"]=mask.astype(bool)
    return summary,out

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--hourly",type=Path,required=True)
    ap.add_argument("--original-metrics",type=Path,required=True)
    ap.add_argument("--accepted-annual",type=Path,required=True)
    ap.add_argument("--accepted-window",type=Path,required=True)
    ap.add_argument("--group",type=int,choices=(1,7),required=True)
    ap.add_argument("--out-dir",type=Path,required=True)
    a=ap.parse_args()
    m,t=compare(pd.read_csv(a.hourly,compression="infer"),
      pd.read_csv(a.original_metrics),pd.read_csv(a.accepted_annual),
      pd.read_csv(a.accepted_window),a.group)
    a.out_dir.mkdir(parents=True,exist_ok=True)
    m.to_csv(a.out_dir/"paper_s_annual_min_throughput_selected_window_comparison.csv",index=False)
    t.to_csv(a.out_dir/"paper_s_annual_min_throughput_hourly_trace.csv.gz",
             index=False,compression="gzip")
    manifest={"status":"ORIGINAL_ARCHIVED_ANNUAL_MIN_THROUGHPUT_SOURCE_REPRODUCED",
      "source_group":a.group,"full_hour_rows":len(t),
      "selected_hour_window":SELECTED,"original_cost_cap_verified":True,
      "secondary_rule_is_not_an_investment_or_reliability_model":True}
    (a.out_dir/"paper_s_annual_min_throughput_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print(m.to_string(index=False));print(json.dumps(manifest,indent=2))
if __name__=="__main__":main()
