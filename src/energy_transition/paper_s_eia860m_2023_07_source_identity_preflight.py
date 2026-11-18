"""Fail-closed historical July 2023 EIA-860M schema/identity preflight.

This does not infer plant IDs, generator IDs, BA geography, net generation,
or operating availability from EIA-930A undocumented source rows.
Emits inspection and actual join only if unambiguous primary source columns.
"""
from __future__ import annotations
import argparse,hashlib,json,re
from pathlib import Path
import pandas as pd

def norm(s):
    return re.sub(r"[^a-z0-9]+"," ",str(s).lower()).strip()

def choose_column(cols,allowed):
    names=[c for c in cols if norm(c) in allowed]
    if len(names)!=1:raise ValueError(f"Expected one unambiguous column from {sorted(allowed)}, found {names}")
    return names[0]

def manifest_and_rows(workbook,roster,out):
    from openpyxl import load_workbook
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    wb=load_workbook(workbook,read_only=True,data_only=True)
    inspection=[]
    for sheet in wb:
        rows=sheet.iter_rows(min_row=1,max_row=min(sheet.max_row,20),values_only=True)
        for n,row in enumerate(rows,1):
            vals=[str(v) if v is not None else "" for v in row]
            inspection.append({"worksheet":sheet.title,"excel_row":n,
               "nonblank_first_45_cells":" | ".join(f"{i+1}:{v[:80]}" for i,v in enumerate(vals[:45]) if v)})
    pd.DataFrame(inspection).to_csv(out/"eia860m_2023_07_source_sheet_header_inspection.csv",index=False)
    # Find exact normalized labels; never guess which column denotes plant/generator.
    candidates=[]
    for sheet in wb:
        if "operat" not in sheet.title.lower():continue
        for n in range(1,min(sheet.max_row,16)+1):
            row=next(sheet.iter_rows(min_row=n,max_row=n,values_only=True))
            cols=[str(v).strip() if v is not None else "" for v in row]
            labelset=set(map(norm,cols))
            if any(x in labelset for x in ("plant code","plant id","eia plant code")) and any(
               x in labelset for x in ("generator id","generator id number")):
                candidates.append((sheet.title,n))
    if len(candidates)!=1:
        # Source download/schema evidence still saved, exact join not silently forced.
        status="SOURCE_SCHEMA_ONLY_JOIN_BLOCKED"
        matches=pd.DataFrame()
    else:
        sheet,header=candidates[0]
        df=pd.read_excel(workbook,sheet_name=sheet,header=header-1,dtype=str)
        pl=choose_column(df.columns,{"plant code","plant id","eia plant code"})
        gn=choose_column(df.columns,{"generator id","generator id number"})
        def cleanplant(x):
            if pd.isna(x):return ""
            s=str(x).strip()
            return s[:-2] if re.fullmatch(r"\\d+\\.0",s) else s
        df["plant_key"]=df[pl].map(cleanplant)
        df["gen_key"]=df[gn].fillna("").astype(str).str.strip()
        eligible=pd.read_csv(roster,dtype=str)
        needed={"sheet","ba_code","fuel","EIA_plant_id","EIA_generator_id",
                "EIA930A_plant_id","EIA930A_generator_id","operating_by_july_2023_candidate"}
        if not needed.issubset(eligible.columns):raise ValueError("EIA930A extracted provenance columns incomplete")
        # Use only source EIA plant and generator IDs, with explicit alternate pair
        # allowed only if the primary pair is absent.
        eligible=eligible[(eligible.sheet=="SCH 2")&(eligible.fuel=="solar")&
                          (eligible.ba_code.isin(["PSCO","WACM"]))].copy()
        eligible["plant_key"]=eligible.EIA_plant_id.combine_first(eligible.EIA930A_plant_id).map(cleanplant)
        eligible["gen_key"]=eligible.EIA_generator_id.combine_first(eligible.EIA930A_generator_id).fillna("").str.strip()
        eligible["id_present"]=eligible.plant_key.ne("")&eligible.gen_key.ne("")
        assert len(eligible)==136
        assert len(eligible.loc[(eligible.ba_code=="WACM")&(~eligible.id_present)])==15
        df=df.loc[df.plant_key.ne("") & df.gen_key.ne("")].copy()
        if df[["plant_key","gen_key"]].duplicated().any():
            duplicate=df.loc[df[["plant_key","gen_key"]].duplicated(keep=False)]
            duplicate.head(100).to_csv(out/"EIA860M_SOURCE_DUPLICATE_KEY_SAMPLE.csv",index=False)
            raise ValueError("Official operable source contains duplicate plant/gen keys; stop for review")
        # Match only source-identifiable rows, no inference. Record unmatched explicitly.
        matches=eligible.loc[eligible.id_present].merge(
            df,on=["plant_key","gen_key"],how="left",validate="many_to_one",
            indicator="official_EIA860M_key_match",suffixes=("_eia930a","_eia860m"))
        matches.to_csv(out/"eia860m_2023_07_PSCO_WACM_source_ID_join_candidates.csv",index=False)
        status="SOURCE_IDS_JOINED_SCHEMA_AUDIT_ONLY"
    manifest={"status":status,"source_month":"2023-07",
       "source_url":"https://www.eia.gov/electricity/data/eia860m/archive/xls/july_generator2023.xlsx",
       "source_file_sha256":hashlib.sha256(Path(workbook).read_bytes()).hexdigest(),
       "source_sheets":wb.sheetnames,
       "matching_worksheet_and_header_candidates":candidates,
       "source_roster_2023_july_active_fleet_confirmed":False,
       "WACM_IDless_15_joined":False,
       "BA_state_measured_capacity_factor_validated":False,
       "match_rows_if_schema_valid":len(matches)}
    (out/"EIA860M_2023_07_SOURCE_PREFLIGHT_MANIFEST.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print("PAPER_S_EIA860M_2023_07_SOURCE_PREFLIGHT",json.dumps(manifest))
    return manifest

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--workbook",required=True,type=Path)
    a.add_argument("--roster",required=True,type=Path)
    a.add_argument("--out",required=True,type=Path)
    x=a.parse_args()
    manifest_and_rows(x.workbook,x.roster,x.out)
if __name__=="__main__":main()
