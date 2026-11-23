"""Annualize ATB 2025 *incremental* utility-scale 4->8h BESS cost.

No numerical ATB assumptions are hardcoded: requires a user-supplied,
provenance-tagged transcription/export of the official ATB workbook. This
module does not invent 2030 costs, model profitability or count a
simulated avoided-variable-cost metric as merchant revenue.

Input CSV columns:
scenario,year,duration_h,capex_usd_per_kw,fom_usd_per_kw_year,
source_url,source_edition,cost_dollar_year,power_basis_kw.
For each scenario exactly two rows (4,8 hours), 2030, same power basis,
edition, source and dollar year. These are overnight installed CAPEX on
common MW power rating, inclusive of appropriate energy components.

Optional value CSV: 240 actual storage triplets with
annualized_marginal_4_to_8_usd_kwh_year, weather_year, state,
county_weight_scheme, load_mode. Alternatively accepts verified
paper_s_same_weather_240_duration_triplets.csv whose value column is
annualized_marginal_4_to_8_usd_kwh_year.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd

SCENARIOS=("Advanced","Moderate","Conservative")
DURATIONS=(4,8)
REQUIRED={
    "scenario","year","duration_h","capex_usd_per_kw",
    "fom_usd_per_kw_year","source_url","source_edition",
    "cost_dollar_year","power_basis_kw",
}


def crf(rate,years):
    if not 0<rate<1 or not 1<=years<=50:
        raise ValueError("Real discount rate must be positive <1 and lifetime 1-50")
    return float(rate*(1+rate)**years/((1+rate)**years-1))


def compute_costs(input_frame,rates=(0.04,0.07,0.10),lifetime_years=15):
    if not REQUIRED.issubset(input_frame.columns):
        raise ValueError(f"Missing ATB extraction fields: {sorted(REQUIRED-set(input_frame.columns))}")
    df=input_frame.copy()
    if len(df)!=6 or df.duplicated(["scenario","year","duration_h"]).any():
        raise ValueError("ATB cost sheet requires exactly 3 scenarios x 4/8 durations")
    if set(df.scenario)!=set(SCENARIOS) or set(df.duration_h)!={4,8} or set(df.year)!={2030}:
        raise ValueError("All six ATB entries must be 2030 Advanced/Moderate/Conservative 4h and 8h")
    for x in ("capex_usd_per_kw","fom_usd_per_kw_year","power_basis_kw"):
        df[x]=pd.to_numeric(df[x],errors="raise")
        if not np.isfinite(df[x]).all() or (df[x]<0).any():
            raise ValueError(f"Nonnegative finite ATB cost required: {x}")
    if (df.power_basis_kw<=0).any() or (df.capex_usd_per_kw==0).any():
        raise ValueError("ATB power basis/capex must be strictly positive")
    for field in ("source_url","source_edition","cost_dollar_year"):
        if df[field].isna().any() or df[field].astype(str).str.strip().eq("").any():
            raise ValueError(f"Missing ATB provenance {field}")
    if not df.source_edition.astype(str).str.contains("2025").all():
        raise ValueError("This program admits only ATB 2025 (not 2024/2025 mix)")
    if not df.source_url.astype(str).str.contains("atb.nlr.gov|data.openei.org",regex=True).all():
        raise ValueError("Source must be traceable to the official 2025 ATB provider")
    outputs=[]
    for scen,g in df.groupby("scenario",sort=True):
        q=g.set_index("duration_h")
        for field in ("source_edition","cost_dollar_year","source_url","power_basis_kw"):
            if q[field].nunique(dropna=False)!=1:
                raise ValueError(f"Inconsistent ATB source/currency/power basis for {scen}: {field}")
        delta_capex=float(q.loc[8,"capex_usd_per_kw"]-q.loc[4,"capex_usd_per_kw"])
        delta_fom=float(q.loc[8,"fom_usd_per_kw_year"]-q.loc[4,"fom_usd_per_kw_year"])
        if delta_capex<=0:
            raise ValueError("Additional energy must have positive total installed CAPEX")
        if delta_fom<0:
            raise ValueError("Incremental O&M must not be negative; investigate source")
        # 1 kW common power * (8-4) h = 4 kWh increment.
        energy_delta=4.
        for rate in rates:
            annualized=(delta_capex*crf(rate,lifetime_years)+delta_fom)/energy_delta
            outputs.append(dict(
                scenario=scen,year=2030,source_edition=q.loc[4,"source_edition"],
                source_url=q.loc[4,"source_url"],cost_dollar_year=q.loc[4,"cost_dollar_year"],
                comparison_duration_start_h=4,comparison_duration_end_h=8,
                delta_capex_usd_kw=delta_capex,delta_fom_usd_kw_year=delta_fom,
                delta_energy_kwh_per_kw=energy_delta,
                capex_increment_usd_per_added_kwh=delta_capex/energy_delta,
                real_discount_rate=rate,lifetime_years=lifetime_years,
                capital_recovery_factor=crf(rate,lifetime_years),
                annualized_extension_hurdle_usd_kwh_year=annualized,
            ))
    out=pd.DataFrame(outputs)
    if len(out)!=3*len(rates):raise ValueError("Expected 3 ATB scenarios x rate assumptions")
    return out


def compare_avoided_cost(costs,triplets):
    keys={"weather_year","state","county_weight_scheme","load_mode",
        "annualized_marginal_4_to_8_usd_kwh_year"}
    if not keys.issubset(triplets.columns):
        raise ValueError("Missing verified LP value-triplet fields")
    df=triplets.copy()
    if df.duplicated(["weather_year","state","county_weight_scheme","load_mode"]).any():
        raise ValueError("Duplicate LP duration value")
    x=df.merge(costs,how="cross",validate="many_to_many")
    x["surplus_illustrative_operating_value_usd_kwh_year"]=(
        x.annualized_marginal_4_to_8_usd_kwh_year-
        x.annualized_extension_hurdle_usd_kwh_year)
    x["operating_value_exceeds_annualized_extension_hurdle"]=(
        x.surplus_illustrative_operating_value_usd_kwh_year>=0)
    x["cash_flow_or_market_profit_established"]=False
    return x


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--atb-extracted-2030",type=Path,required=True)
    p.add_argument("--verified-lp-duration-triplets",type=Path)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    costs=compute_costs(pd.read_csv(a.atb_extracted_2030))
    a.out.mkdir(parents=True,exist_ok=True)
    costs.to_csv(a.out/"paper_s_ATB2025_2030_4to8_annualized_increment.csv",index=False)
    manifest={
        "source_edition":"ATB 2025","target_year":2030,
        "ATB_values_source":"input CSV; MUST retain publisher provenance",
        "capex_and_fom_separate":True,"historical_lp_actual_profit_calculated":False,
        "annual_cost_hurdle_formula":"((capex8-capex4)*CRF + (FOM8-FOM4))/4",
        "power_capacity_fixed_between_4h_and_8h":True,
        "currency_year_inherited_from_source":True,
        "lifetime_years":15,"discount_rates":[.04,.07,.10]}
    if a.verified_lp_duration_triplets:
        outcomes=compare_avoided_cost(costs,pd.read_csv(a.verified_lp_duration_triplets))
        outcomes.to_csv(a.out/"paper_s_ATB2025_avoided_cost_vs_hurdle.csv",index=False)
        manifest["verified_lp_cost_comparisons"]=len(outcomes)
    (a.out/"paper_s_ATB2025_cost_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print("PAPER_S_ATB2025_COST_EXTENSION_AUDIT_COMPLETE",json.dumps(manifest))


if __name__=="__main__":
    main()
