"""Audit generator-level membership in 2024 EIA-930A BPAT Schedule 2.

Generator IDs are sourced from 2024 EIA-860 operating generator inventory;
EIA-923 Page 1 plant/fuel generation is never allocated to generators.
"""
import argparse,io,json,urllib.request,zipfile
from pathlib import Path
import pandas as pd
from .eia860_capacity import URL as EIA860_URL
EIA930A="https://www.eia.gov/electricity/930-content/EIA_930A_2024_with%20layout.xlsx"
def normalize(s):return s.astype("string").str.strip().str.replace(r"\.0$","",regex=True)
def compare(wind,gen,book):
    x=wind.copy();x["plant_id"]=normalize(x.plant_id)
    g=gen.copy();g["plant_id"]=normalize(g.plant_id);g["generator_id"]=normalize(g.generator_id)
    g=g[g.plant_id.isin(x.plant_id)&g.status.astype(str).str.upper().eq("OP")].copy()
    if g.duplicated(["plant_id","generator_id"]).any():raise ValueError("Duplicate EIA860 generator key")
    e=pd.read_excel(io.BytesIO(book),sheet_name="SCH 2")
    needed={"BA Code","EIA Plant ID","EIA Generator ID"}
    if needed-set(e):raise ValueError("Missing EIA930A SCH2 generator keys")
    e=e[e["BA Code"].astype(str).str.upper().eq("BPAT")].copy()
    e["plant_id"]=normalize(e["EIA Plant ID"]);e["generator_id"]=normalize(e["EIA Generator ID"])
    keys=e[["plant_id","generator_id"]].dropna().drop_duplicates()
    j=g.merge(keys.assign(in_bpat_sch2=True),on=["plant_id","generator_id"],how="left",validate="one_to_one")
    j["in_bpat_sch2"]=j.in_bpat_sch2.fillna(False)
    j["capacity_mw"]=pd.to_numeric(j.capacity_mw,errors="coerce")
    if j.capacity_mw.isna().any():raise ValueError("Missing EIA860 generator capacity")
    plants=j.groupby("plant_id").agg(operating_eia860_generators=("generator_id","count"),
       listed_bpat_sch2_generators=("in_bpat_sch2","sum"),
       operating_nameplate_mw=("capacity_mw","sum"),
       listed_nameplate_mw=("capacity_mw",lambda vals:float(vals[j.loc[vals.index,"in_bpat_sch2"]].sum()))).reset_index()
    plants= x[["plant_id","net_generation_mwh"]].merge(plants,on="plant_id",how="left")
    plants["plant_membership"]="not_in_sch2"
    plants.loc[plants.listed_bpat_sch2_generators.gt(0),"plant_membership"]="partial_or_all_sch2"
    plants.loc[plants.listed_bpat_sch2_generators.eq(plants.operating_eia860_generators)&plants.operating_eia860_generators.gt(0),"plant_membership"]="all_operating_generators_listed"
    summary={"plants":len(plants),"operating_generator_records":len(j),
       "listed_operating_generator_records":int(j.in_bpat_sch2.sum()),
       "full_generator_coverage_plants":int(plants.plant_membership.eq("all_operating_generators_listed").sum()),
       "partial_or_all_coverage_plants":int(plants.listed_bpat_sch2_generators.gt(0).sum()),
       "not_listed_plant_count":int(plants.plant_membership.eq("not_in_sch2").sum()),
       "caveat":"Plant EIA923 Page1 MWh cannot be allocated to individual EIA860 generators or Schedule2 listed generation."}
    return j,plants,summary
def main():
    p=argparse.ArgumentParser();p.add_argument("--wind",type=Path,required=True);p.add_argument("--output",type=Path,required=True)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
    req=lambda url:urllib.request.Request(url,headers={"User-Agent":"Energy-Transition-Analysis-PyPSA/1.0"})
    with urllib.request.urlopen(req(EIA930A),timeout=120) as r:book=r.read()
    with urllib.request.urlopen(req(EIA860_URL.format(year=2024)),timeout=120) as r:arc=r.read()
    from .eia860_capacity import read_operable_inventory
    gen=read_operable_inventory(arc,2024)
    j,plants,report=compare(pd.read_csv(a.wind,dtype={"plant_id":"string"}),gen,book)
    j.to_csv(a.output/"bpat_wind_generator_membership_2024.csv",index=False)
    plants.to_csv(a.output/"bpat_wind_plant_generator_coverage_2024.csv",index=False)
    (a.output/"provenance.json").write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2))
if __name__=="__main__":main()
