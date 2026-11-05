"""Audit original EFS Idaho sector/subsector hour series and held-out lag hypotheses.

This is a SOURCE-INDEX regression/diagnostic, not physical timezone attribution.
Never claim a fitted sector-lag is an actual sector-specific publisher clock.
"""
from __future__ import annotations
import argparse, hashlib, itertools, json
from pathlib import Path
import numpy as np
import pandas as pd

from .reeds2022_reference_hdf5_provenance import CHECKSUM, verify_publisher_2012_clock

YEARS=(2030,2040,2050)
HOURS=8760
SCENARIO={"Electrification":"Reference","TechnologyAdvancement":"Moderate"}
FIELDS=["Electrification","TechnologyAdvancement","Year","State","LocalHourID","Sector","Subsector","LoadMW"]
SHIFT=(-1,0,1)

def aggregate_idaho_sectors(source_csv:Path,chunksize=180000):
    pieces=[];count=0;names=set()
    for block in pd.read_csv(source_csv,usecols=FIELDS,chunksize=chunksize):
        part=block[(block.Electrification=="Reference")&(block.TechnologyAdvancement=="Moderate")&
                   (block.Year.isin(YEARS))&(block.State=="ID")].copy()
        if part.empty:continue
        if part[FIELDS].isna().any().any():
            raise ValueError("Incomplete Idaho EFS source fields")
        mw=pd.to_numeric(part.LoadMW,errors="raise").to_numpy(dtype=float)
        if not np.isfinite(mw).all() or (mw<0).any():
            raise ValueError("Bad Idaho source MW")
        if not part.LocalHourID.between(1,HOURS).all():
            raise ValueError("Bad LocalHourID")
        count+=len(part)
        names.update(map(str,part.Sector.unique()))
        pieces.append(part.groupby(["Year","Sector","LocalHourID"],as_index=False,sort=False).LoadMW.sum())
    if not pieces:raise ValueError("No original Idaho source rows")
    grouped=pd.concat(pieces,ignore_index=True).groupby(["Year","Sector","LocalHourID"],as_index=False).LoadMW.sum()
    sectors=sorted(names)
    if len(sectors)<2 or len(sectors)>10:raise ValueError("Unexpected original sector count")
    expected=len(YEARS)*HOURS*len(sectors)
    if len(grouped)!=expected or grouped.duplicated(["Year","Sector","LocalHourID"]).any():
        raise ValueError("Incomplete original Idaho source sector/hour coverage")
    for _,g in grouped.groupby(["Year","Sector"]):
        if not np.array_equal(np.sort(g.LocalHourID.to_numpy()),np.arange(1,HOURS+1)):
            raise ValueError("Sector-hour source gap")
    return grouped,{"selected_original_source_rows":count,"sectors":sectors,"grouped_sector_hour_rows":len(grouped)}


