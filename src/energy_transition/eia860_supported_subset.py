"""Create an explicitly audited supported-carrier subset of EIA-860 nameplate.

This is a model-scope selection, NOT a claim of complete Western BA generation
capacity. Excluded storage/other fuels remain visible in the audit.
"""
import argparse
import json
import shutil
from pathlib import Path
import pandas as pd

SUPPORTED = {"NG","BFG","OG","WND","SUN","WAT","NUC","BIT","SUB",
             "LIG","WC","DFO","RFO","JF","KER","GEO"}

def subset(frame, bas, minimum_fraction=.85):
    required={"ba_code","fuel","capacity_mw"}
    if required-set(frame):raise ValueError("Missing EIA-860 capacity fields")
    x=frame[frame.ba_code.isin(bas)].copy()
    x["capacity_mw"]=pd.to_numeric(x.capacity_mw,errors="raise")
    if x.empty or x.capacity_mw.isna().any() or x.capacity_mw.lt(0).any():
        raise ValueError("No valid requested EIA-860 BA capacity")
    known=x.fuel.isin(SUPPORTED)
    selected=x[known].copy()
    excluded=x[~known].copy()
    fraction=float(selected.capacity_mw.sum()/x.capacity_mw.sum())
    if fraction<minimum_fraction:
        raise ValueError(f"Insufficient model-supported share of actual capacity: {fraction:.2%}")
    return selected,excluded,{"source_total_mw":float(x.capacity_mw.sum()),
        "model_supported_mw":float(selected.capacity_mw.sum()),
        "model_excluded_mw":float(excluded.capacity_mw.sum()),
        "model_supported_fraction":fraction,
        "excluded_by_fuel_mw":{str(k):float(v) for k,v in excluded.groupby("fuel").capacity_mw.sum().items()},
        "caution":"Exclusion is a declared model limitation, especially EIA MWH battery storage; not zero installed capacity."}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--capacity",type=Path,required=True)
    p.add_argument("--bas",nargs="+",default=["CISO","BPAT"])
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
    selected,excluded,report=subset(pd.read_csv(a.capacity),a.bas)
    selected.to_csv(a.output/a.capacity.name,index=False)
    excluded.to_csv(a.output/"excluded_unsupported_eia860_capacity.csv",index=False)
    source_manifest=a.capacity.with_name("ba_crosswalk_manifest_"+a.capacity.stem.rsplit("_",1)[-1]+".json")
    if not source_manifest.is_file():raise FileNotFoundError(source_manifest)
    shutil.copyfile(source_manifest,a.output/source_manifest.name)
    (a.output/"model_carrier_scope_audit.json").write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2))
if __name__=="__main__":main()
