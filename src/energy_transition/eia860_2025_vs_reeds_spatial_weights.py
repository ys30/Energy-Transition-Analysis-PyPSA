"""EIA-860 2025 real operating wind/PV county capacity versus ReEDS potential.

Strictly join EIA Plant and Operable Generator from the official annual
ZIP by Plant Code, retaining only status OP and fuel/prime-mover matching
wind WT/WND or photovoltaic PV/SUN. The EIA published Form 860 reports
generator nameplate MW in AC terms; ReEDS published solar potential MW_DC
is never added to wind MW_AC. County names are joined by state to Census
2020 national county FIPS codes; no fuzzy/geocoding or undocumented
split of plants straddling counties. 2025 observed sites are NOT a 2030
fleet nor proof that original 2012 HDF5 weather CF represents the plants.
"""
from __future__ import annotations
import argparse,hashlib,io,json,re,zipfile
from pathlib import Path
import numpy as np
import pandas as pd
from energy_transition.reeds2022_county_state_resources import (
    STATES,parse_county_columns,WIND_COUNTY_CAPACITY_MD5,PV_COUNTY_CAPACITY_MD5,
)
from energy_transition.reeds2022_real_resource_intake import require_md5

YEARS=(2025,2020)
EIA_ZIP="https://www.eia.gov/electricity/data/eia860/xls/eia8602025.zip"
CENSUS_COUNTY="https://www2.census.gov/geo/docs/reference/codes2020/national_county2020.txt"
TECHS={"wind":("WT","WND"),"pv":("PV","SUN")}
FILES={"plant":re.compile(r"(?i)(?:^|/)[^/]*Plant[^/]*2025\.xlsx$"),
       "operable":re.compile(r"(?i)(?:^|/)3[_ ]*1[_ ]*Generator[^/]*2025\.xlsx$")}
FIELDS_PLANT=("Plant Code","State","County")
FIELDS_GEN=("Plant Code","State","County","Generator ID","Status","Prime Mover",
            "Energy Source 1","Nameplate Capacity (MW)")
FIPS={"AZ":"04","CO":"08","ID":"16","WY":"56"}
DIGEST={"wind":WIND_COUNTY_CAPACITY_MD5,"pv":PV_COUNTY_CAPACITY_MD5}

def norm_county(s):
    if pd.isna(s):return ""
    x=re.sub(r"[^a-z0-9]","",str(s).casefold().replace(" county",""))
    return x

def sheet_from_archive(archive,category,sheet):
    names=[x for x in archive.namelist() if not x.endswith("/")]
    match=[x for x in names if FILES[category].search(x)]
    if len(match)!=1:raise ValueError(f"Exactly one {category} required: {match}; names={names[:40]}")
    return pd.read_excel(io.BytesIO(archive.read(match[0])),sheet_name=sheet,dtype={"Plant Code":"string","Generator ID":"string"})

def census_map(path):
    c=pd.read_csv(path,sep="|",dtype=str)
    needed={"STATE","STATEFP","COUNTYFP","COUNTYNAME"}
    if not needed.issubset(c.columns):raise ValueError("Wrong official Census county codes format")
    c=c[c.STATE.isin(FIPS)].copy()
    if (c.STATEFP!=c.STATE.map(FIPS)).any():raise ValueError("Census state FIPS disagree")
    c["county_norm"]=c.COUNTYNAME.map(norm_county)
    if c.duplicated(["STATE","county_norm"]).any() or (c.county_norm=="").any():
        raise ValueError("Census county names are ambiguous under exact punctuation normalization")
    c["county_fips"]=c.STATEFP+c.COUNTYFP
    if not c.county_fips.str.fullmatch(r"\d{5}").all():raise ValueError("Bad county FIPS")
    return c[["STATE","county_norm","county_fips"]].rename(columns={"STATE":"state"})

