"""Paper T Idaho northern-seven-county independent share audit.

The seven counties are an explicit *proxy set*, NOT the complete statutory Pacific
time-zone territory. ReEDS2022 EFS_REFERENCE remains BLOCK_PHYSICAL_JOIN.
"""
import argparse, hashlib, json, urllib.request
from pathlib import Path
import pandas as pd
import h5py
import numpy as np

URL="https://data.openei.org/files/8562/historic_load_hourly_2016_2023_county.h5"
SEVEN={"p16009":"Benewah","p16017":"Bonner","p16021":"Boundary",
       "p16035":"Clearwater","p16055":"Kootenai","p16057":"Latah","p16079":"Shoshone"}
STATE_PREFIX="p16"
MODEL_PACIFIC_PROXY=1-0.834425
POP_SEVEN_2020=301478
POP_STATE_2020=1839106

def download(path):
    if path.exists():return
    tmp=path.with_suffix(".partial")
    request=urllib.request.Request(URL,headers={"User-Agent":"Paper-T-scientific-audit/1.0"})
    with urllib.request.urlopen(request,timeout=240) as resp,tmp.open("wb") as f:
        while True:
            b=resp.read(8*1024*1024)
            if not b:break
            f.write(b)
    tmp.rename(path)

def prepare(frame):
    if isinstance(frame,pd.Series):raise ValueError("Expected hourly county columns")
    frame.columns=[str(c) for c in frame.columns]
    if not set(SEVEN).issubset(frame.columns):raise ValueError("Seven county FIPS fields missing")
    state=[c for c in frame.columns if c.startswith(STATE_PREFIX) and len(c)==6 and c[1:].isdigit()]
    if len(state)!=44:raise ValueError(f"Idaho should have 44 county columns, got {len(state)}: {state}")
    frame=frame[state].apply(pd.to_numeric,errors="raise")
    if frame.isna().any().any():raise ValueError("Nonfinite county entries; no silent filling")
    return frame

def main():
    p=argparse.ArgumentParser();p.add_argument("--output",type=Path,required=True)
    p.add_argument("--source",type=Path,default=Path("/tmp/county_load_2016_2023.h5"))
    a=p.parse_args();a.output.parent.mkdir(parents=True,exist_ok=True)
    download(a.source)
    sha=hashlib.sha256()
    with a.source.open("rb") as f:
        for b in iter(lambda:f.read(8*1024*1024),b""):sha.update(b)
    results={}
    # HDF may store years as separate keys; discover actual published layout.
    with pd.HDFStore(a.source,"r") as store:
        keys=store.keys()
        print("Discovered HDF keys:",keys,flush=True)
        if not keys:raise ValueError("No pandas HDFStore keys; inspect archive layout first")
        for key in keys:
            st=store.get_storer(key)
            if getattr(st,"is_table",False):
                chunked=store.select(key,chunksize=168)
            else:
                # pandas fixed-format HDF5: read *only* Idaho columns using h5py;
                # never materialize all 3109 nationwide county series in RAM.
                with h5py.File(a.source,"r") as hf:
                    root=hf[key.lstrip("/")]
                    datasets={name:root[name] for name in root if isinstance(root[name],h5py.Dataset)}
                    print("Fixed HDF datasets:",{n:list(d.shape) for n,d in datasets.items()},flush=True)
                    if not {"axis0","axis1","block0_items","block0_values"}.issubset(datasets):
                        raise ValueError("Unknown fixed HDF structure; inspect schema")
                    items=[v.decode() if isinstance(v,bytes) else str(v) for v in datasets["block0_items"][:]]
                    chosen=sorted((i,v) for i,v in enumerate(items) if v.startswith(STATE_PREFIX) and len(v)==6 and v[1:].isdigit())
                    if len(chosen)!=44:raise ValueError(f"Expected 44 Idaho county columns; got {len(chosen)}")
                    indexes=[i for i,v in chosen]
                    values=datasets["block0_values"][:,indexes]
                    index_raw=datasets["axis1"][:]
                    timestamps=pd.to_datetime(index_raw,utc=True)
                    frame=pd.DataFrame(values,index=timestamps,columns=[v for i,v in chosen])
                    chunked=[frame]
            for chunk in chunked:
                if isinstance(chunk.index,pd.MultiIndex):raise ValueError("Unexpected multi-index")
                ix=pd.to_datetime(chunk.index,utc=True,errors="coerce")
                if ix.isna().any():raise ValueError("Non-datetime hourly UTC index")
                chunk=prepare(chunk)
                for year in range(2016,2024):
                    m=ix.year==year
                    if not m.any():continue
                    vals=chunk.loc[m]
                    if (vals<0).any().any():raise ValueError("Negative demand observations")
                    ent=results.setdefault(year,{"hours":0,"north_mwh":0.0,"state_mwh":0.0})
                    ent["hours"]+=len(vals)
                    ent["north_mwh"]+=float(vals[list(SEVEN)].to_numpy().sum())
                    ent["state_mwh"]+=float(vals.to_numpy().sum())
    years=[]
    for y in range(2016,2024):
        r=results.get(y)
        if not r or r["hours"] not in (8760,8784) or r["state_mwh"]<=0:
            raise ValueError(f"Year {y} has incomplete/invalid coverage: {r}")
        share=r["north_mwh"]/r["state_mwh"]
        years.append({"year":y,**r,"north_share_pct":100*share,
                      "difference_from_idaho_fit_pp":100*(share-MODEL_PACIFIC_PROXY)})
    out={"source":URL,"sha256":sha.hexdigest(),"years":years,
         "seven_proxy_counties":SEVEN,
         "population_2020": {"north_seven":POP_SEVEN_2020,"idaho":POP_STATE_2020,
                             "share_pct":100*POP_SEVEN_2020/POP_STATE_2020},
         "fitted_idaho_northern_share_pct":100*MODEL_PACIFIC_PROXY,
         "scope_warning":"7-county population/load proxy only; not the legally complete Pacific-time territory, which includes other counties/part of Idaho County.",
         "lineage_warning":"The 2026 county model is not source-independent of all EIA/ReEDS inputs, and cannot certify EER 2022 time-zone splitting.",
         "physical_hour_join":"BLOCK_PHYSICAL_JOIN"}
    a.output.write_text(json.dumps(out,indent=2)+"\n")
    print(json.dumps(out,indent=2))
if __name__=="__main__":main()
