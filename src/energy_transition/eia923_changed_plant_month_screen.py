"""Official EIA-923 plant-level monthly exposure screen, NOT generator-level generation."""
import argparse,io,json,urllib.request
from pathlib import Path
import pandas as pd
from .eia923_ba_generation import extract_page1
from .eia923_schema_audit import URL

TARGETS={"66183":{"generator":"CWE","event":"2024-01 commissioning"},
         "66811":{"generator":"CW3","event":"2024-09 commissioning"},
         "2454":{"generator":"1","event":"2024-01 retirement"}}

def audit(content,out):
    _,monthly=extract_page1(content)
    selected=monthly.loc[monthly.plant_id.isin(TARGETS)].copy()
    rows=[]
    for plant,meta in TARGETS.items():
        match=selected.loc[selected.plant_id.eq(plant)]
        for month in range(1,13):
            part=match.loc[match.month.eq(month)]
            nonnumeric=int(part.netgen_mwh.isna().sum())
            fuels=sorted(part.fuel.dropna().astype(str).unique().tolist())
            rows.append({"plant_id":plant,"target_generator_id":meta["generator"],
                "target_generator_event":meta["event"],"month":month,
                "plant_page1_rows":len(part),"nonnumeric_cells":nonnumeric,
                "plant_mwh_numeric_sum":float(part.netgen_mwh.sum()) if len(part) and not nonnumeric else None,
                "reported_fuel_codes":";".join(fuels),
                "raw_nonnumeric_tokens":";".join(sorted(set(part.loc[part.netgen_mwh.isna(),"source_netgen"].astype("string").fillna("<missing>").tolist()))),
                "observation_class":("source_dot_not_zero" if nonnumeric and set(part.loc[part.netgen_mwh.isna(),"source_netgen"].astype("string").str.strip())=={"."} else ("other_missing_or_nonnumeric" if nonnumeric else ("no_source_rows" if not len(part) else "numeric_observed"))),
                "can_attribute_generation_to_target_generator":False})
    out.parent.mkdir(parents=True,exist_ok=True)
    result=pd.DataFrame(rows)
    result.to_csv(out,index=False)
    report={"source":URL.format(year=2024),
        "nonnumeric_months_by_plant":result.loc[result.nonnumeric_cells.gt(0)].groupby("plant_id").month.apply(list).to_dict(),
        "nonnumeric_source_tokens_by_plant":result.loc[result.nonnumeric_cells.gt(0)].groupby("plant_id").raw_nonnumeric_tokens.apply(lambda x: sorted(set(x))).to_dict(),
        "complete_numeric_months":int(((result.plant_page1_rows>0)&result.nonnumeric_cells.eq(0)).sum()),
        "plant_month_rows":len(result),
        "missing_plant_months":int(result.plant_page1_rows.eq(0).sum()),
        "non_numeric_plant_months":int(result.nonnumeric_cells.gt(0).sum()),
        "source_dot_plant_months":int(result.observation_class.eq("source_dot_not_zero").sum()),
        "generator_level_mwh_attributed":False,
        "caution":"Page 1 can aggregate multiple generators, primes and fuels. Do not label plant MWh as one generator's output."}
    out.with_suffix(".json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))
if __name__=="__main__":
    a=argparse.ArgumentParser()
    a.add_argument("--out",type=Path,required=True)
    args=a.parse_args()
    req=urllib.request.Request(URL.format(year=2024),headers={"User-Agent":"energy-transition-research/0.4"})
    with urllib.request.urlopen(req,timeout=120) as f:content=f.read()
    audit(content,args.out)
