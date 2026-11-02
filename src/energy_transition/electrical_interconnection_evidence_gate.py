"""Strict admission gate for documentary generator-to-original-network-bus links.

Geographic proximity, matching BA or transmission owner are insufficient.
"""
import argparse,json
from pathlib import Path
import pandas as pd

REQUIRED={"plant_id","generator_id","network_bus_id","substation_id","connection_voltage_kv",
          "source_document_url","source_document_year","source_network_bus_evidence",
          "evidence_type","review_status"}
ELIGIBLE={"official_interconnection_agreement","utility_single_line_diagram","official_facility_interconnection_record"}

def audit(path,out):
    df=pd.read_csv(path,dtype="string")
    missing=REQUIRED-set(df.columns)
    if missing: raise ValueError(f"Missing required crosswalk evidence fields: {sorted(missing)}")
    if df.duplicated(["plant_id","generator_id","network_bus_id"]).any():
        raise ValueError("Duplicate plant/generator/bus evidence")
    valid=(df["review_status"].eq("independently_verified") &
           df["evidence_type"].isin(ELIGIBLE) &
           df["source_document_url"].str.startswith("https://",na=False) &
           df["source_network_bus_evidence"].notna() &
           df["source_document_year"].str.fullmatch(r"20\\d{2}",na=False) &
           pd.to_numeric(df["connection_voltage_kv"],errors="coerce").gt(0) &
           df[["plant_id","generator_id","network_bus_id","substation_id"]].notna().all(axis=1))
    verified=df.loc[valid].copy()
    report={"candidate_rows":len(df),"documentation_complete_rows":int(valid.sum()),
            "verified_unique_generator_bus_keys":int(verified[["plant_id","generator_id","network_bus_id"]].drop_duplicates().shape[0]),
            "rejected_rows":int((~valid).sum()),
            "admission_note":"Documentary structural gate only; manual provenance and electrical topology review still required",
            "automated_approval_of_empirical_dispatch":False}
    out.parent.mkdir(parents=True,exist_ok=True)
    verified.to_csv(out.with_suffix(".verified.csv"),index=False)
    out.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))
    return report
if __name__=="__main__":
    a=argparse.ArgumentParser();a.add_argument("--input",type=Path,required=True);a.add_argument("--out",type=Path,required=True)
    x=a.parse_args();audit(x.input,x.out)
