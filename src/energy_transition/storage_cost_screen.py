"""Screen battery costs against observed-week modeled savings, without annualization.

These are conditional thresholds, NOT investment NPVs: observed 168-hour weeks
are unrepresentative, assumed operating savings omit battery degradation and
network limits. Investment parameters are user-adjustable scenarios.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import pandas as pd

CAPEX_USD_PER_KWH=(150.,250.,350.)
FOM_FRACTION=.04
LIFE_YEARS=15
DISCOUNT_RATE=.07

def capital_recovery_factor(rate, years):
    if years<=0 or rate<0:raise ValueError("Invalid finance assumptions")
    return 1/years if rate==0 else rate*(1+rate)**years/((1+rate)**years-1)

def screen(frame, capex=CAPEX_USD_PER_KWH, fom_fraction=FOM_FRACTION,
           years=LIFE_YEARS, rate=DISCOUNT_RATE):
    needed={"season","scenario","assumed_operating_savings_usd","unserved_with_battery_mwh",
            "unserved_without_battery_mwh"}
    if needed-set(frame):raise ValueError("Missing observed renewables storage results")
    if frame.duplicated(["season","scenario"]).any():raise ValueError("Duplicate seasonal scenario")
    if not capex or any(v<=0 for v in capex) or not (0<=fom_fraction<1):
        raise ValueError("Invalid cost scenario")
    crf=capital_recovery_factor(rate,years)
    rows=[]
    for _,r in frame.iterrows():
        for price in capex:
            investment=1_000_000*4*price # 1 GW / 4 GWh as modeled
            annual_fixed=investment*(crf+fom_fraction)
            weekly=float(r.assumed_operating_savings_usd)
            shortage=bool(max(float(r.unserved_with_battery_mwh),float(r.unserved_without_battery_mwh))>1e-5)
            rows.append({
                "season":r.season,"scenario":r.scenario,"capex_usd_per_kwh":float(price),
                "battery_power_mw":1000.,"battery_energy_mwh":4000.,
                "investment_usd_assumed":investment,
                "annualized_capital_usd_assumed":investment*crf,
                "annual_fixed_om_usd_assumed":investment*fom_fraction,
                "annual_fixed_cost_usd_assumed":annual_fixed,
                "observed_week_operating_savings_usd_assumed":weekly,
                "break_even_equivalent_weeks_at_observed_week_savings":annual_fixed/weekly if weekly>0 else None,
                "shortage_affected":shortage,
                "classification":"shortage_penalty_dominated_not_arbitrage" if shortage else "illustrative_dispatch_only",
            })
    return pd.DataFrame(rows)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
    result=screen(pd.read_csv(a.input))
    result.to_csv(a.output/"storage_cost_threshold_screen.csv",index=False)
    (a.output/"cost_screen_provenance.json").write_text(json.dumps({
        "technology":"1 GW / 4 GWh utility-scale battery",
        "overnight_capex_usd_per_kwh_scenarios":list(CAPEX_USD_PER_KWH),
        "scenario_not_claimed_as_published_ATB_point_estimates":True,
        "fixed_om_fraction_assumed":FOM_FRACTION,
        "years_assumed":LIFE_YEARS,"real_discount_rate_assumed":DISCOUNT_RATE,
        "references":[
          "https://atb.nlr.gov/electricity/2025/utility-scale_battery_storage",
          "https://atb.nrel.gov/electricity/2024/utility-scale_battery_storage"],
        "caveat":"Annual fixed costs are compared to ONE observed-week saving only via break-even equivalent weeks. Not an annual benefit, payback, NPV, LCOS, or investment recommendation. No extrapolation of selected-week savings."
    },indent=2))
    print(result.to_string(index=False))
if __name__=="__main__":main()
