"""Audit a specific plant across original EIA-860 annual generator workbooks.

Report separately Operable and Proposed (never infer operating from plant existence).
"""
import argparse
import io
import json
import urllib.request
import zipfile
from pathlib import Path
import pandas as pd

URL="https://www.eia.gov/electricity/data/eia860/archive/xls/eia860{year}.zip"


def audit_zip(raw, year, plant_id):
    found=[]
    inspected_sheets=[]
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        files=[x for x in archive.namelist() if x.lower().endswith((".xlsx",".xls")) and "3_1_generator" in x.lower()]
        if not files:
            raise ValueError("EIA generator workbook absent")
        book=pd.ExcelFile(io.BytesIO(archive.read(files[0])))
        for sheet in book.sheet_names:
            if sheet.lower() not in ("operable","proposed","retired","retired and canceled","canceled or postponed","cancelled or postponed"):
                continue
            table=None
            for hdr in (1,0,2):
                df=pd.read_excel(book,sheet_name=sheet,header=hdr)
                columns={str(x).strip().lower():x for x in df.columns}
                pc=next((v for k,v in columns.items() if k in ("plant code","plant id","plant id number")),None)
                gc=next((v for k,v in columns.items() if k in ("generator id","generator id number")),None)
                if pc is not None and gc is not None:
                    table=(df,columns,pc,gc);break
            if table is None:
                raise ValueError(f"Unrecognized {sheet} sheet schema")
            df,columns,pc,gc=table
            inspected_sheets.append({"sheet":sheet,"rows":len(df),"id_column":str(pc)})
            ids=df[pc].astype("string").str.strip().str.replace(r"\.0$","",regex=True)
            selection=df.loc[ids.eq(str(plant_id)).fillna(False)]
            for _,r in selection.iterrows():
                status=next((r[v] for k,v in columns.items() if k in ("status","operational status")),None)
                fuel=next((r[v] for k,v in columns.items() if k=="energy source 1"),None)
                cap=next((r[v] for k,v in columns.items() if "nameplate capacity" in k),None)
                # Preserve date fields verbatim; a status switch is not itself a commissioning date.
                date_fields={str(k): (None if pd.isna(r[v]) else str(r[v]))
                    for k,v in columns.items()
                    if ("operating" in k and ("month" in k or "year" in k))
                    or ("retirement" in k and ("month" in k or "year" in k))
                    or ("operation" in k and ("month" in k or "year" in k))}
                found.append({"year":year,"sheet":sheet,"plant_id":str(plant_id),
                    "source_date_fields":date_fields,
                    "generator_id":str(r[gc]),"reported_status":None if pd.isna(status) else str(status),
                    "fuel":None if pd.isna(fuel) else str(fuel),
                    "nameplate_mw":None if pd.isna(cap) else float(cap),
                    "reporting_sheet_is_operable":sheet.lower()=="operable"})
    return {"year":year,"plant_id":str(plant_id),"matching_generator_rows":len(found),
      "original_source":URL.format(year=year),"generator_records":found,"inspected_sheets":inspected_sheets,
      "no_matching_row_is_not_proof_of_nonexistence":True,
      "verified_electrical_connection":False}


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--year",type=int,required=True)
    p.add_argument("--plant-id",default="59047")
    p.add_argument("--generator-id",default=None)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    req=urllib.request.Request(URL.format(year=a.year),headers={"User-Agent":"research-eia860-generator-audit/1.0"})
    with urllib.request.urlopen(req,timeout=120) as r: raw=r.read()
    result=audit_zip(raw,a.year,a.plant_id)
    if a.generator_id is not None:
        result["requested_generator_id"]=a.generator_id
        result["generator_records"]=[x for x in result["generator_records"] if x["generator_id"].strip()==a.generator_id]
        result["matching_generator_rows"]=len(result["generator_records"])
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))


if __name__=="__main__":main()