def one_year(sector_source, original_hourly, published,year):
    sectors=sorted(sector_source.Sector.unique())
    aligned=[]
    for sector in sectors:
        sub=sector_source[(sector_source.Year==year)&(sector_source.Sector==sector)].sort_values("LocalHourID")
        aligned.append(sub.LoadMW.to_numpy(dtype=float))
    s=np.stack(aligned)
    a=np.asarray(original_hourly,dtype=float)
    b=np.asarray(published,dtype=float)
    if s.shape!=(len(sectors),HOURS) or a.shape!=(HOURS,) or b.shape!=(HOURS,):
        raise ValueError("Bad sector or state source dimension")
    if not np.allclose(s.sum(axis=0),a,rtol=1e-10,atol=.02):
        raise ValueError("Source sector sum does not reproduce archived Idaho original state hourly")
    # Source roll of ReEDS -2; exclude last two hours to avoid wrap.
    idx=np.arange(HOURS-2)
    target=np.roll(b,-2)[idx]
    baseline=s[:,idx].sum(axis=0)
    baseline_error=np.abs(baseline-target)
    # Falsification-only sector source shifts; edge exclusion to avoid any wrap.
    # Use interior indices where all +/-1-sector perturbations are genuine.
    interior=np.arange(1,HOURS-3)
    y=target[interior]
    matrices={off:np.stack([series[interior-off] for series in s]) for off in SHIFT}
    # First 6 months train and second 6 months holdout, same preselected shifts.
    train=interior<4380
    test=~train
    candidates=[]
    for shifts in itertools.product(SHIFT,repeat=len(sectors)):
        pred=sum(matrices[k][i] for i,k in enumerate(shifts))
        tr=float(np.mean(np.abs(pred[train]-y[train])))
        te=float(np.mean(np.abs(pred[test]-y[test])))
        candidates.append((tr,te,shifts))
    if not candidates:raise ValueError("No candidate sector shift")
    candidates.sort(key=lambda v:(v[0],v[2]))
    best=candidates[0]
    no_shift=np.abs(baseline[interior]-y)
    original_year_mwh=float(a.sum())
    return {
        "year":int(year),"state":"ID","sector_names":"|".join(sectors),
        "source_original_state_mwh":original_year_mwh,
        "source_sector_sum_mwh":float(s.sum()),
        "exact_state_reconciliation":True,
        "baseline_best_state_lag_h":-2,
        "baseline_nonwrap_full_mae_mw":float(baseline_error.mean()),
        "baseline_interior_train_mae_mw":float(no_shift[train].mean()),
        "baseline_interior_test_mae_mw":float(no_shift[test].mean()),
        "training_selected_sector_shifts":"|".join(str(k) for k in best[2]),
        "training_selected_baseline_no_shifts":bool(all(k==0 for k in best[2])),
        "training_selected_sector_shift_train_mae_mw":best[0],
        "training_selected_sector_shift_test_mae_mw":best[1],
        "heldout_mae_reduction_vs_unshifted_sectors_mw":float(no_shift[test].mean()-best[1]),
        "best_candidate_in_sample_better_or_equal_baseline":bool(best[0]<=float(no_shift[train].mean())+1e-8),
        "exhaustive_sector_shift_candidates":len(candidates),
        "source_sector_shifts_have_physical_timezone_credibility":False,
        "upstream_EFS2020_sector_timezone_definition_certified":False,
    }

def audit(original_csv,archived_state_csv,reeds_h5):
    import h5py  # optional HDF5 reader only for real-source audit
    with reeds_h5.open("rb") as fd:
        digest=hashlib.file_digest(fd,"md5").hexdigest()
    if digest!=CHECKSUM:raise ValueError("Official ReEDS2022 HDF5 MD5 mismatch")
    sectors,source_report=aggregate_idaho_sectors(original_csv)
    archive=pd.read_csv(archived_state_csv,compression="infer")
    rows=[]
    with h5py.File(reeds_h5,"r") as hf:
        for y in YEARS:
            verify_publisher_2012_clock(hf[str(y)]["datetime"][:])
            state=archive[(archive.year==y)&(archive.state=="ID")].sort_values("local_hour_id")
            if not np.array_equal(state.local_hour_id.to_numpy(),np.arange(1,HOURS+1)):
                raise ValueError("Incomplete original EFS state archived hours")
            rows.append(one_year(sectors,state.load_mw.to_numpy(),hf[str(y)]["ID"][:],y))
    return pd.DataFrame(rows),{
        "status":"IDAHO_RAW_EFS_SECTOR_SOURCE_RECONCILED_AND_HYPOTHESIS_TESTED",
        "source_file_sha256":hashlib.sha256(original_csv.read_bytes()).hexdigest(),
        "published_2022_hdf5_md5":digest,
        "original_state_hour_archive_sha256":hashlib.sha256(archived_state_csv.read_bytes()).hexdigest(),
        "sectors":source_report["sectors"],
        "source_rows_selected":source_report["selected_original_source_rows"],
        "source_sector_hour_records":source_report["grouped_sector_hour_rows"],
        "source_clock_corrected_or_synchronized":False,
        "physical_timezone_sector_membership_identified":False,
        "future_wind_solar_join_admitted":False,
        "note":"Sector-shift train/holdout exercise is an unconstrained source-index falsification only, not a valid source-time transformation."
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--original-efs",required=True,type=Path)
    p.add_argument("--archived-hourly",required=True,type=Path)
    p.add_argument("--reeds-h5",required=True,type=Path)
    p.add_argument("--out-dir",required=True,type=Path)
    a=p.parse_args()
    frame,meta=audit(a.original_efs,a.archived_hourly,a.reeds_h5)
    a.out_dir.mkdir(parents=True,exist_ok=True)
    frame.to_csv(a.out_dir/"idaho_raw_sector_shift_holdout.csv",index=False)
    (a.out_dir/"idaho_source_sector_provenance.json").write_text(json.dumps(meta,indent=2)+"\n")
    print(frame.to_string(index=False))
    print(json.dumps(meta,indent=2))
if __name__=="__main__":main()
