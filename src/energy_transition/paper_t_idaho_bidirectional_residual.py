"""Paper T: source-index-only Idaho bidirectional mixture and residual structure."""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
import numpy as np,pandas as pd
from scipy.optimize import minimize
from .reeds2022_reference_hdf5_provenance import CHECKSUM,YEARS,verify_publisher_2012_clock
N=8760
def align(y,x,offsets):
    low=max((0,*offsets));high=min((N,*(N+k for k in offsets)))
    i=np.arange(low,high)
    return i,y[i],np.column_stack([x[i-k] for k in offsets])
def weights(y,x):
    n=x.shape[1]
    if n==1:return np.ones(1)
    # Center to avoid large signal magnitude in constrained optimizer.
    z=x-x[:,-1,None];a=z[:,:-1];b=y-x[:,-1]
    result=minimize(lambda w:np.mean((b-a@w)**2),np.full(n-1,1/n),
        method="SLSQP",bounds=[(0,1)]*(n-1),
        constraints=[{"type":"ineq","fun":lambda w:1-w.sum()}],
        options={"maxiter":600,"ftol":1e-9})
    if not result.success:raise ValueError("Constrained fit failed: "+result.message)
    return np.r_[result.x,1-result.x.sum()]
def metrics(y,p):
    r=y-p;return dict(mae_mw=float(abs(r).mean()),rmse_mw=float(np.sqrt(np.mean(r*r))),
      over_1mw=int((abs(r)>1).sum()),n=int(len(y)),signed_mean_mw=float(r.mean()),
      p95_abs_mw=float(np.quantile(abs(r),.95)))
def audit(pair):
    rows=[];hours=[];extras=[]
    for year in YEARS:
        e,b=pair["ID"][year]
        cases=[("EFS_from_ReEDS_minus",e,b,(-2,-3)),
               ("EFS_from_ReEDS_plus",e,b,(2,3)),
               ("ReEDS_from_EFS_minus",b,e,(-2,-3)),
               ("ReEDS_from_EFS_plus",b,e,(2,3)),
               ("EFS_from_ReEDS_expanded",e,b,(-1,-2,-3,-4))]
        for name,y,x,offs in cases:
            i,yy,X=align(y,x,offs);w=weights(yy,X);pred=X@w;r=yy-pred
            slope=np.diff(x,prepend=np.nan);good=np.isfinite(slope[i])
            corr=float(np.corrcoef(r[good],slope[i][good])[0,1])
            rows.append(dict(year=year,state="ID",orientation=name,offsets=str(offs),
                 weights=";".join(f"{v:.8f}" for v in w),
                 residual_vs_source_slope_corr=corr,**metrics(yy,pred)))
            if name in ("EFS_from_ReEDS_minus","ReEDS_from_EFS_plus","EFS_from_ReEDS_expanded"):
                for hour in range(24):
                    subset=r[i%24==hour]
                    hours.append(dict(year=year,orientation=name,source_ordinal_hour_mod24=hour,
                        signed_mean_mw=float(subset.mean()),mae_mw=float(abs(subset).mean()),n=len(subset)))
        i,y,X=align(e,b,(-1,-2,-3,-4))
        w4=weights(y,X);w2=weights(y,X[:,1:3])
        extras.append(dict(year=year,weights_4=w4.tolist(),weights_2=w2.tolist(),
             same_support_mae_gain_mw=float(abs(y-X[:,1:3]@w2).mean()-abs(y-X@w4).mean())))
    for year in YEARS:
        e,b=pair["OR"][year]
        for off in (-3,-2):
            i,y,X=align(e,b,(off,))
            rows.append(dict(year=year,state="OR",orientation="EFS_from_ReEDS_single",
                  offsets=str((off,)),weights="1.0",residual_vs_source_slope_corr=None,
                  **metrics(y,X[:,0])))
    return pd.DataFrame(rows),pd.DataFrame(hours),extras
def run(efs,h5):
    import h5py
    with h5.open("rb") as f:md5=hashlib.file_digest(f,"md5").hexdigest()
    if md5!=CHECKSUM:raise ValueError("Publisher HDF5 MD5 mismatch")
    src=pd.read_csv(efs,compression="infer")
    cols={"year","state","local_hour_id","load_mw"}
    if not cols.issubset(src) or src[list(cols)].isna().any().any():raise ValueError("Bad EFS archive")
    pairs={}
    with h5py.File(h5,"r") as f:
        for state in ("ID","OR"):
            pairs[state]={}
            for year in YEARS:
                d=src[(src.state==state)&(src.year==year)].sort_values("local_hour_id")
                if not np.array_equal(d.local_hour_id.to_numpy(),np.arange(1,N+1)):
                    raise ValueError("Missing source hours")
                g=f[str(year)];verify_publisher_2012_clock(g["datetime"][:])
                pairs[state][year]=(d.load_mw.to_numpy(),g[state][:])
    t,h,extra=audit(pairs)
    return t,h,dict(efs_sha256=hashlib.sha256(efs.read_bytes()).hexdigest(),
        reeds_md5=md5,expanded_components=extra,physical_efs_clock_verified=False,
        caution="Hour mod 24 is source ordinal, not certified physical local time; exploratory in-sample weights are not geographic shares.")
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--efs-hourly",type=Path,required=True)
    p.add_argument("--reeds-h5",type=Path,required=True)
    p.add_argument("--out-dir",type=Path,required=True)
    a=p.parse_args()
    t,h,meta=run(a.efs_hourly,a.reeds_h5)
    a.out_dir.mkdir(parents=True,exist_ok=True)
    t.to_csv(a.out_dir/"idaho_bidirectional_residual_metrics.csv",index=False)
    h.to_csv(a.out_dir/"idaho_signed_residual_by_source_hour.csv",index=False)
    (a.out_dir/"idaho_bidirectional_provenance.json").write_text(json.dumps(meta,indent=2)+"\n")
    print("RESULT_TABLE_BEGIN")
    print(t.to_string(index=False))
    print("RESULT_HOUR_SIGNED_BEGIN")
    print(h.to_string(index=False))
    print("RESULT_EXPANDED",json.dumps(meta["expanded_components"]))
if __name__=="__main__":main()
