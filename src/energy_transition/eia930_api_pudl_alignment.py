"""Same-hour independent cross-check: EIA API hourly records versus PUDL stages.

No annual-sum comparisons are permitted without timestamp intersection.
EIA timestamp interpretation is reported via exact and +/-1h candidate alignment.
"""
import argparse
import json
from pathlib import Path
import pandas as pd
from .pudl_eia930_stage_audit import fetch as fetch_pudl
from .eia930_balance_audit import fetch_ti
from .eia930_generation_audit import fetch_net_generation
from .eia930_west import fetch_eia_demand


def compare(api, pudl, stages=("reported","adjusted")):
    records=[]
    api=api.copy();pudl=pudl.copy()
    api["period"]=pd.to_datetime(api.period,utc=True)
    pudl["datetime_utc"]=pd.to_datetime(pudl.datetime_utc,utc=True)
    for shift in (-1,0,1):
        shifted=api.copy()
        shifted["datetime_utc"]=shifted.period+pd.Timedelta(hours=shift)
        for stage in stages:
            cols=[f"{field}_{stage}_mwh" for field in ("demand","net_generation","interchange")]
            for v,col in zip(("demand","generation","interchange"),cols):
                left=shifted[["respondent","datetime_utc",v]].rename(columns={v:"api"})
                right=pudl[["balancing_authority_code_eia","datetime_utc",col]].rename(
                    columns={"balancing_authority_code_eia":"respondent",col:"pudl"})
                paired=left.merge(right,on=["respondent","datetime_utc"],how="inner")
                paired=paired.dropna(subset=["api","pudl"])
                for ba,part in paired.groupby("respondent"):
                    difference=part.api-part.pudl
                    records.append({
                      "ba_code":ba,"stage":stage,"series":v,"api_shift_hours":shift,
                      "same_hour_pairs":len(part),
                      "mean_difference_mw":float(difference.mean()),
                      "mae_mw":float(difference.abs().mean()),
                      "max_abs_difference_mw":float(difference.abs().max()),
                      "exact_match_fraction":float(difference.abs().lt(1e-6).mean())
                    })
    return pd.DataFrame(records)


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--year",type=int,default=2024)
    p.add_argument("--bas",nargs="+",default=["BPAT","CISO"])
    p.add_argument("--output",type=Path,default=Path("outputs/pudl_api_alignment"))
    args=p.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    source={"demand":fetch_eia_demand(args.year,args.bas),
            "generation":fetch_net_generation(args.year,args.bas),
            "interchange":fetch_ti(args.year,args.bas)}
    api=None
    for col,frame in source.items():
        part=frame[["respondent","period","value"]].rename(columns={"value":col})
        api=part if api is None else api.merge(part,on=["respondent","period"],how="outer",validate="one_to_one")
    pudl=fetch_pudl(args.year,args.bas)
    comparison=compare(api,pudl)
    if comparison.empty: raise ValueError("No EIA-930 API/PUDL overlapping hourly records")
    comparison.to_csv(args.output/"api_pudl_same_hour_comparison.csv",index=False)
    (args.output/"provenance.json").write_text(json.dumps({
       "year":args.year,"bas":args.bas,
       "candidate_api_hour_shifts":[-1,0,1],
       "source":"EIA-930 API vs Catalyst PUDL core_eia930__hourly_operations nightly",
       "caution":"Shift is a diagnostic, not a correction. Demand includes previously audited EIA API short-gap handling; assess imputed flags before scientific calibration."
    },indent=2))
    print(comparison.to_string(index=False))
if __name__=="__main__":main()
