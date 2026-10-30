"""Use EIA's 2024 EIA-930A plant/generator population crosswalk."""
import argparse,io,json,urllib.request
from pathlib import Path
import pandas as pd
URL="https://www.eia.gov/electricity/930-content/EIA_930A_2024_with%20layout.xlsx"
def audit(wind,book):
    x=wind.copy();x["plant_id"]=x.plant_id.astype("string").str.strip()
    excel=pd.ExcelFile(io.BytesIO(book))
    matches=[]
    schema=[]
    for sheet in excel.sheet_names:
        for header in (0,1,2,3):
            d=pd.read_excel(excel,sheet_name=sheet,header=header)
            names={str(c).strip().lower().replace("\n"," "):c for c in d.columns}
            pid=next((v for k,v in names.items() if k in ("eia plant id","plant id (eia-930a)","plant id")),None)
            ba=next((v for k,v in names.items() if k=="ba code" or ("balancing authority" in k and "code" in k)),None)
            if pid and ba:
                schema.append({"sheet":sheet,"header":header,"plant_col":str(pid),"ba_col":str(ba),"rows":len(d)})
                sub=d[[pid,ba]].copy();sub.columns=["plant_id","eia930a_ba"]
                sub["plant_id"]=sub.plant_id.astype("string").str.strip().str.replace(r"\.0$","",regex=True)
                sub["eia930a_ba"]=sub.eia930a_ba.astype("string").str.strip().str.upper()
                matches.append(sub.dropna().drop_duplicates())
                break
    if not matches:raise ValueError("Unrecognized official EIA930A sheets: "+str([(s,list(pd.read_excel(excel,sheet_name=s,nrows=3).columns)) for s in excel.sheet_names]))
    cross=pd.concat(matches,ignore_index=True).drop_duplicates()
    bpat=cross[cross.eia930a_ba.eq("BPAT")]
    ids=set(bpat.plant_id)
    x["in_eia930a_bpat_population"]=x.plant_id.isin(ids)
    x["in_any_eia930a_population"]=x.plant_id.isin(set(cross.plant_id))
    summary={"source_url":URL,"sheet_schemas":schema,"bpat_wind_plants":len(x),
      "in_eia930a_bpat":int(x.in_eia930a_bpat_population.sum()),
      "not_in_eia930a_bpat":int((~x.in_eia930a_bpat_population).sum()),
      "listed_bpat_wind_qualified_mwh":float(x.loc[x.in_eia930a_bpat_population,"net_generation_mwh"].sum()),
      "unlisted_bpat_wind_qualified_mwh":float(x.loc[~x.in_eia930a_bpat_population,"net_generation_mwh"].sum()),
      "limitation":"EIA930A plant population membership does not identify which share of plant generation entered hourly BPAT WND net generation."}
    return x,summary
def main():
    p=argparse.ArgumentParser();p.add_argument("--wind",type=Path,required=True);p.add_argument("--output",type=Path,required=True)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
    req=urllib.request.Request(URL,headers={"User-Agent":"Mozilla/5.0"})
    with urllib.request.urlopen(req,timeout=120) as r:book=r.read()
    x,s=audit(pd.read_csv(a.wind,dtype={"plant_id":"string"}),book)
    x.to_csv(a.output/"bpat_wind_eia930a_population_audit.csv",index=False)
    (a.output/"provenance.json").write_text(json.dumps(s,indent=2))
    print(json.dumps(s,indent=2))
if __name__=="__main__":main()
