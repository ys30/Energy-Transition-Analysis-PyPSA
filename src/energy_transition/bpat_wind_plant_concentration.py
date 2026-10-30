"""BPAT wind EIA-923 source-record concentration audit.

EIA-930 supplies no plant-wise wind records; concentration does not establish
which plants explain a cross-product aggregate reporting discrepancy.
"""
import argparse,json
from pathlib import Path
import pandas as pd

def summarize(frame):
    x=frame[frame.ba_code.eq("BPAT") & frame.fuel.eq("WND")].copy()
    if x.empty:raise ValueError("No BPAT wind plant records")
    if x.source_row_id.duplicated().any():raise ValueError("Duplicate source rows")
    if not x.qualified.astype(str).str.lower().eq("true").all():
        raise ValueError("BPAT wind includes unqualified rows")
    if not x.plant_match_status.eq("matched").all():
        raise ValueError("BPAT wind includes unmatched BA attribution")
    x["qualified_generation_mwh"]=pd.to_numeric(x.qualified_generation_mwh,errors="raise")
    plants=x.groupby("plant_id",as_index=False).agg(
      source_rows=("source_row_id","size"),
      net_generation_mwh=("qualified_generation_mwh","sum"))
    plants=plants.sort_values("net_generation_mwh",ascending=False)
    total=float(plants.net_generation_mwh.sum())
    if total<=0:raise ValueError("Unexpected BPAT wind net generation")
    plants["share_of_qualified_bpat_wind"]=plants.net_generation_mwh/total
    plants["cumulative_share"]=plants.share_of_qualified_bpat_wind.cumsum()
    return plants,{"source_rows":len(x),"distinct_plants":len(plants),
      "qualified_eia923_wind_mwh":total,
      "top_5_plant_generation_share":float(plants.head(5).net_generation_mwh.sum()/total),
      "limitation":"No EIA-930 plant-level counterparty; cannot attribute 1.981 TWh discrepancy to specific plants."}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--plant-audit",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
    plants,report=summarize(pd.read_csv(a.plant_audit,dtype={"plant_id":"string"}))
    plants.to_csv(a.output/"bpat_wind_qualified_plant_concentration.csv",index=False)
    (a.output/"provenance.json").write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2))
    print(plants.head(15).to_string(index=False))
if __name__=="__main__":main()
