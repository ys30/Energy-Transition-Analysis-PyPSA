"""State-level validation of archived 55-source-bus EFS exposure screen.

Works on immutable artifacts from successful source-only CI. Produces a
concentration table, never an empirical allocation, outage or OPF result.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd

YEARS={2030,2040,2050}

def summarize(rows:pd.DataFrame):
    required={"bus_id","year","exported_state_code","source_v_nom_kv","source_Pd",
              "source_LAF_state","efs_state_annual_mwh",
              "hypothetical_exported_state_laf_annual_mwh"}
    if not required.issubset(rows):raise ValueError("Missing archived source screen fields")
    d=rows.copy()
    d.bus_id=d.bus_id.astype("string")
    d.year=pd.to_numeric(d.year,errors="raise").astype(int)
    if set(d.year)!=YEARS or d.duplicated(["year","bus_id"]).any():
        raise ValueError("Source bus-year keys missing or repeated")
    for field in ["source_Pd","source_LAF_state","efs_state_annual_mwh",
                  "hypothetical_exported_state_laf_annual_mwh"]:
        d[field]=pd.to_numeric(d[field],errors="coerce")
    if not np.isfinite(d[["source_Pd","source_LAF_state","efs_state_annual_mwh",
                           "hypothetical_exported_state_laf_annual_mwh"]].to_numpy(dtype=float)).all():
        raise ValueError("Invalid numeric evidence")
    if (d.source_Pd<=0).any() or (d.source_LAF_state<0).any() or (d.source_LAF_state>1).any():
        raise ValueError("Invalid source bus weight or original Pd")
    identity=d.groupby("bus_id").agg(
        source_state_count=("exported_state_code","nunique"),
        source_pd_count=("source_Pd","nunique"),
        laf_count=("source_LAF_state","nunique"),
        years=("year","nunique"))
    if (identity.source_state_count!=1).any() or (identity.source_pd_count!=1).any() or (identity.laf_count!=1).any() or (identity.years!=3).any():
        raise ValueError("Original bus identity, weight or year coverage inconsistent")
    if not np.allclose(d.hypothetical_exported_state_laf_annual_mwh,
                       d.source_LAF_state*d.efs_state_annual_mwh,atol=0.01,rtol=1e-10):
        raise ValueError("Screened source-LAF exposure not numerically reproducible")
    state_source=d.groupby(["year","exported_state_code"]).efs_state_annual_mwh.nunique()
    if (state_source!=1).any():raise ValueError("Inconsistent EFS state source within a year")
    grouped=d.groupby(["year","exported_state_code"],as_index=False).agg(
        candidate_bus_count=("bus_id","nunique"),
        source_bus_pd_sum_mw=("source_Pd","sum"),
        source_laf_sum=("source_LAF_state","sum"),
        source_state_annual_efs_mwh=("efs_state_annual_mwh","first"),
        candidate_annual_exposure_mwh=("hypothetical_exported_state_laf_annual_mwh","sum"))
    grouped["candidate_share_of_source_state_efs"]=grouped.candidate_annual_exposure_mwh/grouped.source_state_annual_efs_mwh
    if grouped.candidate_share_of_source_state_efs.gt(1.000001).any():
        raise ValueError("Cannot attribute >100% of source-state annual demand")
    annual=grouped.groupby("year",as_index=False).candidate_annual_exposure_mwh.sum()
    grouped=grouped.merge(annual.rename(columns={"candidate_annual_exposure_mwh":"screened_year_total_mwh"}),on="year")
    grouped["contribution_to_screened_year_total"]=grouped.candidate_annual_exposure_mwh/grouped.screened_year_total_mwh
    grouped.sort_values(["year","candidate_annual_exposure_mwh"],
                        ascending=[True,False],inplace=True)
    top=[]
    for year,frame in grouped.groupby("year"):
        top.append({
            "year":int(year),
            "source_EFS_covered_state_count":int(len(frame)),
            "candidate_53_bus_count":int(frame.candidate_bus_count.sum()),
            "hypothetical_annual_exposure_mwh":float(frame.candidate_annual_exposure_mwh.sum()),
            "largest_source_state":str(frame.iloc[0].exported_state_code),
            "largest_source_state_exposure_mwh":float(frame.iloc[0].candidate_annual_exposure_mwh),
            "top_three_states_fraction_of_screened_total":float(frame.head(3).candidate_annual_exposure_mwh.sum()/frame.candidate_annual_exposure_mwh.sum()),
        })
    result={
        "source_screen_years":sorted(YEARS),
        "screened_unique_source_bus_count":int(d.bus_id.nunique()),
        "screened_source_bus_year_rows":int(len(d)),
        "screened_source_bus_pd_mw":float(d.drop_duplicates("bus_id").source_Pd.sum()),
        "screened_exported_state_codes":sorted(d.exported_state_code.unique().tolist()),
        "annual_state_concentration":top,
        "actual_electrical_source_bus_connections_confirmed":False,
        "dropped_upstream_full_state_denominators_recovered":False,
        "physically_correct_bus_level_efs_allocations_admitted":False,
        "2024_plant_POI_crosswalk_approved":False,
        "empirical_OPF_solved":False,
        "note":"State aggregation of *hypothetical exported-state* LAF exposure, not actual served/unserved MWh or model-solving result.",
    }
    return grouped,result

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--screen",type=Path,required=True)
    p.add_argument("--outdir",type=Path,required=True)
    a=p.parse_args()
    table,report=summarize(pd.read_csv(a.screen,dtype={"bus_id":"string","exported_state_code":"string"}))
    a.outdir.mkdir(parents=True,exist_ok=True)
    table.to_csv(a.outdir/"55bus_candidate_exposure_by_state_year.csv",index=False)
    (a.outdir/"55bus_candidate_exposure_state_concentration.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))
    print(table.to_string(index=False))
if __name__=="__main__":main()
