"""Attach provenance-limited T&D owner metadata to EIA plant review records.

This is an evidence-enrichment join, NOT plant-bus electrical verification.
"""
import argparse
import json
from pathlib import Path
import pandas as pd


def enrich(review_path, owners_path, output_path, year):
    q=pd.read_csv(review_path,dtype={"plant_id":"string"})
    o=pd.read_csv(owners_path,dtype={"plant_id_eia":"string"})
    needed={"plant_id_eia","report_date","transmission_distribution_owner_id",
            "transmission_distribution_owner_name","transmission_distribution_owner_state"}
    if needed-set(o):
        raise ValueError("Missing yearly plant owner source fields")
    if "plant_id" not in q or q.plant_id.isna().any() or q.plant_id.duplicated().any():
        raise ValueError("Invalid review plant identities")
    dates=pd.to_datetime(o.report_date,errors="coerce")
    o=o.loc[dates.dt.year.eq(year)].copy()
    if o.plant_id_eia.isna().any() or o.plant_id_eia.duplicated().any():
        raise ValueError("Ambiguous or missing plant identity in year-specific owner records")
    cols=["plant_id_eia","transmission_distribution_owner_id",
          "transmission_distribution_owner_name","transmission_distribution_owner_state"]
    joined=q.merge(o[cols],left_on="plant_id",right_on="plant_id_eia",
                   how="left",validate="one_to_one",indicator=True)
    joined["owner_source_joined"]=joined["_merge"].eq("both")
    joined["owner_identity_available"]=joined.transmission_distribution_owner_id.notna() & joined.transmission_distribution_owner_name.notna()
    joined["electrical_connection_verified"]=False
    joined["eligible_for_real_dispatch"]=False
    joined["evidence_tier"]="G1_owner_only"
    joined.loc[~joined.owner_identity_available,"evidence_tier"]="G0_geographic_only"
    joined=joined.drop(columns=["_merge","plant_id_eia"])
    output_path.parent.mkdir(parents=True,exist_ok=True)
    joined.to_csv(output_path,index=False)
    report={"year":year,"review_plants":len(q),
            "owner_source_matched_plants":int(joined.owner_source_joined.sum()),
            "plants_with_owner_identity":int(joined.owner_identity_available.sum()),
            "verified_electrical_connections":0,"real_dispatch_approved":False}
    output_path.with_suffix(".json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))
    return report


def main():
    a=argparse.ArgumentParser()
    a.add_argument("--review",type=Path,required=True)
    a.add_argument("--owners",type=Path,required=True)
    a.add_argument("--year",type=int,required=True)
    a.add_argument("--out",type=Path,required=True)
    v=a.parse_args()
    enrich(v.review,v.owners,v.out,v.year)


if __name__=="__main__":main()
