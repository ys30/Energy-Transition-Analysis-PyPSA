"""Independent Idaho Subsector provenance and prospective sector-lag transfer test.

Uses exact original EFS 2020 CSV and publisher-MD5-verified ReEDS 2022 HDF5.
The 2030 Transportation +1 source-index perturbation is frozen *before*
the 2040 and 2050 evaluations. No timezone or physical-hour claims.
"""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
import numpy as np
import pandas as pd
from .efs_idaho_raw_sector_source_forensic import YEARS, HOURS, FIELDS, aggregate_idaho_sectors
from .reeds2022_reference_hdf5_provenance import CHECKSUM, verify_publisher_2012_clock

SECTORS=("Commercial","Industrial","Residential","Transportation")

def subsector_annual_source(csv_path:Path,chunk_size=200000):
    records=[];raw_rows=0
    for chunk in pd.read_csv(csv_path,usecols=FIELDS,chunksize=chunk_size):
        chosen=chunk.loc[(chunk.Electrification=="Reference") &
                         (chunk.TechnologyAdvancement=="Moderate") &
                         (chunk.Year.isin(YEARS)) & (chunk.State=="ID")].copy()
        if chosen.empty:continue
        if chosen[FIELDS].isna().any().any():raise ValueError("Null original source labels or MW")
        if not set(chosen.Sector).issubset(SECTORS):raise ValueError("Unknown original EFS sector")
        if not chosen.LocalHourID.between(1,HOURS).all():raise ValueError("Bad original EFS hour")
        original_mw=pd.to_numeric(chosen.LoadMW,errors="raise").to_numpy(dtype=float)
        if not np.isfinite(original_mw).all() or (original_mw<0).any():raise ValueError("Invalid source MW")
        raw_rows+=len(chosen)
        pieces=chosen.groupby(["Year","Sector","Subsector"],as_index=False,sort=False).agg(
            original_load_mwh=("LoadMW","sum"),original_source_rows=("LoadMW","size"))
        records.append(pieces)
    if not records:raise ValueError("No original Idaho source subsectors")
    summary=pd.concat(records,ignore_index=True).groupby(["Year","Sector","Subsector"],as_index=False).agg(
        original_load_mwh=("original_load_mwh","sum"),original_source_rows=("original_source_rows","sum"))
    if int(summary.original_source_rows.sum())!=raw_rows:raise ValueError("Source record accounting error")
    if set(summary.Year)!=set(YEARS):raise ValueError("Incomplete years")
    sum_by_year=summary.groupby("Year").original_load_mwh.sum()
    summary["original_year_load_share"]=summary.apply(
        lambda x:x.original_load_mwh/sum_by_year.loc[x.Year],axis=1)
    summary=summary.sort_values(["Year","Sector","Subsector"]).reset_index(drop=True)
    return summary,{"source_rows_selected":raw_rows,"source_unique_subsector_combinations":int(summary[["Sector","Subsector"]].drop_duplicates().shape[0])}

def frozen_shift_transfer(sector_year,original_hourly,reeds_hourly,year):
    sec={}
    for s in SECTORS:
        p=sector_year.loc[(sector_year.Year==year)&(sector_year.Sector==s)].sort_values("LocalHourID")
        if not np.array_equal(p.LocalHourID.to_numpy(),np.arange(1,HOURS+1)):
            raise ValueError(f"Missing EFS original source hours {year}/{s}")
        sec[s]=p.LoadMW.to_numpy(dtype=float)
    original=np.asarray(original_hourly,dtype=float)
    reference=np.asarray(reeds_hourly,dtype=float)
    if original.shape!=(HOURS,) or reference.shape!=(HOURS,):raise ValueError("Bad state vectors")
    if not np.allclose(sum(sec.values()),original,rtol=1e-10,atol=.02):
        raise ValueError("Original 4-sector sum does not match archived state source")
    # -2 HDF5 index is previously identified on different original source data.
    # 1..8756 gives room for the fixed 2030 Transportation +1 perturbation.
    ids=np.arange(1,HOURS-3)
    target=reference[ids+2]
    baseline=sum(series[ids] for series in sec.values())
    frozen=baseline-sec["Transportation"][ids]+sec["Transportation"][ids-1]
    holdout=ids>=4380
    baseline_errors=np.abs(baseline[holdout]-target[holdout])
    frozen_errors=np.abs(frozen[holdout]-target[holdout])
    # Also show all common interior hours. No train re-selection in 2040/2050.
    return {
        "planning_year":int(year),
        "heldout_hours":int(holdout.sum()),
        "baseline_heldout_mae_mw":float(baseline_errors.mean()),
        "fixed_2030_transport_plus1_heldout_mae_mw":float(frozen_errors.mean()),
        "heldout_improvement_mw":float(baseline_errors.mean()-frozen_errors.mean()),
        "frozen_2030_sector_candidate":"Commercial:0|Industrial:0|Residential:0|Transportation:+1",
        "fit_selection_repeated_on_this_year":False,
        "candidate_shift_physical_timezone_verified":False,
    }

