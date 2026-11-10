"""Certified physical charge/discharge exclusivity witness from archived full-hour LPs.

No new optimization or MILP: a *feasible transformation* of previously accepted
near-optimal LP schedules preserving all source balances, firm generation and SOC.

For eta2=0.90, t=min(c,d/eta2):
    r' = r + eta2*t; c' = c-t; d' = d-eta2*t
    f'=f; u'=u+(1-eta2)*t; s'=s.
Both renewable and load balance are preserved; the SOC recursion is unchanged.
Moreover r' <= min(A,L) because eta2*t <= c and eta2*t <= d.
The original positive renewable-use/charge cost is reduced by
5*(1-eta2)*t, so the candidate remains under the same cost ceiling.
The repaired max is a valid lower bound on the exclusive maximum, NOT the
computed exclusive optimum. The original relaxed maximum is an upper bound.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd

EFFICIENCY=.90
RENEWABLE_PRICE=5.
WINDOW=(4001,4168)
REQUIRED={"solution","local_hour_id","storage_charge_input_mwh",
          "storage_discharge_to_load_mwh","soc_end_mwh",
          "firm_generation_mwh","unused_renewable_mwh"}
SUMMARY={"solution","window_discharge_mwh","annual_discharge_mwh",
         "original_cost_usd","allowed_extra_cost_usd"}

def certify(traces,summaries,area):
    if not REQUIRED.issubset(traces) or not SUMMARY.issubset(summaries):
        raise ValueError("Missing accepted original source archived variables")
    if len(traces)!=26280 or len(summaries)!=3 or set(summaries.solution)!={"baseline","min","max"}:
        raise ValueError("Missing three complete accepted annual schedules")
    original=summaries.set_index("solution")
    report=[]
    extremes={}
    for solution in ("baseline","min","max"):
        x=traces[traces.solution==solution].sort_values("local_hour_id")
        if len(x)!=8760 or not np.array_equal(x.local_hour_id.to_numpy(),np.arange(1,8761)):
            raise ValueError("Unverified original source hour sequence")
        keys=["storage_charge_input_mwh","storage_discharge_to_load_mwh",
              "soc_end_mwh","firm_generation_mwh","unused_renewable_mwh"]
        if not np.isfinite(x[keys].to_numpy(dtype=float)).all() or (x[keys]<-1e-6).any().any():
            raise ValueError("Invalid original primal variables")
        c=x.storage_charge_input_mwh.to_numpy(dtype=float)
        d=x.storage_discharge_to_load_mwh.to_numpy(dtype=float)
        u=x.unused_renewable_mwh.to_numpy(dtype=float)
        t=np.minimum(c,d/EFFICIENCY)
        repaired_c=c-t
        repaired_d=d-EFFICIENCY*t
        repaired_u=u+(1-EFFICIENCY)*t
        direct_increase=EFFICIENCY*t
        if (np.minimum(repaired_c,repaired_d)>1e-6).any() or min(repaired_c.min(),repaired_d.min(),repaired_u.min())< -1e-6:
            raise ValueError("Repair leaves overlapping charge and discharge")
        if max(abs(-t+direct_increase+(1-EFFICIENCY)*t))>1e-5 or max(abs(-EFFICIENCY*t+direct_increase))>1e-5:
            raise ValueError("Original renewable/load balance change not zero")
        if np.max(np.abs(EFFICIENCY*c-d-(EFFICIENCY*repaired_c-repaired_d)))>1e-5:
            raise ValueError("Original SOC recursion changes")
        if (direct_increase>d+1e-6).any() or (direct_increase>c+1e-6).any():
            raise ValueError("Implied renewable-direct bound violated")
        within=x.local_hour_id.between(*WINDOW).to_numpy(dtype=bool)
        old_window=float(d[within].sum())
        new_window=float(repaired_d[within].sum())
        if not np.isclose(old_window,float(original.loc[solution,"window_discharge_mwh"]),atol=.02,rtol=1e-10):
            raise ValueError("Accepted original selected-window dispatch mismatch")
        if not np.isclose(float(d.sum()),float(original.loc[solution,"annual_discharge_mwh"]),atol=.02,rtol=1e-10):
            raise ValueError("Accepted original annual dispatch mismatch")
        saved=float(RENEWABLE_PRICE*(1-EFFICIENCY)*t.sum())
        report.append({"area":area,"solution":solution,
          "simultaneous_hours_before":int(((c>1e-6)&(d>1e-6)).sum()),
          "simultaneous_hours_after":0,"charge_removed_mwh":float(t.sum()),
          "discharge_removed_mwh":float((EFFICIENCY*t).sum()),
          "original_window_discharge_mwh":old_window,
          "repaired_window_discharge_mwh":new_window,
          "window_discharge_reduction_mwh":old_window-new_window,
          "original_cost_decrease_usd":saved,
          "unchanged_firm_and_soc":True,
          "original_cost_ceiling_preserved":True})
        extremes[solution]=(old_window,new_window)
    lower=extremes["min"][1]
    relaxed_upper=extremes["max"][0]
    feasible_upper=extremes["max"][1]
    if extremes["min"][0]-lower>1e-5 or feasible_upper<lower:
        raise ValueError("Original relaxed lower bound cannot anchor exclusive feasible range")
    witness={"area":area,
      "relaxed_window_min_mwh":lower,
      "relaxed_window_max_mwh":relaxed_upper,
      "exclusive_window_min_mwh":lower,
      "exclusive_window_max_lower_bound_mwh":feasible_upper,
      "exclusive_window_max_upper_bound_mwh":relaxed_upper,
      "relaxed_interval_width_mwh":relaxed_upper-lower,
      "exclusive_interval_width_at_least_mwh":feasible_upper-lower,
      "exclusive_interval_width_at_most_mwh":relaxed_upper-lower,
      "retained_relaxed_interval_width_at_least_percent":
          100*(feasible_upper-lower)/(relaxed_upper-lower)}
    return pd.DataFrame(report),witness

def main():
    p=argparse.ArgumentParser()
    for area in ("arizona","wyoming"):
        p.add_argument("--"+area+"-traces",required=True,type=Path)
        p.add_argument("--"+area+"-summary",required=True,type=Path)
    p.add_argument("--out-dir",required=True,type=Path)
    a=p.parse_args()
    results=[];bounds=[]
    for area in ("arizona","wyoming"):
        report,witness=certify(pd.read_csv(getattr(a,area+"_traces"),compression="infer"),
           pd.read_csv(getattr(a,area+"_summary")),area)
        results.append(report);bounds.append(witness)
    out=Path(a.out_dir);out.mkdir(parents=True,exist_ok=True)
    pd.concat(results,ignore_index=True).to_csv(out/"paper_s_six_algebraic_exclusive_repair_certificates.csv",index=False)
    pd.DataFrame(bounds).to_csv(out/"paper_s_exclusive_window_interval_feasible_bounds.csv",index=False)
    (out/"paper_s_exclusive_repair_manifest.json").write_text(json.dumps({
       "status":"ARCHIVED_ORIGINAL_DISPATCH_EXCLUSIVE_FEASIBILITY_WITNESS",
       "accepted_original_source_run":42851448558,
       "new_MILP_or_LP_solved":False,
       "exclusive_global_optimum_computed":False,
       "simultaneous_charge_discharge_after_repair":False,
       "original_SOC_and_firm_unchanged":True,
       "all_constraints_certified_by_algebraic_invariance_and_source_original_validation":True,
       "source_hours_not_UTC":True,"resource_supply_not_measured":True},indent=2)+"\n")
    print(pd.DataFrame(bounds).to_string(index=False))
if __name__=="__main__":main()
