"""Independently certify Paper S published LP objective and energy identities.

Reads original archived 540-case result table, not an illustrative figure.
Code-audited objective coefficients are $5 per MWh for renewable direct
delivery AND battery charge input, and $90 per MWh firm delivery.
The assumed initial/terminal SOC is zero and round-trip efficiency 0.9.
This is a toy operational objective, NOT net economic storage value.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd

KEY=["planning_year","state","reeds_zone","synthetic_supply_shape","battery_duration_h"]
REQUIRED=set(KEY+["demand_mwh","renewable_available_mwh","renewable_direct_mwh",
"storage_charge_input_mwh","storage_discharge_to_load_mwh","firm_generation_mwh",
"unused_renewable_mwh","objective_illustrative_variable_usd","storage_terminal_soc_mwh",
"max_equality_residual_mwh","source_hours","solver_status"])

def audit(df):
    if not REQUIRED.issubset(df):raise ValueError("Missing LP case columns")
    if len(df)!=540 or df.duplicated(KEY).any():raise ValueError("Incomplete or duplicate 540-case population")
    if set(df.planning_year)!={2030,2040,2050}:raise ValueError("Unexpected source years")
    if set(df.battery_duration_h)!={0,4,8}:raise ValueError("Unexpected duration")
    if df[["state","reeds_zone"]].drop_duplicates().shape[0]!=20:raise ValueError("Expected 20 zones")
    if not df.source_hours.eq(8760).all() or not df.solver_status.eq("optimal").all():
        raise ValueError("Invalid original annual source hours or solver status")
    n=df[["renewable_direct_mwh","storage_charge_input_mwh","storage_discharge_to_load_mwh",
          "firm_generation_mwh","unused_renewable_mwh","objective_illustrative_variable_usd",
          "storage_terminal_soc_mwh","max_equality_residual_mwh"]].to_numpy(dtype=float)
    if not np.isfinite(n).all() or (n[:,:-2]<-1e-6).any():
        raise ValueError("Nonfinite or negative LP source metrics")
    cost=5.*(df.renewable_direct_mwh+df.storage_charge_input_mwh)+90.*df.firm_generation_mwh
    error=cost-df.objective_illustrative_variable_usd
    if not np.allclose(cost,df.objective_illustrative_variable_usd,rtol=1e-9,atol=.01):
        raise ValueError("Code-objective mismatch: published objective != 5*(r+c)+90*f")
    renewable_error=df.renewable_direct_mwh+df.storage_charge_input_mwh+df.unused_renewable_mwh-df.renewable_available_mwh
    demand_error=df.renewable_direct_mwh+df.storage_discharge_to_load_mwh+df.firm_generation_mwh-df.demand_mwh
    battery_error=.9*df.storage_charge_input_mwh-df.storage_discharge_to_load_mwh
    if max(np.abs(renewable_error).max(),np.abs(demand_error).max(),np.abs(battery_error).max())>.02:
        raise ValueError("Original result conservation or cyclic battery energy failed")
    if df.storage_terminal_soc_mwh.abs().max()>1e-5 or df.max_equality_residual_mwh.max()>1e-5:
        raise ValueError("Noncyclic SOC or LP primal equality failed")
    if not df.groupby("planning_year")[["state","reeds_zone"]].apply(lambda x:len(x.drop_duplicates())).eq(20).all():
        raise ValueError("Incomplete yearly zone coverage")
    return {
       "status":"PAPER_S_540_CASE_OBJECTIVE_AND_ENERGY_AUDIT_PASS",
       "cases":540,"source_ordinal_hours_per_case":8760,
       "objective_formula":"5*(renewable_direct_mwh + battery_charge_input_mwh) + 90*firm_generation_mwh",
       "note":"Battery charging and renewable direct energy each charged $5/MWh; toy marginal costs, no battery capex.",
       "battery_roundtrip_efficiency_assumed":0.9,
       "max_absolute_objective_usd_recalculation_error":float(np.abs(error).max()),
       "max_source_renewable_balance_mwh_error":float(np.abs(renewable_error).max()),
       "max_source_demand_balance_mwh_error":float(np.abs(demand_error).max()),
       "max_cyclic_battery_90pct_balance_mwh_error":float(np.abs(battery_error).max()),
       "max_terminal_soc_mwh":float(df.storage_terminal_soc_mwh.abs().max()),
       "all_source_years":[2030,2040,2050],
       "synthetic_renewable_shapes":True,
       "source_clock_UTC_certified":False,
       "real_western_grid_optimization":False
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--cases",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()
    result=audit(pd.read_csv(a.cases))
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))
if __name__=="__main__":main()