def get_fleet(zip_file,census_file):
    with zipfile.ZipFile(zip_file) as z:
        p=sheet_from_archive(z,"plant","Plant")
        g=sheet_from_archive(z,"operable","Operable")
    if not set(FIELDS_PLANT).issubset(p.columns) or not set(FIELDS_GEN).issubset(g.columns):
        raise ValueError("Original EIA plant or operable generator columns changed")
    p=p[list(FIELDS_PLANT)].copy()
    g=g[list(FIELDS_GEN)].copy()
    for d in (p,g):
        d["Plant Code"]=pd.to_numeric(d["Plant Code"],errors="raise").astype("Int64")
        d["State"]=d["State"].astype("string").str.strip()
    if p["Plant Code"].isna().any() or p["Plant Code"].duplicated().any():
        raise ValueError("Plant Code must uniquely identify one plant in official EIA release")
    g=g[g.State.isin(FIPS)].copy()
    g=g[g.Status.astype("string").str.strip().eq("OP")].copy()
    g["Nameplate Capacity (MW)"]=pd.to_numeric(g["Nameplate Capacity (MW)"],errors="raise")
    if not np.isfinite(g["Nameplate Capacity (MW)"].to_numpy(float)).all() or (g["Nameplate Capacity (MW)"]<0).any():
        raise ValueError("Invalid EIA generator nameplate MW")
    g["technology"]=None
    for tech,(prime,fuel) in TECHS.items():
        mask=g["Prime Mover"].astype("string").str.strip().eq(prime)&g["Energy Source 1"].astype("string").str.strip().eq(fuel)
        g.loc[mask,"technology"]=tech
    g=g[g.technology.notna() & g["Nameplate Capacity (MW)"].gt(0)].copy()
    if g.empty:raise ValueError("No official operating 2025 wind and PV generators")
    if g.duplicated(["Plant Code","Generator ID"]).any():
        raise ValueError("Generator record duplicates within operating sheet")
    m=g.merge(p,on="Plant Code",how="left",validate="many_to_one",suffixes=("_gen","_plant"),indicator=True)
    if not m._merge.eq("both").all():raise ValueError("EIA plant missing for generator")
    if not m.State_gen.eq(m.State_plant).all():raise ValueError("EIA plant/generator state disagreement")
    gn=m.County_gen.map(norm_county)
    pn=m.County_plant.map(norm_county)
    # Do not silently swap diverging generator and plant geographies.
    conflicts=gn.ne("") & pn.ne("") & gn.ne(pn)
    if conflicts.any():raise ValueError("Plant and generator county labels conflict")
    m["state"]=m.State_plant
    m["county_raw"]=m.County_plant.fillna(m.County_gen)
    m["county_norm"]=m.county_raw.map(norm_county)
    m=m.merge(census_map(census_file),on=["state","county_norm"],how="left",
              validate="many_to_one",indicator="county_merge")
    m["nameplate_mw_ac"]=m["Nameplate Capacity (MW)"].astype(float)
    m["geographic_mapping_found"]=m.county_fips.notna()
    return m

def source_potential(path,tech):
    require_md5(path,DIGEST[tech])
    p=pd.read_csv(path,dtype=str)
    if list(p.columns)!=["class|region","MW"]:raise ValueError("Source supply curve schema mismatch")
    keys=parse_county_columns(p["class|region"].tolist())
    cap=pd.to_numeric(p["MW"],errors="raise")
    if len(cap)!=len(keys) or cap.isna().any() or (cap<0).any():
        raise ValueError("Invalid original source MW")
    keys["source_potential_mw_original_basis"]=cap.to_numpy(float)
    keys["technology"]=tech
    keys["state"]=keys.state_fips.map({v:k for k,v in FIPS.items()})
    return keys[keys.state.notna()].groupby(["state","technology","county_fips"],as_index=False)["source_potential_mw_original_basis"].sum()