def audit(original_csv,previous_state_csv,reeds_h5):
    import h5py
    with reeds_h5.open("rb") as f: md5=hashlib.file_digest(f,"md5").hexdigest()
    if md5!=CHECKSUM:raise ValueError("Official ReEDS2022 HDF5 checksum mismatch")
    subsectors,details=subsector_annual_source(original_csv)
    sectors,sector_meta=aggregate_idaho_sectors(original_csv)
    if details["source_rows_selected"]!=sector_meta["selected_original_source_rows"]:
        raise ValueError("Source provenance counts disagree")
    archived=pd.read_csv(previous_state_csv,compression="infer")
    results=[]
    with h5py.File(reeds_h5,"r") as f:
        for year in YEARS:
            verify_publisher_2012_clock(f[str(year)]["datetime"][:])
            a=archived.loc[(archived.year==year)&(archived.state=="ID")].sort_values("local_hour_id")
            if not np.array_equal(a.local_hour_id.to_numpy(),np.arange(1,HOURS+1)):
                raise ValueError("Original state hour archive incomplete")
            expected=float(a.load_mw.sum())
            reported=float(subsectors.loc[subsectors.Year==year,"original_load_mwh"].sum())
            if not np.isclose(expected,reported,rtol=1e-11,atol=.1):
                raise ValueError("Original subsector total does not reconcile archived state year")
            results.append(frozen_shift_transfer(sectors,a.load_mw.to_numpy(),f[str(year)]["ID"][:],year))
    return subsectors,pd.DataFrame(results),{
        "status":"IDAHO_SOURCE_SUBSECTOR_AND_FROZEN_SHIFT_TRANSFER_AUDITED",
        "original_source_csv_sha256":hashlib.sha256(original_csv.read_bytes()).hexdigest(),
        "original_state_archive_sha256":hashlib.sha256(previous_state_csv.read_bytes()).hexdigest(),
        "official_reeds2022_md5":md5,**details,
        "subsector_energy_reconciled_2030_2040_2050":True,
        "source_hourly_sector_reconciled_all_years":True,
        "2012_reeds_source_clock_used_as_reference_only":True,
        "authoritative_efs2020_clock_verified":False,
        "subsector_geographic_timezone_identified":False,
        "cross_source_future_wind_solar_join_allowed":False,
        "real_Western_powerflow_admitted":False,
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--original-efs",required=True,type=Path)
    ap.add_argument("--state-hour",required=True,type=Path)
    ap.add_argument("--reeds-h5",required=True,type=Path)
    ap.add_argument("--out-dir",required=True,type=Path)
    args=ap.parse_args()
    subs,transfer,meta=audit(args.original_efs,args.state_hour,args.reeds_h5)
    args.out_dir.mkdir(parents=True,exist_ok=True)
    subs.to_csv(args.out_dir/"idaho_source_subsector_annual_energy.csv",index=False)
    transfer.to_csv(args.out_dir/"idaho_frozen_2030_transport_shift_crossyear.csv",index=False)
    (args.out_dir/"idaho_subsector_source_provenance.json").write_text(json.dumps(meta,indent=2)+"\n")
    print("SOURCE_SUBSECTOR_SUMMARY")
    print(subs.to_string(index=False))
    print("FROZEN_2030_TRANSPORT_SHIFT")
    print(transfer.to_string(index=False))
    print(json.dumps(meta,indent=2))
if __name__=="__main__":main()
