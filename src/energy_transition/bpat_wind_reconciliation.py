"""Source-explicit BPAT wind reconciliation; no forced EIA-923/EIA-930 equivalence."""
import argparse
import json
from pathlib import Path
import pandas as pd


def reconcile(plant_month: pd.DataFrame, plant_ba: pd.DataFrame, hourly: pd.DataFrame, year: int = 2024):
    required = (("plant_month", plant_month, {"plant_id","report_year","fuel","net_generation_mwh"}),
                ("plant_ba", plant_ba, {"plant_id","ba_code","mapping_year"}),
                ("hourly", hourly, {"period","respondent","type","value"}))
    for name, frame, columns in required:
        if columns - set(frame):
            raise ValueError(f"{name} missing columns: {sorted(columns-set(frame))}")
    pm=plant_month.copy()
    cw=plant_ba.copy()
    h=hourly.copy()
    pm["report_year"]=pd.to_numeric(pm.report_year,errors="raise")
    cw["mapping_year"]=pd.to_numeric(cw.mapping_year,errors="raise")
    if not pm.report_year.eq(year).all() or not cw.mapping_year.eq(year).all():
        raise ValueError("EIA-923 and EIA-860 vintages must match the target year")
    for f in (pm,cw):
        f["plant_id"]=f.plant_id.astype("string").str.strip().str.replace(r"\\.0$","",regex=True)
        if f.plant_id.isna().any() or f.plant_id.eq("").any():
            raise ValueError("Missing plant ID")
    if cw.duplicated("plant_id").any():
        raise ValueError("Ambiguous or repeated plant crosswalk rows")
    pm["net_generation_mwh"]=pd.to_numeric(pm.net_generation_mwh,errors="raise")
    if not pm.net_generation_mwh.map(lambda v: pd.notna(v) and abs(v)!=float("inf")).all():
        raise ValueError("Nonfinite plant generation")
    wind=pm.loc[pm.fuel.astype("string").str.strip().str.lower().isin(["wind","wnd"])].copy()
    if wind.empty: raise ValueError("No wind observations; check harmonized fuel labels")
    cw["ba_code"]=cw.ba_code.astype("string").str.strip().str.upper()
    joined=wind.merge(cw[["plant_id","ba_code"]],on="plant_id",how="left",validate="many_to_one",indicator=True)
    plant_totals=joined.groupby(["plant_id","ba_code"],dropna=False,as_index=False).net_generation_mwh.sum()
    bpat=joined.loc[joined.ba_code.eq("BPAT")]
    unmatched=joined.loc[joined._merge.eq("left_only")]
    reassigned=joined.loc[joined.ba_code.notna() & ~joined.ba_code.eq("BPAT")]
    h["period"]=pd.to_datetime(h.period,utc=True,errors="raise")
    h["value"]=pd.to_numeric(h.value,errors="raise")
    observed=h.loc[h.respondent.astype("string").str.upper().eq("BPAT") & h.type.astype("string").str.upper().eq("WND")]
    observed=observed.loc[observed.period.dt.year.eq(year)]
    if observed.period.duplicated().any():raise ValueError("Duplicate BPAT WND hourly timestamps")
    expected=len(pd.date_range(f"{year}-01-01",f"{year+1}-01-01",freq="h",inclusive="left",tz="UTC"))
    if observed.empty:raise ValueError("No BPAT EIA-930 WND observations")
    if observed.value.isna().any():raise ValueError("Null BPAT WND observations; report coverage separately")
    result={
        "year":year,"eia923_bpat_wind_mwh":float(bpat.net_generation_mwh.sum()),
        "eia923_unmatched_wind_mwh":float(unmatched.net_generation_mwh.sum()),
        "eia923_other_ba_wind_mwh":float(reassigned.net_generation_mwh.sum()),
        "eia923_bpat_plant_count":int(bpat.plant_id.nunique()),
        "eia923_unmatched_plant_count":int(unmatched.plant_id.nunique()),
        "eia930_bpat_wnd_mwh":float(observed.value.sum()),
        "eia930_observed_hours":len(observed),"expected_hours":expected,
        "eia930_coverage_complete":bool(len(observed)==expected),
        "signed_difference_eia923_minus_eia930_mwh":float(bpat.net_generation_mwh.sum()-observed.value.sum()),
        "caution":"Unmatched and other-BA plant totals are diagnostics, not proven explanations of the signed difference."
    }
    return result,plant_totals


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--plant-month",type=Path,required=True)
    p.add_argument("--plant-ba",type=Path,required=True)
    p.add_argument("--hourly",type=Path,required=True)
    p.add_argument("--year",type=int,default=2024)
    p.add_argument("--output",type=Path,default=Path("outputs/bpat_wind_reconciliation"))
    a=p.parse_args()
    result,plants=reconcile(pd.read_csv(a.plant_month),pd.read_csv(a.plant_ba),pd.read_csv(a.hourly),a.year)
    a.output.mkdir(parents=True,exist_ok=True)
    plants.to_csv(a.output/"wind_plant_ba_totals.csv",index=False)
    (a.output/"reconciliation.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))


if __name__=="__main__":main()
