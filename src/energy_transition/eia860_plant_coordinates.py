"""Extract official EIA-860 plant coordinates without assigning electrical buses."""
import argparse,io,json,urllib.request,zipfile
from pathlib import Path
import pandas as pd
from .eia860_capacity import URL,WESTERN_STATES
from .ba_crosswalk import normalize_plant_id

def extract(raw):
 with zipfile.ZipFile(io.BytesIO(raw)) as z:
  candidates=[x for x in z.namelist() if Path(x).name.lower().startswith("2_") and "plant" in Path(x).name.lower() and x.lower().endswith((".xlsx",".xls"))]
  if not candidates:raise ValueError("Official 2_Plant workbook absent")
  book=pd.ExcelFile(io.BytesIO(z.read(candidates[0])))
  for sheet in book.sheet_names:
   for h in (1,0,2):
    d=pd.read_excel(book,sheet_name=sheet,header=h)
    cols={str(x).strip().lower():x for x in d.columns}
    plant=next((v for k,v in cols.items() if k in ("plant code","plant id","plant id number")),None)
    state=cols.get("state")
    lat=next((v for k,v in cols.items() if k=="latitude" or k.startswith("latitude ")),None)
    lon=next((v for k,v in cols.items() if k=="longitude" or k.startswith("longitude ")),None)
    if all(v is not None for v in (plant,state,lat,lon)):
     name=next((v for k,v in cols.items() if k in ("plant name","plant name (nameplate)")),None)
     selected=[plant,state,lat,lon]+([name] if name is not None else [])
     out=d[selected].copy()
     out.columns=["plant_id","state","latitude","longitude"]+(["plant_name"] if name is not None else [])
     if "plant_name" not in out:
      out["plant_name"]=pd.NA
     out["plant_name"]=out.plant_name.astype("string").str.strip()
     out.plant_id=normalize_plant_id(out.plant_id)
     out.state=out.state.astype("string").str.strip().str.upper()
     out=out[out.state.isin(WESTERN_STATES)].copy()
     out.latitude=pd.to_numeric(out.latitude,errors="coerce")
     out.longitude=pd.to_numeric(out.longitude,errors="coerce")
     out["coordinate_qc"]="valid"
     invalid=~(out.latitude.between(25,50)&out.longitude.between(-125,-102))
     out.loc[invalid,"coordinate_qc"]="missing_or_outside_screen"
     if out.empty:raise ValueError("No Western EIA plant rows")
     if out.plant_id.isna().any():raise ValueError("Missing plant IDs in position extract")
     if out.duplicated("plant_id").any():raise ValueError("Duplicate official plant IDs: review EIA source")
     return out,{"plant_workbook":candidates[0],"sheet":sheet,"header_row":h}
 raise ValueError("EIA plant latitude/longitude columns not found; inspect workbook schema")

def main():
 p=argparse.ArgumentParser();p.add_argument("--year",type=int,required=True)
 p.add_argument("--out-dir",type=Path,required=True)
 a=p.parse_args();a.out_dir.mkdir(parents=True,exist_ok=True)
 url=URL.format(year=a.year)
 req=urllib.request.Request(url,headers={"User-Agent":"energy-transition-research/0.2"})
 with urllib.request.urlopen(req,timeout=120) as resp:raw=resp.read()
 d,details=extract(raw)
 d.to_csv(a.out_dir/f"official_eia860_plant_coordinates_{a.year}.csv",index=False)
 report={"year":a.year,"source_url":url,"source_details":details,
   "official_plant_rows":len(d),"valid_geographic_coordinates":int(d.coordinate_qc.eq("valid").sum()),
   "invalid_geographic_coordinates":int(d.coordinate_qc.ne("valid").sum()),
   "electrical_bus_mapping_verified":False,
   "coordinate_crs_authoritatively_verified":False}
 (a.out_dir/f"official_eia860_plant_coordinates_{a.year}.json").write_text(json.dumps(report,indent=2)+"\n")
 print(json.dumps(report,indent=2))
if __name__=="__main__":main()
