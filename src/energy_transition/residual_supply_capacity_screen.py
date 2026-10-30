"""Audit assumed one-bus firm/peaker power against 2024 EIA-860 BA nameplate.

This is a capacity *screen*, NOT historical calibration, firm-capacity credit,
generator commitment, or deliverability evidence.
"""
import argparse,json
from pathlib import Path
import pandas as pd

THERMAL={"NG","OG","PG","SG","BFG","BIT","SUB","LIG","RC","WC","DFO","RFO","JF","KER","PC","WO","NUC"}
HYDRO={"WAT"}
GEO={"GEO"}
VARIABLE={"SUN","WND"}
STORAGE={"MWH","PUR"}

def audit(source,bas=("CISO","BPAT"),firm_mw=55000.,peaker_mw=20000.):
    required={"ba_code","fuel","capacity_mw"}
    if missing:=required-set(source):raise ValueError(f"Missing source columns: {sorted(missing)}")
    d=source[source.ba_code.isin(bas)].copy()
    if set(d.ba_code)!=set(bas):raise ValueError("One or more requested BAs absent")
    if d.duplicated(["ba_code","fuel"]).any():raise ValueError("Duplicate BA/fuel sums")
    d["capacity_mw"]=pd.to_numeric(d.capacity_mw,errors="coerce")
    if d.capacity_mw.isna().any() or d.capacity_mw.lt(0).any():raise ValueError("Invalid capacity")
    d["capacity_class"]=d.fuel.map(lambda f:"thermal_nuclear" if f in THERMAL else
       "hydro" if f in HYDRO else "geothermal" if f in GEO else
       "variable_wind_solar" if f in VARIABLE else "storage" if f in STORAGE else "other")
    grouped=d.groupby("capacity_class").capacity_mw.sum().to_dict()
    thermal=grouped.get("thermal_nuclear",0.)
    broad=thermal+grouped.get("hydro",0.)+grouped.get("geothermal",0.)
    assumed=firm_mw+peaker_mw
    summary={"bas":list(bas),"thermal_nuclear_nameplate_mw":thermal,
      "thermal_nuclear_hydro_geo_nameplate_mw":broad,
      "wind_solar_nameplate_mw":grouped.get("variable_wind_solar",0.),
      "assumed_firm_nameplate_mw":firm_mw,"assumed_peaker_nameplate_mw":peaker_mw,
      "assumed_dispatchable_supply_mw":assumed,
      "assumed_minus_thermal_nuclear_mw":assumed-thermal,
      "assumed_minus_thermal_nuclear_hydro_geo_mw":assumed-broad,
      "capacity_calibrated":False,
      "interpretation":"Thermal-only and thermal+hydro+geothermal are NAMEPLATE screening bounds, NOT actual hourly dependable capacity. Firm and peaker cannot be identified from nameplate fuel alone. Supported fuel categories omit some EIA-860 assets. Separate realized BA solar/wind must not be counted twice."}
    return d,summary

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
    detail,report=audit(pd.read_csv(a.input))
    detail.to_csv(a.output/"eia860_ba_capacity_classification.csv",index=False)
    (a.output/"residual_supply_capacity_screen.json").write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2))
if __name__=="__main__":main()
