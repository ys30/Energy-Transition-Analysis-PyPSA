"""Paper T v15: common-support baselines, inverse sector mixtures, storage precision.

One 4-sector experiment with 2030 first-half fit and fixed holdout evaluation.
A 14-subsector sensitivity is executed only if the primary model does not
approach the control-state rounding level. No claimed physical timezone.
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
import numpy as np,pandas as pd
from scipy.optimize import lsq_linear
from .reeds2022_reference_hdf5_provenance import CHECKSUM,YEARS,verify_publisher_2012_clock
from .efs_idaho_raw_sector_source_forensic import FIELDS
N=8760
SECTORS=("Commercial","Industrial","Residential","Transportation")
IDX=np.arange(3,N)  # ReEDS[h] versus EFS[h-2],EFS[h-3], both valid; 8757 keys
TRAIN=IDX<4380

def fit_inverse(target,component_matrix):
    """components: (K, 8760), one weight per component, 0 <= a_s <= 1."""
    lo=component_matrix[:,IDX-3].T
    delta=(component_matrix[:,IDX-2]-component_matrix[:,IDX-3]).T
    rhs=target[IDX]-lo.sum(axis=1)
    if np.max(np.abs(delta),axis=0).min()<1e-12:
        # The data contain all-zero end-use shapes: drop them, fix a=0.5.
        active=np.max(np.abs(delta),axis=0)>1e-12
    else:active=np.ones(delta.shape[1],dtype=bool)
    weights=np.full(delta.shape[1],0.5)
    if active.any():
        x=delta[TRAIN][:,active];y=rhs[TRAIN]
        solved=lsq_linear(x,y,bounds=(0,1),method="trf",
                          tol=1e-12,max_iter=1000,lsmr_tol="auto")
        if not solved.success:raise ValueError("Bounded fit did not converge: "+str(solved.message))
        weights[active]=solved.x
    return weights

def predict(comp,weights):
    lo=comp[:,IDX-3].T
    delta=(comp[:,IDX-2]-comp[:,IDX-3]).T
    return lo.sum(axis=1)+delta@weights

def score(y,p,mask):
    d=y[mask]-p[mask]
    return dict(n=int(mask.sum()),mae_mw=float(np.abs(d).mean()),
      rmse_mw=float(np.sqrt(np.mean(d*d))),over_1mw=int((np.abs(d)>1).sum()),
      p95_abs_mw=float(np.quantile(abs(d),.95)),bias_mw=float(d.mean()))

def parse_source(original):
    expected_year=set(YEARS)
    grouped=[]
    selected=0
    for chunk in pd.read_csv(original,usecols=FIELDS,chunksize=200000):
        p=chunk.loc[(chunk.Electrification=="Reference")&
            (chunk.TechnologyAdvancement=="Moderate")&
            (chunk.State=="ID")&(chunk.Year.isin(YEARS))]
        if p.empty:continue
        if p[FIELDS].isna().any().any():raise ValueError("Missing original fields")
        if not p.LocalHourID.between(1,N).all():raise ValueError("Bad source hour")
        if (p.LoadMW<0).any() or not np.isfinite(p.LoadMW.to_numpy()).all():
            raise ValueError("Invalid MW")
        selected+=len(p)
        grouped.append(p.groupby(["Year","Sector","Subsector","LocalHourID"],as_index=False).LoadMW.sum())
    if selected!=367920:raise ValueError("Wrong original population "+str(selected))
    t=pd.concat(grouped).groupby(["Year","Sector","Subsector","LocalHourID"],as_index=False).LoadMW.sum()
    if set(t.Year)!=expected_year:raise ValueError("Missing scenario years")
    keys=t[["Sector","Subsector"]].drop_duplicates().sort_values(["Sector","Subsector"])
    names=list(map(tuple,keys.itertuples(index=False,name=None)))
    if len(names)!=14 or set(t.Sector)!=set(SECTORS):raise ValueError("Unexpected subsector set")
    result={}
    for year in YEARS:
        arr=[]
        year_data=t[t.Year==year]
        for sec,sub in names:
            f=year_data[(year_data.Sector==sec)&(year_data.Subsector==sub)].sort_values("LocalHourID")
            if len(f)!=N or not np.array_equal(f.LocalHourID.to_numpy(),np.arange(1,N+1)):
                raise ValueError("Incomplete sub-sector chronology "+str((year,sec,sub)))
            arr.append(f.LoadMW.to_numpy(dtype=float))
        result[year]=np.stack(arr)
    return result,names,selected

def audit(original,state_file,reeds_file):
    import h5py
    with reeds_file.open("rb") as f:
        md5=hashlib.file_digest(f,"md5").hexdigest()
    if md5!=CHECKSUM:raise ValueError("Publisher HDF5 checksum mismatch")
    subs,names,selected=parse_source(original)
    archive=pd.read_csv(state_file,compression="infer")
    refs={};states={};precision=[];rounding=[]
    with h5py.File(reeds_file,"r") as h:
        for year in YEARS:
            g=h[str(year)]
            verify_publisher_2012_clock(g["datetime"][:])
            arr=g["ID"][:]
            refs[year]=np.asarray(arr,dtype=float)
            precision.append(dict(year=year,state="ID",storage_dtype=str(g["ID"].dtype),
              exact_integer_fraction=float(np.mean(refs[year]==np.rint(refs[year]))),
              max_distance_to_integer_mw=float(np.max(abs(refs[year]-np.rint(refs[year]))))))
            for state in ("OR","AZ","CA"):
                d=archive[(archive.year==year)&(archive.state==state)].sort_values("local_hour_id")
                if not np.array_equal(d.local_hour_id.to_numpy(),np.arange(1,N+1)):
                    raise ValueError("Bad archived state hours "+str((year,state)))
                shift={"OR":-3,"AZ":-2,"CA":-3}[state]
                j=np.arange(0,N+shift)
                resid=d.load_mw.to_numpy()[j]-g[state][:][j-shift]
                precision.append(dict(year=year,state=state,storage_dtype=str(g[state].dtype),
                  exact_integer_fraction=float(np.mean(g[state][:]==np.rint(g[state][:]))),
                  max_distance_to_integer_mw=float(np.max(abs(g[state][:]-np.rint(g[state][:]))))))
                for lft,rgt in [(-1.0,-.5),(-.5,-.4),(-.4,-.2),(-.2,0),(0,.2),(.2,.4),(.4,.5),(.5,1.)]:
                    rounding.append(dict(year=year,state=state,left_mw=lft,right_mw=rgt,
                       count=int(np.sum((resid>=lft)&(resid<rgt)))))
            d=archive[(archive.year==year)&(archive.state=="ID")].sort_values("local_hour_id")
            if not np.array_equal(d.local_hour_id.to_numpy(),np.arange(1,N+1)):
                raise ValueError("Bad archived Idaho")
            states[year]=d.load_mw.to_numpy(dtype=float)
            if not np.allclose(subs[year].sum(axis=0),states[year],rtol=0,atol=.001):
                raise ValueError("Original sector/subsector hourly reconciliation failed")
    four={year:np.stack([subs[year][[j for j,name in enumerate(names) if name[0]==s]].sum(axis=0)
           for s in SECTORS]) for year in YEARS}
    # Baseline comparison uses a common 8757 hour EFS target/ ReEDS source window.
    baseline=[]
    for year in YEARS:
        s=states[year];r=refs[year]
        y=s[:N-3]
        x2=r[2:N-1];x3=r[3:N]
        w=np.dot(y-x3,x2-x3)/np.dot(x2-x3,x2-x3)
        w=float(np.clip(w,0,1))
        for label,p in [("single_minus2_same8757",x2),("same_year_forward_mixture",w*x2+(1-w)*x3)]:
            baseline.append(dict(year=year,model=label,weight=w if label.startswith("same") else None,
                compared_hours=len(y),mae_mw=float(abs(y-p).mean()),over_1mw=int((abs(y-p)>1).sum())))
    # All inverse models are evaluated against the identical 8757 reference h indices.
    whole_weights=fit_inverse(refs[2030],states[2030][None,:])
    four_weights=fit_inverse(refs[2030],four[2030])
    output=[]
    for year in YEARS:
        y=refs[year][IDX]
        models={"inverse_single_minus2":states[year][IDX-2],
                "inverse_whole_2030_frozen":predict(states[year][None,:],whole_weights),
                "inverse_four_sector_2030_frozen":predict(four[year],four_weights)}
        for model,p in models.items():
            for window,mask in [("first_half",TRAIN),("second_half",~TRAIN),
                                ("full",np.ones(len(IDX),dtype=bool))]:
                output.append(dict(year=year,model=model,window=window,**score(y,p,mask)))
    result=pd.DataFrame(output)
    four_hold=result[(result.model=="inverse_four_sector_2030_frozen")&
              (((result.year==2030)&(result.window=="second_half"))|
               ((result.year>2030)&(result.window=="full")))]
    sub_triggered=bool((four_hold.mae_mw>1.).any())
    if sub_triggered:
        sub_weights=fit_inverse(refs[2030],subs[2030])
        for year in YEARS:
            y=refs[year][IDX];p=predict(subs[year],sub_weights)
            for window,mask in [("first_half",TRAIN),("second_half",~TRAIN),
                                ("full",np.ones(len(IDX),dtype=bool))]:
                output.append(dict(year=year,model="inverse_14_subsector_2030_frozen",
                    window=window,**score(y,p,mask)))
    else:sub_weights=None
    metadata=dict(original_csv_sha256=hashlib.sha256(original.read_bytes()).hexdigest(),
      official_reeds_md5=md5,year_count=3,source_records=selected,
      common_support_hours=8757,train_hours=int(TRAIN.sum()),
      holdout_hours=int((~TRAIN).sum()),sectors=list(SECTORS),
      whole_weight_2030_frozen=whole_weights.tolist(),
      four_sector_weights_2030_frozen=dict(zip(SECTORS,map(float,four_weights))),
      subsector_fallback_activated=sub_triggered,
      subsector_weights_2030_frozen={f"{a}|{b}":float(v) for (a,b),v in zip(names,sub_weights)} if sub_triggered else None,
      source_clock_certified=False,
      interpretation="Source-ordinal numerical audit, not identification of geographical time-zone proportions")
    return pd.DataFrame(baseline),pd.DataFrame(output),pd.DataFrame(precision),pd.DataFrame(rounding),metadata

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--original-efs",required=True,type=Path)
    p.add_argument("--state-hour",required=True,type=Path)
    p.add_argument("--reeds-h5",required=True,type=Path)
    p.add_argument("--out-dir",required=True,type=Path)
    a=p.parse_args()
    base,rows,storage,hist,meta=audit(a.original_efs,a.state_hour,a.reeds_h5)
    a.out_dir.mkdir(parents=True,exist_ok=True)
    for name,table in [("same_support_baseline.csv",base),
                       ("frozen_sector_models.csv",rows),("hdf5_integer_precision.csv",storage),
                       ("control_residual_histogram_bins.csv",hist)]:
        table.to_csv(a.out_dir/name,index=False)
    (a.out_dir/"provenance.json").write_text(json.dumps(meta,indent=2)+"\n")
    print("V15_BASELINES\n"+base.to_string(index=False))
    print("V15_FROZEN_RESULTS\n"+rows[rows.window.isin(["full","second_half"])].to_string(index=False))
    print("V15_STORAGE\n"+storage.to_string(index=False))
    print("V15_WEIGHTS\n"+json.dumps(meta,indent=2))
if __name__=="__main__":main()
