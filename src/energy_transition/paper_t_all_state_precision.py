"""Audit all 11 ReEDS HDF5 stored hourly-array integer types and residual tail counts."""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
import numpy as np,pandas as pd
from .reeds2022_reference_hdf5_provenance import CHECKSUM,STATES,YEARS,verify_publisher_2012_clock
SHIFTS={"AZ":-2,"CO":-2,"ID":-2,"MT":-2,"NM":-2,"UT":-2,"WY":-2,
        "CA":-3,"NV":-3,"OR":-3,"WA":-3}
N=8760
def check(efs,hdf):
    import h5py
    with hdf.open("rb") as f:dig=hashlib.file_digest(f,"md5").hexdigest()
    if dig!=CHECKSUM:raise ValueError("Publisher HDF5 MD5 invalid")
    frame=pd.read_csv(efs,compression="infer")
    rows=[];tails=[]
    with h5py.File(hdf) as h:
        for year in YEARS:
            g=h[str(year)]
            verify_publisher_2012_clock(g["datetime"][:])
            for state in SHIFTS:
                raw=g[state]
                v=raw[:]
                st=frame[(frame.year==year)&(frame.state==state)].sort_values("local_hour_id")
                if not np.array_equal(st.local_hour_id.to_numpy(),np.arange(1,N+1)):
                    raise ValueError("Source missing "+str((year,state)))
                k=SHIFTS[state]
                i=np.arange(0,N+k)
                r=st.load_mw.to_numpy()[i]-v[i-k]
                ab=np.abs(r)
                rows.append(dict(year=year,state=state,hdf5_dtype=str(raw.dtype),
                    total_hdf5_hours=len(v),non_integer_hdf5_values=int(np.count_nonzero(v!=np.rint(v))),
                    exact_integer_fraction=float(np.mean(v==np.rint(v))),
                    nonwrapping_lag=k,compared_hours=len(i),
                    abs_error_over_0_5mw=int(np.count_nonzero(ab>.5)),
                    abs_error_over_1mw=int(np.count_nonzero(ab>1.)),
                    residual_max_abs_mw=float(ab.max()),residual_mae_mw=float(ab.mean())))
                if state in ("OR","AZ","CA"):
                    tails.append(dict(year=year,state=state,compared_hours=len(i),
                        above_0_5mw=int(np.count_nonzero(ab>.5)),
                        negative_below_minus_0_5=int(np.count_nonzero(r<-.5)),
                        positive_above_0_5=int(np.count_nonzero(r>.5))))
    return pd.DataFrame(rows),pd.DataFrame(tails),dict(publisher_md5=dig,
           original_archive_sha256=hashlib.sha256(efs.read_bytes()).hexdigest(),
           integer_check_all_33_arrays=True,physically_verified_time=False)
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--efs-hourly",type=Path,required=True)
    p.add_argument("--reeds-h5",type=Path,required=True)
    p.add_argument("--out-dir",type=Path,required=True)
    a=p.parse_args()
    table,tails,meta=check(a.efs_hourly,a.reeds_h5)
    a.out_dir.mkdir(parents=True,exist_ok=True)
    table.to_csv(a.out_dir/"all_11_states_hdf5_storage_and_residual_tails.csv",index=False)
    tails.to_csv(a.out_dir/"OR_AZ_CA_above_0p5mw.csv",index=False)
    (a.out_dir/"source_verification.json").write_text(json.dumps(meta,indent=2)+"\n")
    print("ALL_STATES_PRECISION\n"+table.to_string(index=False))
    print("CONTROL_TAILS\n"+tails.to_string(index=False))
if __name__=="__main__":main()
