"""Audit original EIA-860 Operable versus Proposed sheets for all priority plants.

Never infer current operating supply from a proposed-plant record.
"""
import argparse
import io
import json
import urllib.request
import zipfile
from pathlib import Path
import pandas as pd

from .eia860_plant_generator_sheet_audit import URL


def audit(raw, year, queue, out):
    review=pd.read_csv(queue,dtype={"plant_id":"string"})
    if review.plant_id.isna().any() or review.plant_id.duplicated().any():
        raise ValueError("Invalid priority plant IDs")
    targets=set(review.plant_id.astype(str))
    found=[]
    sheets={}
    other_sheet_hits=[]
    unparsed_sheets=[]
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        matches=[x for x in z.namelist() if x.lower().endswith((".xlsx",".xls")) and "3_1_generator" in x.lower()]
        if len(matches)!=1:raise ValueError("Expected exactly one generator workbook")
        book=pd.ExcelFile(io.BytesIO(z.read(matches[0])))
        for sheet in ("Operable","Proposed"):
            if sheet not in book.sheet_names:raise ValueError(f"Missing {sheet} sheet")
            data=None
            for hdr in (1,0,2):
                d=pd.read_excel(book,sheet_name=sheet,header=hdr)
                col={str(k).strip().lower():k for k in d.columns}
                p=next((v for k,v in col.items() if k in ("plant code","plant id","plant id number")),None)
                g=next((v for k,v in col.items() if k in ("generator id","generator id number")),None)
                if p is not None and g is not None:
                    data=(d,col,p,g);break
            if data is None:raise ValueError(f"Unrecognized schema in {sheet}")
            d,col,p,g=data
            sheets[sheet]=len(d)
            ids=d[p].astype("string").str.strip().str.replace(r"\.0$","",regex=True)
            hits=d.loc[ids.isin(targets)].copy()
            status_key=next((v for k,v in col.items() if k in ("status","operational status")),None)
            for _,r in hits.iterrows():
                pid=str(r[p]).removesuffix(".0")
                gen=str(r[g]).strip()
                if not gen or gen=="nan":raise ValueError("Missing generator ID")
                status=str(r[status_key]).strip() if status_key else ""
                found.append({"year":year,"plant_id":pid,"generator_id":gen,
                              "source_sheet":sheet,"reported_status":status,
                              "operable_sheet":sheet=="Operable",
                              "counted_as_operating":sheet=="Operable" and status=="OP",
                              "electrical_connection_verified":False})
    # Source inventory can contain retired/cancelled sheets. Audit these separately
    # without changing the strict historical Operable/Proposed supply gate.
    for sheet in book.sheet_names:
        if sheet in ("Operable","Proposed"):
            continue
        parsed=None
        for hdr in (1,0,2):
            d=pd.read_excel(book,sheet_name=sheet,header=hdr)
            columns={str(k).strip().lower():k for k in d.columns}
            plant_col=next((v for k,v in columns.items() if k in ("plant code","plant id","plant id number")),None)
            if plant_col is not None:
                parsed=(d,plant_col)
                break
        if parsed is None:
            unparsed_sheets.append(str(sheet))
            continue
        d,plant_col=parsed
        ids=d[plant_col].astype("string").str.strip().str.replace(r"\.0$","",regex=True)
        for plant in sorted(set(ids[ids.isin(targets)].dropna().astype(str))):
            other_sheet_hits.append({"plant_id":plant,"source_sheet":str(sheet),
                                     "year":year,"eligible_as_operating_supply":False})
    df=pd.DataFrame(found,columns=["year","plant_id","generator_id","source_sheet","reported_status",
                                   "operable_sheet","counted_as_operating","electrical_connection_verified"])
    if df.duplicated(["plant_id","generator_id"]).any():
        raise ValueError("Duplicate plant-generator across inventoried sheets")
    out.parent.mkdir(parents=True,exist_ok=True)
    df.to_csv(out,index=False)
    pd.DataFrame(other_sheet_hits,columns=["plant_id","source_sheet","year","eligible_as_operating_supply"]).to_csv(out.with_name(out.stem+"_other_sheets.csv"),index=False)
    proposed=set(df.loc[df.source_sheet.eq("Proposed"),"plant_id"])
    operable=set(df.loc[df.source_sheet.eq("Operable"),"plant_id"])
    missing=sorted(targets-set(df.plant_id))
    other_hits_on_missing=[row for row in other_sheet_hits if row["plant_id"] in missing]
    unresolved=sorted(set(missing)-{row["plant_id"] for row in other_hits_on_missing})
    summary={"year":year,"priority_plant_ids":len(targets),"matched_plant_ids":len(set(df.plant_id)),
      "operable_sheet_plant_ids":len(operable),"proposed_sheet_plant_ids":len(proposed),
      "plants_in_both_sheets":len(operable&proposed),
      "plants_not_in_either_sheet":missing,"other_sheet_matches_for_missing":other_hits_on_missing,
      "unresolved_after_all_parseable_sheets":unresolved,"unparsed_workbook_sheets":unparsed_sheets,
      "source_sheet_rows":sheets,
      "plant_59047_proposed": "59047" in proposed,
      "plant_59047_operable": "59047" in operable,
      "real_generator_bus_connections_verified":0,
      "note":"Source sheet/status eligibility is distinct from verified generator-to-network connectivity."}
    out.with_suffix(".json").write_text(json.dumps(summary,indent=2)+"\n")
    print(json.dumps(summary,indent=2))
    return summary


if __name__=="__main__":
    a=argparse.ArgumentParser()
    a.add_argument("--year",type=int,required=True)
    a.add_argument("--queue",type=Path,required=True)
    a.add_argument("--out",type=Path,required=True)
    v=a.parse_args()
    req=urllib.request.Request(URL.format(year=v.year),headers={"User-Agent":"energy-transition-annual-audit/1.0"})
    with urllib.request.urlopen(req,timeout=120) as r:raw=r.read()
    audit(raw,v.year,v.queue,v.out)
