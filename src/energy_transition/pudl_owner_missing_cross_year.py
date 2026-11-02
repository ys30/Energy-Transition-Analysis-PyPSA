"""Cross-year PUDL missing-owner reconciliation (evidence only)."""
import argparse,json
from pathlib import Path
import pandas as pd

def audit(a,b,out):
    years={}
    for year,path in ((2023,a),(2024,b)):
        d=pd.read_csv(path,dtype={"plant_id":"string"})
        required={"plant_id","owner_identity_available","electrical_connection_verified","eligible_for_real_dispatch"}
        if required-set(d):raise ValueError(f"{year} missing fields")
        if d.plant_id.isna().any() or d.plant_id.duplicated().any():raise ValueError(f"{year} duplicate/null plant ID")
        for col in ("owner_identity_available","electrical_connection_verified","eligible_for_real_dispatch"):
            values=d[col].astype("string").str.lower()
            if values.isna().any() or not values.isin(["true","false"]).all():raise ValueError(f"{year} bad {col}")
            d[col]=values.eq("true")
        if d.electrical_connection_verified.any() or d.eligible_for_real_dispatch.any():
            raise ValueError("Owner metadata cannot approve real dispatch")
        years[year]=set(d.loc[~d.owner_identity_available,"plant_id"].astype(str))
    result={"missing_owner_2023":sorted(years[2023]),"missing_owner_2024":sorted(years[2024]),
            "persistent_missing_owner":sorted(years[2023]&years[2024]),
            "only_2023":sorted(years[2023]-years[2024]),
            "only_2024":sorted(years[2024]-years[2023]),
            "electrical_connections_verified":0,"real_dispatch_approved":False}
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))
    return result

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--year-2023",type=Path,required=True)
    p.add_argument("--year-2024",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    v=p.parse_args()
    audit(v.year_2023,v.year_2024,v.out)
