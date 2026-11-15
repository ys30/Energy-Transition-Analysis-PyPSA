"""Compare source-cell-pinned ATB 2025 v2 costs against authenticated matched-weather LPs.

Uses the 2025 v2 workbook source SHA, tab and exact source cell identifiers.
All model financing assumptions are explicitly analyst sensitivities; operating
value is not observed profit. The LP 2030 representation uses historical weather.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd
from energy_transition.paper_s_atb_2030_storage_extension_cost import (
    compute_costs,compare_avoided_cost,
)

EXPECTED_SHA="c3cece683ecbc943ac7170cbe668e4efdc5367731fe0bce83ee34bb359970b56"
VARIANTS=("Expand","R&D")
YEAR=2030

def run(atb,lp,out):
    required={"source_variant","source_sha256","source_capex_cell","source_fom_cell"}
    if not required.issubset(atb.columns):
        raise ValueError("Missing original-workbook cell provenance")
    if len(atb)!=12 or atb.duplicated(["source_variant","scenario","duration_h"]).any():
        raise ValueError("Expected 12 unique v2-source 4h/8h rows")
    if set(atb.source_variant)!=set(VARIANTS) or not atb.source_sha256.eq(EXPECTED_SHA).all():
        raise ValueError("Unknown workbook version/sha or missing cost-driver variants")
    if not atb.source_edition.astype(str).str.contains("2025 v2").all():
        raise ValueError("Source must be corrected updated ATB2025 v2")
    for _,row in atb.iterrows():
        if row.duration_h not in (4,8) or row.scenario not in ("Advanced","Moderate","Conservative"):
            raise ValueError("Unexpected ATB duration/cost category")
        name="'Utility-Scale Battery - "+row.source_variant+"'!"
        if not str(row.source_capex_cell).startswith(name+"O"):
            raise ValueError("CAPEX source cell sheet/year mismatch")
        if not str(row.source_fom_cell).startswith(name+"O"):
            raise ValueError("FOM source cell sheet/year mismatch")
    required_lp={"weather_year","state","county_weight_scheme","load_mode",
                 "annualized_marginal_4_to_8_usd_kwh_year"}
    if not required_lp.issubset(lp.columns):raise ValueError("Missing authenticated LP results")
    raw=lp[lp.load_mode.eq("actual_historical_level")].copy()
    if len(lp)!=240 or len(raw)!=120 or raw.duplicated(
            ["weather_year","state","county_weight_scheme"]).any():
        raise ValueError("Expected 240 source triplets with 120 distinct actual-history cases")
    if not np.isfinite(raw.annualized_marginal_4_to_8_usd_kwh_year).all():
        raise ValueError("LP values not finite")
    if len(set(raw.weather_year))!=15 or set(raw.state)!={"AZ","CO","ID","WY"}:
        raise ValueError("Weather calendar or state set mismatch")
    results=[];screen=[]
    for variant,g in atb.groupby("source_variant"):
        if len(g)!=6:raise ValueError("Missing ATB scenario rows")
        costs=compute_costs(g,rates=(.04,.07,.10),lifetime_years=15)
        costs["source_variant"]=variant
        compared=compare_avoided_cost(costs,raw)
        compared["source_variant"]=variant
        results.append(costs)
        screen.append(compared)
    costs=pd.concat(results,ignore_index=True)
    cases=pd.concat(screen,ignore_index=True)
    if len(costs)!=18 or len(cases)!=2160:raise ValueError("Expected 18 cost assumptions and 2160 comparisons")
    summary=(cases.groupby(["source_variant","scenario","real_discount_rate"],as_index=False)
        .agg(total_lp_cases=("operating_value_exceeds_annualized_extension_hurdle","size"),
             meeting_threshold=("operating_value_exceeds_annualized_extension_hurdle","sum"),
             min_value_minus_cost=("surplus_illustrative_operating_value_usd_kwh_year","min"),
             max_value_minus_cost=("surplus_illustrative_operating_value_usd_kwh_year","max")))
    if not summary.total_lp_cases.eq(120).all():
        raise ValueError("Unexpected LP count per cost assumption")
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    costs.to_csv(out/"paper_s_official_atb2025_v2_18_cost_hurdles.csv",index=False)
    cases.to_csv(out/"paper_s_official_atb2025_v2_2160_lp_cost_comparisons.csv",index=False)
    summary.to_csv(out/"paper_s_official_atb2025_v2_18_screening_summaries.csv",index=False)
    manifest={
        "status":"ATB2025_V2_SOURCE_CELL_PINNED_COST_SCREENING",
        "official_source_sha256":EXPECTED_SHA,
        "source_atb_edition":"ATB2025 v2 (Nov 11, 2026)",
        "source_currency":"2023 USD",
        "source_cost_variants":list(VARIANTS),
        "matched_lp_workflow_run_id":43665299980,
        "workbook_layout_workflow_run_id":43673367026,
        "duration_h_increment":4,
        "discount_rate_sensitivity":[.04,.07,.10],
        "lifetime_years_assumption":15,
        "cost_rows":len(costs),"matched_historical_lp_triplets":len(raw),
        "case_comparisons":len(cases),
        "zero_of_120_claim_only_per_assumption":bool(summary.meeting_threshold.eq(0).all()),
        "cash_flow_or_market_profit_established":False,
        "EIA930_observational_validation_established":False,
        "additional_cost_components_not_modeled":True,
    }
    (out/"paper_s_official_atb2025_v2_screening_manifest.json").write_text(
        json.dumps(manifest,indent=2)+"\n")
    print("PAPER_S_ATB2025_V2_AUTHENTIC_SOURCE_2160_SCREENING_COMPLETE",json.dumps(manifest))
    return costs,cases,summary

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source-cells",type=Path,required=True)
    p.add_argument("--verified-lp-triplets",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    run(pd.read_csv(a.source_cells),pd.read_csv(a.verified_lp_triplets),a.out)

if __name__=="__main__":main()
