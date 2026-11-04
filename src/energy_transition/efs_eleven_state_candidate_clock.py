"""Read-only combined 11-state EFS zonal candidate and mixed-clock sensitivity.

Inputs are archived actual EFS state-hour loads, independently verified seven
state zonal pilot, and a four-state *numerical candidate* LAF report. This is
not verified geography, actual UTC, or a solved PyPSA network.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from energy_transition.efs_fixed_clock_sensitivity import fixed_utc_ordinal

YEARS=(2030,2040,2050)
HOURS=8760
STATE_NAMES={
    "AZ":"Arizona","CA":"California","CO":"Colorado","ID":"Idaho",
    "MT":"Montana","NM":"New Mexico","NV":"Nevada","OR":"Oregon",
    "UT":"Utah","WA":"Washington","WY":"Wyoming",
}
EXISTING=set(("AZ","CO","ID","MT","NM","UT","WY"))
CANDIDATE=set(("CA","NV","OR","WA"))
SHIFTS={s:(8 if s in ("CA","NV","OR","WA") else 7) for s in STATE_NAMES}


def _check_hours(x:pd.DataFrame, keys:list[str], hours:int)->None:
    expected=np.arange(1,hours+1,dtype=np.int64)
    if x.duplicated(keys+["local_hour_id"]).any():
        raise ValueError(f"Duplicate ordinal key: {keys}")
    for group,g in x.groupby(keys,sort=True):
        try:
            vals=pd.to_numeric(g.local_hour_id,errors="raise").to_numpy(dtype=np.int64)
        except (TypeError,ValueError) as exc:
            raise ValueError(f"Invalid local-hour ordinal in {group}") from exc
        if not np.array_equal(np.sort(vals),expected):
            raise ValueError(f"Missing/noncontiguous local-hour ordinals: {group}")


def analyze_combined_source(
    source:pd.DataFrame, seven:pd.DataFrame, candidate:dict, *, hours:int=HOURS,
)->dict:
    source_columns={"year","state","local_hour_id","load_mw"}
    seven_columns={"year","state","local_hour_id","reeds_zone","allocated_mw"}
    if set(source.columns)!=source_columns or set(seven.columns)!=seven_columns:
        raise ValueError("Unexpected archived source/seven-state zonal schema")
    if not candidate.get("candidate_only") or candidate.get("EFS_demand_admitted") is not False:
        raise ValueError("Missing candidate-only admission guard")
    if candidate.get("source_geography_independently_validated") is not False:
        raise ValueError("Unexpected geographic verification claim")
    if candidate.get("offshore_auxiliaries_excluded_count")!=157:
        raise ValueError("Pinned 157-offshore-source audit is required")
    if candidate.get("offshore_auxiliaries_LAF_modified") is not False:
        raise ValueError("Archived source coefficients cannot be modified")
    src=source.copy()
    seven=seven.copy()
    src["year"]=pd.to_numeric(src.year,errors="raise").astype(int)
    seven["year"]=pd.to_numeric(seven.year,errors="raise").astype(int)
    if set(src.year)!=set(YEARS) or set(seven.year)!=set(YEARS):
        raise ValueError("Expected all three planning years")
    if set(src.state)!=set(STATE_NAMES):
        raise ValueError("Original EFS input must include exactly 11 source state codes")
    if set(seven.state)!=set(STATE_NAMES[s] for s in EXISTING):
        raise ValueError("Archive must include exactly the established seven states")
    if src.isna().any().any() or seven.isna().any().any():
        raise ValueError("Null EFS source or existing seven-state allocation")
    src["load_mw"]=pd.to_numeric(src.load_mw,errors="raise")
    seven["allocated_mw"]=pd.to_numeric(seven.allocated_mw,errors="raise")
    for frame,col in ((src,"load_mw"),(seven,"allocated_mw")):
        v=frame[col].to_numpy(dtype=float)
        if not np.isfinite(v).all() or (v<0).any():
            raise ValueError("Invalid source or allocated MW")
    _check_hours(src,["year","state"],hours)
    _check_hours(seven,["year","state","reeds_zone"],hours)
    if not all(set(g.reeds_zone)==set(seven[seven.state.eq(state)].reeds_zone)
               for (year,state),g in seven.groupby(["year","state"])):
        raise ValueError("Existing seven-state zone inventory not stable")
    seven["state"]=seven.state.map({v:k for k,v in STATE_NAMES.items()})
    keys=["year","state","local_hour_id"]
    # Seven-state archive must have the same local-hour source keys and must
    # preserve one constant allocated share per state/year (partial-Western
    # states can have totals <1; NEVER renormalize those to 1).
    seven_hour=seven.groupby(keys,sort=True).allocated_mw.sum()
    seven_src=src[src.state.isin(EXISTING)].set_index(keys).load_mw.sort_index()
    if not seven_src.index.equals(seven_hour.index):
        raise ValueError("Original seven-state hour labels do not match source")
    seven_shares={}
    for (year,state),group in seven_hour.groupby(level=["year","state"]):
        y=seven_src.loc[(year,state)].to_numpy()
        z=group.to_numpy()
        if not (y>0).any(): raise ValueError("Zero-only archived source series")
        factor=float(np.median(z[y>0]/y[y>0]))
        if factor<=0 or factor>1+1e-6:
            raise ValueError(f"Invalid archived Western partial factor {year}/{state}")
        if not np.allclose(z,factor*y,rtol=1e-9,atol=1e-5):
            raise ValueError(f"Seven-state archived ratio changed: {year}/{state}")
        seven_shares[f"{year}/{state}"]=factor
    weights=pd.DataFrame(candidate.get("source_to_reeds_zone_candidate_weights",[]))
    if set(weights.columns)!={"source_state","reeds_zone","weight"} or weights.empty:
        raise ValueError("Missing four-state source-weight table")
    if weights.isna().any().any() or set(weights.source_state)!=CANDIDATE:
        raise ValueError("Four-state weight source coverage mismatch")
    if weights.duplicated(["source_state","reeds_zone"]).any():
        raise ValueError("Duplicate four-state source/zone weight")
    weights["weight"]=pd.to_numeric(weights.weight,errors="raise")
    if not np.isfinite(weights.weight.to_numpy()).all() or (weights.weight<=0).any():
        raise ValueError("Invalid four-state source weights")
    totals=weights.groupby("source_state").weight.sum()
    if not np.allclose(totals.loc[sorted(CANDIDATE)].to_numpy(),1,rtol=0,atol=1e-9):
        raise ValueError("Candidate four-state weights do not conserve source mass")
    supplied=candidate.get("source_state_weight_totals",{})
    if set(supplied)!=CANDIDATE or not all(
        abs(float(supplied[s])-float(totals[s]))<1e-9 for s in CANDIDATE
    ):
        raise ValueError("Candidate weight report totals disagree with zonal table")
    four=src[src.state.isin(CANDIDATE)].merge(
        weights,left_on="state",right_on="source_state",how="left",validate="many_to_many"
    )
    if four.weight.isna().any():
        raise ValueError("Unmapped candidate source state")
    four["allocated_mw"]=four.load_mw*four.weight
    allocated=pd.concat([
        seven[keys+["reeds_zone","allocated_mw"]],
        four[keys+["reeds_zone","allocated_mw"]],
    ],ignore_index=True)
    four_check=four.groupby(keys).allocated_mw.sum()
    four_source=src[src.state.isin(CANDIDATE)].set_index(keys).load_mw.sort_index()
    if not four_source.index.equals(four_check.index) or not np.allclose(
        four_source.to_numpy(),four_check.to_numpy(),rtol=1e-11,atol=1e-5
    ):
        raise ValueError("Four-state state-hour candidate MW conservation failure")
    allocated["compat_hour"]=np.empty(len(allocated),dtype=np.int64)
    for state,shift in SHIFTS.items():
        subset=allocated.state.eq(state)
        allocated.loc[subset,"compat_hour"]=fixed_utc_ordinal(
            allocated.loc[subset,"local_hour_id"].to_numpy(),shift)
    annual=[]
    for year,sub in allocated.groupby("year",sort=True):
        local=sub.groupby("local_hour_id").allocated_mw.sum().reindex(range(1,hours+1))
        compat=sub.groupby("compat_hour").allocated_mw.sum().reindex(range(1,hours+1))
        if local.isna().any() or compat.isna().any():
            raise ValueError("Combined 11-state hourly coverage incomplete")
        annual.append({
            "year":int(year),
            "all_11_state_local_index_peak_mw":float(local.max()),
            "all_11_state_compat_shift_peak_mw":float(compat.max()),
            "mixed_offset_peak_delta_mw":float(compat.max()-local.max()),
            "all_11_state_local_index_peak_ordinal":int(local.idxmax()),
            "all_11_state_compat_shift_peak_ordinal":int(compat.idxmax()),
            "annual_allocated_mwh":float(local.sum()),
            "annual_allocated_compat_mwh":float(compat.sum()),
            "annual_four_candidate_source_mwh":float(
                four.loc[four.year.eq(year),"load_mw"].sum()/len(weights) if False else
                src.loc[src.year.eq(year)&src.state.isin(CANDIDATE),"load_mw"].sum()),
        })
        if not np.isclose(local.sum(),compat.sum(),rtol=1e-12,atol=1e-5):
            raise ValueError("Annual total changed under fixed-state offset")
    return {
        "source_state_count":11,
        "candidate_new_state_count":4,
        "unchanged_existing_state_count":7,
        "source_state_hour_count":int(len(src)),
        "combined_zonal_state_hour_rows":int(len(allocated)),
        "candidate_weights_source_only":True,
        "archived_seven_state_values_unchanged":True,
        "existing_partial_interconnect_factors":seven_shares,
        "all_four_candidate_source_masses_equal_one":True,
        "candidate_state_source_to_zone_conservation_verified":True,
        "upstream_fixed_offset_only":True,
        "source_state_offsets_hours":SHIFTS,
        "planning_year_results":annual,
        "independently_verified_original_full_state_geography":False,
        "source_EFS_localhour_to_actual_UTC_verified":False,
        "wind_solar_renewable_alignment_verified":False,
        "empirically_admitted_11_state_load":False,
        "full_western_calibrated_OPF_solved":False,
        "warning":"Mixed offset peak sensitivity is candidate-only. Do not treat it as calibrated Western UTC peak demand or dispatch.",
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",required=True,type=Path)
    p.add_argument("--seven",required=True,type=Path)
    p.add_argument("--four-candidate",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()
    report=analyze_combined_source(
        pd.read_csv(a.source,compression="infer"),
        pd.read_csv(a.seven,compression="infer"),
        json.loads(a.four_candidate.read_text(encoding="utf-8")),
    )
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in report.items()
                      if k!="existing_partial_interconnect_factors"},indent=2))

if __name__=="__main__":
    main()
