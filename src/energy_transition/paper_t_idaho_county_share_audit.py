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
P14={"p16009":"Benewah","p16017":"Bonner","p16021":"Boundary","p16055":"Kootenai","p16057":"Latah","p16061":"Lewis","p16069":"Nez Perce"}
NINE={**SEVEN,"p16061":"Lewis","p16069":"Nez Perce"}
assert len(P14)==7 and len(NINE)==9 and len(set(P14)^set(SEVEN))==4
PARTIAL_COUNTY="p16049" # Idaho County is crossed by federal boundary; do not count entire county as Pacific
STATE_PREFIX="p16"
MODEL_PACIFIC_PROXY=1-0.834425  # contemporaneous fitted, NOT frozen
FROZEN_PACIFIC_PROXY=1-0.827385
POP_P14_2020=325198
POP_SEVEN_2020=301478
POP_STATE_2020=1839106
POP_NINE_2020=347101

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
    if not set(P14).issubset(frame.columns):raise ValueError("ReEDS p14 FIPS fields missing")
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
                    ent=results.setdefault(year,{"hours":0,"north_mwh":0.0,"p14_mwh":0.0,"nine_full_pacific_mwh":0.0,"idaho_county_mwh":0.0,"state_mwh":0.0})
                    ent["hours"]+=len(vals)
                    ent["north_mwh"]+=float(vals[list(SEVEN)].to_numpy().sum())
                    ent["p14_mwh"]+=float(vals[list(P14)].to_numpy().sum())
                    ent["nine_full_pacific_mwh"]+=float(vals[list(NINE)].to_numpy().sum())
                    ent["idaho_county_mwh"]+=float(vals[PARTIAL_COUNTY].sum())
                    ent["state_mwh"]+=float(vals.to_numpy().sum())
    years=[]
    for y in range(2016,2024):
        r=results.get(y)
        if not r or r["hours"] not in (8760,8784) or r["state_mwh"]<=0:
            raise ValueError(f"Year {y} has incomplete/invalid coverage: {r}")
        share=r["north_mwh"]/r["state_mwh"]
        years.append({"year":y,**r,"north_share_pct":100*share,
                      "difference_from_idaho_fit_pp":100*(share-MODEL_PACIFIC_PROXY),
                      "p14_share_pct":100*r["p14_mwh"]/r["state_mwh"],
                      "p14_minus_same_year_fit_pp":100*(r["p14_mwh"]/r["state_mwh"]-MODEL_PACIFIC_PROXY),
                      "p14_minus_frozen_fit_pp":100*(r["p14_mwh"]/r["state_mwh"]-FROZEN_PACIFIC_PROXY),
                      "nine_full_pacific_share_pct":100*r["nine_full_pacific_mwh"]/r["state_mwh"],
                      "nine_plus_all_idaho_county_upper_pct":100*(r["nine_full_pacific_mwh"]+r["idaho_county_mwh"])/r["state_mwh"]})
    out={"source":URL,"sha256":sha.hexdigest(),"years":years,
         "seven_proxy_counties":SEVEN,"reeds_p14_counties":P14,"nine_full_pacific_counties":NINE,
         "idaho_county_partially_pacific":PARTIAL_COUNTY,
         "population_2020": {"north_seven":POP_SEVEN_2020,"reeds_p14_seven":POP_P14_2020,
                             "reeds_p14_share_pct":100*POP_P14_2020/POP_STATE_2020,"idaho":POP_STATE_2020,
                             "share_pct":100*POP_SEVEN_2020/POP_STATE_2020,
                             "nine_full_pacific_counties":POP_NINE_2020,
                             "nine_full_pacific_share_pct":100*POP_NINE_2020/POP_STATE_2020},
         "same_year_fitted_idaho_component_pct":100*MODEL_PACIFIC_PROXY,
         "frozen_idaho_component_pct":100*FROZEN_PACIFIC_PROXY,
         "fitted_idaho_northern_share_pct":100*MODEL_PACIFIC_PROXY,
         "scope_warning":"ReEDS p14 seven counties differ from prior erroneous seven-county proxy and from nine full Pacific-time counties. Full Pacific territory also includes part of Idaho County. ReEDS p14 excludes Clearwater and Shoshone.",
         "lineage_warning":"The 2026 county model is not source-independent of all EIA/ReEDS inputs, and cannot certify EER 2022 time-zone splitting.",
         "physical_hour_join":"BLOCK_PHYSICAL_JOIN"}
    a.output.write_text(json.dumps(out,indent=2)+"\n")
    print(json.dumps(out,indent=2))
if __name__=="__main__":main()
