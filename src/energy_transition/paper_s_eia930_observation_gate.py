"""Fail-closed admission gate for independent EIA-930 BA net-generation observations.

Inputs MUST be independently prepared and provenance-traceable. Never infer a
balancing authority is equivalent to an entire state or confuse EIA-930 MWh
net generation with instantaneous ReEDS resource capacity factors.

This module verifies ONLY source structure, clock, BA-to-state full-coverage
mapping claims, and observational evidence prerequisites. It cannot certify
an unverified crosswalk or measured power-plant resource-class distribution.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd

STATES=("AZ","CO","ID","WY")
TECHS=("wind","solar")
REQUIRED_OBS={
  "utc_hour_end","ba_code","fuel","net_generation_mwh",
  "source_url","source_release","observation_year",
}
REQUIRED_MAPPING={
  "ba_code","state","state_share_of_ba_generation",
  "geometry_basis","source_url","mapping_year",
  "all_ba_counties_accounted_for","state_share_includes_unmodeled_regions",
}
ALLOWED_GEOMETRY={"audited_county_ba_plant_mapping","audited_ba_state_geospatial_intersection"}


def validate_observations(frame):
    if not REQUIRED_OBS.issubset(frame.columns):
        raise ValueError(f"Missing EIA-930 observation fields: {sorted(REQUIRED_OBS-set(frame.columns))}")
    f=frame.copy()
    if f.empty:raise ValueError("No EIA-930 observation records")
    ts=pd.to_datetime(f.utc_hour_end,utc=True,errors="raise")
    if ts.isna().any() or ((ts.dt.minute!=0)|(ts.dt.second!=0)).any():
        raise ValueError("EIA-930 UTC hour-ending timestamps invalid")
    if not (ts==ts.dt.floor("h")).all():
        raise ValueError("EIA-930 source clock not an exact hour ending")
    f["utc_hour_end"]=ts
    if not f.fuel.isin(TECHS).all():
        raise ValueError("Fuel must be standardized wind or solar")
    if f.ba_code.isna().any() or f.ba_code.astype(str).str.strip().eq("").any():
        raise ValueError("Missing BA codes")
    f["net_generation_mwh"]=pd.to_numeric(f.net_generation_mwh,errors="raise")
    if not np.isfinite(f.net_generation_mwh).all():
        raise ValueError("Non-finite BA generation")
    # Negative net generation can occur operationally in source records; record but
    # do not silently clip or normalize negative values.
    if f.duplicated(["utc_hour_end","ba_code","fuel"]).any():
        raise ValueError("Duplicate BA/fuel/hour")
    if f.source_url.isna().any() or f.source_release.isna().any():
        raise ValueError("Missing EIA-930 traceability")
    if not f.source_url.astype(str).str.contains("eia.gov",regex=False).all():
        raise ValueError("Source URL is not an official EIA endpoint")
    if not np.array_equal(ts.dt.year.to_numpy(),pd.to_numeric(
            f.observation_year,errors="raise").to_numpy()):
        raise ValueError("Observation year disagrees with UTC hour label")
    return f


def validate_ba_crosswalk(frame,observations):
    if not REQUIRED_MAPPING.issubset(frame.columns):
        raise ValueError("Missing audited BA-to-state mapping fields")
    m=frame.copy()
    if m.empty or m.duplicated(["ba_code","state"]).any():
        raise ValueError("Missing/duplicated BA-to-state crosswalk records")
    if not m.state.isin(STATES).all():
        raise ValueError("BA crosswalk outside four modeled states")
    m["state_share_of_ba_generation"]=pd.to_numeric(
        m.state_share_of_ba_generation,errors="raise")
    if not np.isfinite(m.state_share_of_ba_generation).all() or (
        (m.state_share_of_ba_generation<0) |
        (m.state_share_of_ba_generation>1)).any():
        raise ValueError("Geographic allocation shares must be in [0,1]")
    if not m.geometry_basis.isin(ALLOWED_GEOMETRY).all():
        raise ValueError("Unverified BA=state assumption forbidden")
    if m.source_url.isna().any() or m.source_url.astype(str).str.strip().eq("").any():
        raise ValueError("BA-to-state mapping provenance missing")
    for flag in ("all_ba_counties_accounted_for","state_share_includes_unmodeled_regions"):
        if not m[flag].isin([True,False]).all():
            raise ValueError("Missing explicit BA mapping coverage flags")
    if not m.all_ba_counties_accounted_for.all():
        raise ValueError("Crosswalk fails full BA geography accounting")
    if m.state_share_includes_unmodeled_regions.any():
        raise ValueError("State allocation includes unsupported region")
    if not set(observations.ba_code).issubset(set(m.ba_code)):
        raise ValueError("Some observed BAs have no audited state mapping")
    if (m.groupby("ba_code").state_share_of_ba_generation.sum()>1+1e-8).any():
        raise ValueError("BA generation allocated to states more than once")
    if not set(STATES).issubset(set(m.loc[m.state_share_of_ba_generation>0,"state"])):
        raise ValueError("All modeled states require independently audited coverage")
    return m


def audit(obs,map_frame):
    data=validate_observations(obs)
    crosswalk=validate_ba_crosswalk(map_frame,data)
    by_ba=data.groupby(["ba_code","fuel"]).agg(
        source_records=("net_generation_mwh","size"),
        total_net_mwh=("net_generation_mwh","sum"),
        start_utc=("utc_hour_end","min"),end_utc=("utc_hour_end","max"),
        negative_observation_hours=("net_generation_mwh",lambda a:int((a<0).sum()))
    ).reset_index()
    coverage=crosswalk.groupby("state").agg(
        mapped_ba_count=("ba_code","nunique"),
        total_assigned_ba_fraction=("state_share_of_ba_generation","sum")
    ).reset_index()
    manifest={
        "status":"EIA930_STRUCTURE_AND_DECLARED_CROSSWALK_GATE_ONLY",
        "ba_fuel_groups":len(by_ba),"observed_rows":len(data),
        "mapped_states":len(coverage),
        "hour_end_utc_verified":True,
        "numeric_measured_cf_validation_performed":False,
        "observed_capacity_denominator_verified":False,
        "BA_to_state_mapping_factual_truth_externally_verified":False,
        "instantaneous_ReEDS_cf_to_hour_ended_EIA_measurement_admitted":False,
        "publication_validation_passed":False,
        "warnings":[
            "Crosswalk assertions can be wrong even with a valid schema",
            "EIA BA territories often span states; not equivalent to modeled state",
            "Need historical matching-year installed MW and wind/PV class distribution",
            "Demand end-hour and ReEDS instantaneous sample cannot be naively equated",
        ]}
    return by_ba,coverage,manifest


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--eia930-observed-hourly",type=Path,required=True)
    p.add_argument("--audited-ba-state-crosswalk",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    obs=pd.read_csv(a.eia930_observed_hourly)
    m=pd.read_csv(a.audited_ba_state_crosswalk)
    by_ba,coverage,manifest=audit(obs,m)
    a.out.mkdir(parents=True,exist_ok=True)
    by_ba.to_csv(a.out/"paper_s_EIA930_source_observation_coverage.csv",index=False)
    coverage.to_csv(a.out/"paper_s_EIA930_BA_state_crosswalk_coverage.csv",index=False)
    (a.out/"paper_s_EIA930_observation_admission_gate.json").write_text(
        json.dumps(manifest,indent=2)+"\n")
    print("PAPER_S_EIA930_SCHEMA_GATE_ONLY_NO_EMPIRICAL_VALIDATION",json.dumps(manifest))


if __name__=="__main__":
    main()
