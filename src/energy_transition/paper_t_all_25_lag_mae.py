"""All 825 source-derived nonwrapping lag MAEs for Paper T (11 states x 3 years x 25 lags).
No synthetic interpolation and no EFS physical-clock certification.
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
import h5py,numpy as np,pandas as pd
from energy_transition.efs2020_reeds2022_nonwrapping_lag import lag_overlap,LAGS,HOURS
from energy_transition.reeds2022_reference_hdf5_provenance import CHECKSUM,STATES,YEARS,verify_publisher_2012_clock
def compute(efs_csv,reeds_h5):
 with reeds_h5.open("rb") as stream:
  assert hashlib.file_digest(stream,"md5").hexdigest()==CHECKSUM,"ReEDS publisher MD5 mismatch"
 df=pd.read_csv(efs_csv,compression="infer")
 assert {"year","state","local_hour_id","load_mw"}<=set(df.columns)
 assert len(df)==33*HOURS and not df.duplicated(["year","state","local_hour_id"]).any()
 out=[]
 with h5py.File(reeds_h5,"r") as h5:
  for year in YEARS:
   group=h5[str(year)]
   verify_publisher_2012_clock(group["datetime"][:])
   for state in STATES:
    s=df.loc[(df.year==year)&(df.state==state)].sort_values("local_hour_id")
    assert len(s)==HOURS and np.array_equal(s.local_hour_id,np.arange(1,HOURS+1))
    a=s.load_mw.to_numpy(dtype=float);b=group[state][:]
    for lag in LAGS:
     metrics=lag_overlap(a,b,lag)
     out.append(dict(year=year,state=state,lag_h=lag,n_hours=metrics["compared_hours"],
      excluded_boundary_hours=metrics["excluded_boundary_hours"],mae_mw=metrics["mae_mw"],
      rmse_mw=metrics["rmse_mw"]))
 result=pd.DataFrame(out)
 assert len(result)==825 and not result.duplicated(["year","state","lag_h"]).any()
 return result
def validate(df,canonical):
 keys=["year","state"]; ref=pd.read_csv(canonical)
 assert len(ref)==33
 pairs=[]
 for (year,state),g in df.groupby(keys):
  sort=g.sort_values(["mae_mw","lag_h"])
  best=sort.iloc[0]; second=sort.iloc[1];zero=g[g.lag_h==0].iloc[0]
  orig=ref[(ref.year==year)&(ref.state==state)].iloc[0]
  fields=ref.columns.tolist()
  best_lag_col=next(c for c in ["best_nonwrap_offset","best_lag","best_offset"] if c in fields)
  best_mae_col=next(c for c in ["best_nonwrap_mae_mw","best_mae_mw"] if c in fields)
  runner_col=next(c for c in ["second_best_mae_mw","runnerup_mae_mw"] if c in fields)
  zero_col=next(c for c in ["zero_offset_mae_mw","unshifted_mae_mw"] if c in fields)
  assert int(best.lag_h)==int(orig[best_lag_col]),(year,state,"lag")
  assert abs(best.mae_mw-float(orig[best_mae_col]))<1e-5,(year,state,"best MAE")
  assert abs(second.mae_mw-float(orig[runner_col]))<1e-5,(year,state,"runner MAE")
  assert abs(zero.mae_mw-float(orig[zero_col]))<1e-5,(year,state,"zero MAE")
  pairs.append({"year":year,"state":state,"checked":True})
 return pairs
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--efs-hourly",required=True,type=Path)
 p.add_argument("--reeds-h5",required=True,type=Path)
 p.add_argument("--canonical",required=True,type=Path)
 p.add_argument("--outdir",required=True,type=Path)
 a=p.parse_args();a.outdir.mkdir(parents=True,exist_ok=True)
 table=compute(a.efs_hourly,a.reeds_h5)
 checks=validate(table,a.canonical)
 table.to_csv(a.outdir/"all_825_lag_mae.csv",index=False)
 (a.outdir/"validation.json").write_text(json.dumps({"source":"original archived EFS and publisher MD5 ReEDS 2022","points":825,
  "n_state_year":33,"lags":list(LAGS),"canonical_matches":len(checks),"physical_hour_join_admitted":False},indent=2)+"\n")
 print(f"Passed {len(checks)} canonical state-year checks; wrote {len(table)} original-data lag points.")
if __name__=="__main__":main()
