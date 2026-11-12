"""Fail-closed audit of native 2007–2021 ReEDS county wind/PV hourly calendars.

No ordinal year alignment is authorized by this audit. Read original
publisher HDF5 index_0, validate each year independently and compare
wind vs PV at source. These point samples are NOT hour-integrated output.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
import h5py
import numpy as np
import pandas as pd
from energy_transition.reeds2022_county_state_resources import WIND_COUNTY_MD5,PV_COUNTY_MD5
from energy_transition.reeds2022_real_resource_intake import require_md5,decode

YEARS=tuple(range(2007,2022))
HOURS=8760

def calendar_audit(index,tech):
    labels=decode(index)
    t=pd.DatetimeIndex(pd.to_datetime(labels,errors="raise"))
    if t.isna().any() or t.has_duplicates or not t.is_monotonic_increasing:
        raise ValueError("Duplicate, unparseable or unordered original time labels")
    result=[]
    for y in YEARS:
        where=np.flatnonzero(t.year==y)
        if not len(where):raise ValueError(f"Original source missing year {y}")
        native=t[where]
        observed=8760 if len(native)==HOURS else len(native)
        hourly_gaps=np.flatnonzero((native[1:]-native[:-1])!=pd.Timedelta(hours=1))
        theoretical=pd.date_range(f"{y}-01-01",f"{y+1}-01-01",freq="h",inclusive="left",tz=t.tz)
        missing=theoretical.difference(native)
        extraneous=native.difference(theoretical)
        if len(extraneous):raise ValueError("Unexpected out-of-year original source dates")
        if len(hourly_gaps):raise ValueError(f"Non-hourly gap within source year {y}: {len(hourly_gaps)}")
        result.append({
            "technology":tech,"weather_year":y,
            "source_row_count":observed,
            "full_standard_calendar_hour_count":len(theoretical),
            "source_year_first":str(native[0]),"source_year_last":str(native[-1]),
            "is_exact_conventional_calendar":bool(len(missing)==0 and not len(hourly_gaps)),
            "is_8760_source_reference":bool(len(native)==8760),
            "missing_conventional_calendar_hours":len(missing),
            "missing_feb29_source_hours":int(sum(x.month==2 and x.day==29 for x in missing)),
            "missing_dec31_source_hours":int(sum(x.month==12 and x.day==31 for x in missing)),
            "missing_calendar_first":str(missing[0]) if len(missing) else None,
            "missing_calendar_last":str(missing[-1]) if len(missing) else None,
            "within_year_nonhourly_gap_count":len(hourly_gaps),
            "native_source_timezone":str(t.tz) if t.tz is not None else "naive (publisher fixed CST)",
            "hour_energy_integral_verified":False,
            "ordinal_8760_join_to_2030_demand_validated":False})
    if len(result)!=len(YEARS):raise ValueError("Incomplete source calendar audit")
    return t,pd.DataFrame(result)

def compare_indexes(wind,pv):
    wt,ws=calendar_audit(wind,"wind")
    pt,ps=calendar_audit(pv,"pv")
    if not wt.equals(pt):
        i=np.flatnonzero(np.asarray(wt)!=np.asarray(pt))
        raise ValueError(f"Original wind and PV weather clocks disagree, first indices={i[:10]}")
    if len(wt)!=15*8760:
        raise ValueError("Original release is not 15×8760 reference records")
    if not ws.source_row_count.eq(HOURS).all() or not ps.source_row_count.eq(HOURS).all():
        raise ValueError("Original years do not all provide exactly 8760 samples")
    if not ws.is_8760_source_reference.all():
        raise ValueError("Original weather calendars do not support 8760 ordinal models")
    return ws,ps

def run(wind_h5,pv_h5,out):
    require_md5(wind_h5,WIND_COUNTY_MD5)
    require_md5(pv_h5,PV_COUNTY_MD5)
    with h5py.File(wind_h5,"r") as w,h5py.File(pv_h5,"r") as p:
        ws,ps=compare_indexes(w["index_0"][:],p["index_0"][:])
    o=Path(out);o.mkdir(parents=True,exist_ok=True)
    df=pd.concat([ws,ps],ignore_index=True)
    df.to_csv(o/"paper_s_reeds2022_2007_2021_wind_pv_native_calendar_30_audit.csv",index=False)
    source=ws[ws.weather_year.eq(2012)].iloc[0]
    if source.missing_dec31_source_hours!=24 or source.missing_feb29_source_hours!=0:
        raise ValueError("Known 2012 leap year source boundary contract changed")
    candidate=ws[(ws.is_exact_conventional_calendar)&(ws.weather_year!=2012)].weather_year.tolist()
    manifest={
      "status":"ORIGINAL_REEDS_WIND_PV_2007_2021_SOURCE_NATIVE_CALENDAR_VERIFIED",
      "source_wind_md5":WIND_COUNTY_MD5,"source_pv_md5":PV_COUNTY_MD5,
      "native_clocks_identical":True,"audited_weather_years":list(YEARS),
      "wind_pv_calendar_rows":len(df),
      "source_2012_missing_dec31_hours":24,
      "conventional_full_calendar_candidate_years":candidate,
      "publisher_weather_CF_are_instantaneous_not_integrated":True,
      "native_same_instant_not_physical_hour_ending_equivalence":True,
      "projected_demand_2030_timestamps_joined":False,
      "LPs_solved":0,
      "weather_year_sensitivity_tested":False,
      "further_step_requires_explicit_calendar_mapping_and_original_class_CFs":True}
    (o/"paper_s_reeds2022_2007_2021_source_calendar_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print(df[["technology","weather_year","source_row_count","is_exact_conventional_calendar",
        "missing_conventional_calendar_hours","missing_feb29_source_hours",
        "missing_dec31_source_hours","within_year_nonhourly_gap_count"]].to_string(index=False))
    print(json.dumps(manifest,indent=2))
    print("PAPER_S_REEDS_15_WEATHER_YEAR_CLOCK_AUDIT_PASS")
    return df,manifest

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--wind-h5",required=True,type=Path)
    p.add_argument("--pv-h5",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()
    run(a.wind_h5,a.pv_h5,a.out)

if __name__=="__main__":main()