def contrast(fleet,potential):
    counts=fleet.groupby(["state","technology"]).size().rename("generator_count")
    rows=[];geo=[]
    for state in FIPS:
        for tech in TECHS:
            x=fleet[fleet.state.eq(state)&fleet.technology.eq(tech)]
            y=potential[potential.state.eq(state)&potential.technology.eq(tech)]
            if y.empty:raise ValueError("Missing potential for state/tech")
            installed_total=float(x.nameplate_mw_ac.sum())
            mapped=x[x.geographic_mapping_found]
            mapped_total=float(mapped.nameplate_mw_ac.sum())
            if installed_total<=0:
                rows.append({"state":state,"technology":tech,
                            "observed_2025_generator_count":0,
                            "observed_2025_total_nameplate_ac_mw":0.,
                            "county_mapping_capacity_coverage":np.nan,
                            "fleet_to_potential_total_variation":np.nan,
                            "relative_effective_county_ratio":np.nan,
                            "diagnostic_state":"NO_REPORTED_OPERATING_GENERATORS"})
                continue
            a=mapped.groupby("county_fips").nameplate_mw_ac.sum()
            b=y.groupby("county_fips").source_potential_mw_original_basis.sum()
            both=pd.DataFrame(index=a.index.union(b.index))
            both["eia2025_ac_nameplate_mw"]=a.reindex(both.index).fillna(0)
            both["reeds2022_source_potential_mw_original_basis"]=b.reindex(both.index).fillna(0)
            both["eia2025_share_among_geocoded"]=both.eia2025_ac_nameplate_mw/mapped_total if mapped_total else 0.
            both["reeds2022_potential_share"]=both.reeds2022_source_potential_mw_original_basis/b.sum()
            both["state"]=state;both["technology"]=tech;both["county_fips"]=both.index
            geo.append(both.reset_index(drop=True))
            dist=float(.5*np.abs(both.eia2025_share_among_geocoded-both.reeds2022_potential_share).sum()) if mapped_total else np.nan
            h_eia=float(np.square(both.eia2025_share_among_geocoded).sum()) if mapped_total else np.nan
            h_reeds=float(np.square(both.reeds2022_potential_share).sum())
            rows.append({"state":state,"technology":tech,
                        "observed_2025_generator_count":len(x),
                        "observed_2025_total_nameplate_ac_mw":installed_total,
                        "mapped_2025_nameplate_ac_mw":mapped_total,
                        "county_mapping_capacity_coverage":mapped_total/installed_total,
                        "observed_2025_mapped_counties":int((both.eia2025_ac_nameplate_mw>0).sum()),
                        "reeds2022_positive_potential_counties":int((both.reeds2022_source_potential_mw_original_basis>0).sum()),
                        "observed_2025_fleet_effective_counties":1/h_eia if h_eia>0 else np.nan,
                        "source_potential_effective_counties":1/h_reeds,
                        "fleet_to_potential_total_variation":dist,
                        "eia_fleet_capacity_in_zero_reeds_potential_counties_fraction":float(
                           both.loc[both.reeds2022_source_potential_mw_original_basis.eq(0),"eia2025_ac_nameplate_mw"].sum()/installed_total),
                        "diagnostic_state":"DESCRIPTIVE_2025_OPERATING_FLEET_NOT_2030_BUILDOUT"})
    return pd.DataFrame(rows),pd.concat(geo,ignore_index=True)

def run(annual_zip,census_file,wind_sc,pv_sc,out):
    eia=get_fleet(annual_zip,census_file)
    potential=pd.concat([source_potential(wind_sc,"wind"),source_potential(pv_sc,"pv")],ignore_index=True)
    stats,county=contrast(eia,potential)
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    stats.to_csv(out/"paper_s_eia860_2025_vs_reeds_county_spatial_weight_8_summary.csv",index=False)
    county.to_csv(out/"paper_s_eia860_2025_vs_reeds_county_spatial_weights.csv",index=False)
    unmatched=eia[~eia.geographic_mapping_found][["Plant Code","Generator ID","state","county_raw","technology","nameplate_mw_ac"]]
    unmatched.to_csv(out/"paper_s_eia860_2025_unmatched_county_geographies.csv",index=False)
    coverage=stats.county_mapping_capacity_coverage.dropna()
    manifest={
        "status":"OBSERVED_2025_OPERATING_WIND_PV_EIA860_COUNTY_WEIGHTS_VS_REEDS_RESOURCE_POTENTIAL",
        "EIA_860_publisher":EIA_ZIP,
        "EIA_zip_observed_sha256":hashlib.sha256(Path(annual_zip).read_bytes()).hexdigest(),
        "Census_county_2020_crosswalk_source":CENSUS_COUNTY,
        "Census_county_crosswalk_observed_sha256":hashlib.sha256(Path(census_file).read_bytes()).hexdigest(),
        "EIA_generator_filter":"Operable sheet, Status OP, WT/WND wind or PV/SUN solar",
        "EIA_nameplate_mw":"form-reported AC, grouped within wind or solar only",
        "ReEDS_resource_potential_mw":"wind AC; solar DC; never sum across technology",
        "all_fleet_counties_mapped":bool(eia.geographic_mapping_found.all()),
        "min_positive_fleet_geocoded_capacity_fraction":float(coverage.min()) if len(coverage) else None,
        "this_is_2025_not_forecast_2030":True,
        "2025_source_weather_generation_reproduced":False,
        "2012_hourly_source_integral_validated":False,
        "LPs_solved":0,
        "only_potential_vs_observed_capacity_spatial_weights_compared":True,
        "source_and_year_mismatch_explicit":True}
    (out/"paper_s_eia860_2025_vs_reeds_spatial_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print(stats.to_string(index=False))
    print("EIA860_2025_OPERATING_FLEET_COUNTY_WEIGHTS_VS_REEDS_POTENTIAL_AUDITED")
    return stats,county,manifest

def main():
    p=argparse.ArgumentParser()
    for name in ("annual_zip","census_file","wind_sc","pv_sc"):
        p.add_argument("--"+name.replace("_","-"),type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    x=p.parse_args()
    run(x.annual_zip,x.census_file,x.wind_sc,x.pv_sc,x.out)

if __name__=="__main__":
    main()
