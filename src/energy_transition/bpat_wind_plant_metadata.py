"""Enrich audited BPAT wind plant identifiers with official 2024 EIA-860 plant metadata."""
import argparse,io,json,zipfile,urllib.request
from pathlib import Path
import pandas as pd
from .eia860_capacity import URL

def enrich(wind,archive):
    with zipfile.ZipFile(io.BytesIO(archive)) as z:
        matches=[n for n in z.namelist() if Path(n).name.lower().startswith("2_") and "plant" in Path(n).name.lower() and n.lower().endswith((".xlsx",".xls"))]
        if len(matches)!=1:raise ValueError("Cannot uniquely locate official plant workbook")
        raw=z.read(matches[0])
    metadata=None
    for header in (1,0,2):
        d=pd.read_excel(io.BytesIO(raw),header=header)
        names={str(k).strip().lower():k for k in d.columns}
        def choose(*terms):
            return next((v for k,v in names.items() if any(t==k for t in terms)),None)
        plant=choose("plant code","plant id","plant id number")
        name=choose("plant name");state=choose("state")
        if plant and name and state:
            cols={"plant_id":plant,"plant_name":name,"state":state}
            for new,aliases in {"county":("county",),"operator":("operator name","utility name","entity name"),"ba_code":("balancing authority code",),"latitude":("latitude",),"longitude":("longitude",)}.items():
                v=choose(*aliases)
                if v is not None:cols[new]=v
            metadata=d[list(cols.values())].rename(columns={v:k for k,v in cols.items()})
            break
    if metadata is None:raise ValueError("Official 2024 plant name/state fields not found")
    metadata["plant_id"]=metadata.plant_id.astype("string").str.strip().str.replace(r"\.0$","",regex=True)
    if metadata.plant_id.duplicated().any():raise ValueError("Ambiguous official plant identifiers")
    w=wind.copy();w["plant_id"]=w.plant_id.astype("string").str.strip()
    joined=w.merge(metadata,on="plant_id",how="left",validate="many_to_one")
    missing=joined.plant_name.isna()
    report={"source":"2024 official EIA-860 2___Plant workbook",
      "wind_plants":len(joined),"metadata_matched":int((~missing).sum()),
      "metadata_unmatched":int(missing.sum()),
      "note":"Official plant metadata, not a claim these plants account for EIA-930 versus EIA-923 reported difference."}
    return joined,report

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--wind",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
    with urllib.request.urlopen(urllib.request.Request(URL.format(year=2024),headers={"User-Agent":"Energy-Transition-Analysis-PyPSA/1.0"}),timeout=120) as r:archive=r.read()
    result,report=enrich(pd.read_csv(a.wind,dtype={"plant_id":"string"}),archive)
    result.to_csv(a.output/"bpat_wind_official_plant_metadata_2024.csv",index=False)
    (a.output/"metadata_provenance.json").write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2))
    print(result.head(15).to_string(index=False))
if __name__=="__main__":main()
