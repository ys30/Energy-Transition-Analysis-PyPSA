"""Extract year-scoped PUDL plant owner records for reviewed EIA IDs.

Source is the published PUDL nightly Parquet; outputs retain provenance.
"""
import argparse
import json
from pathlib import Path
import duckdb
import pandas as pd


def extract(review, year, output):
    ids=pd.read_csv(review,dtype={"plant_id":"string"}).plant_id.dropna().tolist()
    if not ids or len(ids)!=len(set(ids)):
        raise ValueError("Review plant IDs missing or duplicated")
    connection=duckdb.connect()
    connection.execute("INSTALL httpfs; LOAD httpfs")
    source="s3://pudl.catalyst.coop/nightly/out_eia__yearly_plants.parquet"
    query="""SELECT CAST(plant_id_eia AS VARCHAR) AS plant_id_eia,
                    CAST(report_date AS VARCHAR) AS report_date,
                    CAST(transmission_distribution_owner_id AS VARCHAR) AS transmission_distribution_owner_id,
                    transmission_distribution_owner_name,
                    transmission_distribution_owner_state
             FROM read_parquet(?)
             WHERE year(report_date) = ? AND CAST(plant_id_eia AS VARCHAR) IN (SELECT unnest(?))"""
    data=connection.execute(query,[source,year,ids]).df()
    if data.plant_id_eia.duplicated().any():raise ValueError("PUDL duplicate plant-year keys")
    output.parent.mkdir(parents=True,exist_ok=True)
    data.to_csv(output,index=False)
    provenance={"year":year,"review_plant_ids":len(ids),"source_matched_ids":len(data),
      "source":"PUDL nightly out_eia__yearly_plants.parquet",
      "source_uri":source,"retrieval_is_version_pinned":False,
      "real_interconnection_verified":False}
    output.with_suffix(".source.json").write_text(json.dumps(provenance,indent=2)+"\n")
    return provenance


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--review",type=Path,required=True)
    p.add_argument("--year",type=int,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    print(json.dumps(extract(a.review,a.year,a.out),indent=2))
