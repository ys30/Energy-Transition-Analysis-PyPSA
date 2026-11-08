"""Decompose marginal toy LP objective changes into firm and unused-potential terms.

Identity holds only for fixed original renewable availability across the three
battery durations: delta cost = 90 * avoided firm MWh - 5 * avoided unused MWh.
Does not establish storage profitability or weather/clock attribution.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd

from .paper_s_marginal_duration import derive

INC = ("0to4h", "4to8h")
FIRM_PRICE = 90.
RENEWABLE_PRICE = 5.


def decompose(cases: pd.DataFrame) -> pd.DataFrame:
    marginals=derive(cases)  # Independently validates 540 cases and LP objective.
    # Annual renewable availability must be duration-invariant *within every zone and profile*.
    by_zone=["planning_year","state","reeds_zone","synthetic_supply_shape"]
    spread=cases.groupby(by_zone).renewable_available_mwh.agg(lambda v: float(v.max()-v.min()))
    if (spread > .001).any():
        raise ValueError("Renewable availability changes across battery durations")
    out=[]
    for row in marginals.itertuples(index=False):
        r={"planning_year":int(row.planning_year),"synthetic_supply_shape":row.synthetic_supply_shape}
        for inc in INC:
            avoided_firm=getattr(row,f"firm_generation_mwh_reduction_{inc}")
            avoided_unused=getattr(row,f"unused_renewable_mwh_reduction_{inc}")
            reported=getattr(row,f"objective_illustrative_variable_usd_reduction_{inc}")
            firm_component=FIRM_PRICE*avoided_firm
            renewable_component=-RENEWABLE_PRICE*avoided_unused
            predicted=firm_component+renewable_component
            if not np.isclose(predicted,reported,rtol=1e-10,atol=.03):
                raise ValueError("Marginal objective decomposition fails on original 540-case archive")
            r.update({
                f"avoided_firm_{inc}_mwh":avoided_firm,
                f"avoided_unused_{inc}_mwh":avoided_unused,
                f"firm_component_{inc}_usd":firm_component,
                f"renewable_utilization_component_{inc}_usd":renewable_component,
                f"reconstructed_cost_reduction_{inc}_usd":predicted,
                f"reported_cost_reduction_{inc}_usd":reported,
                f"reconciliation_error_{inc}_usd":predicted-reported,
            })
        a=r["reported_cost_reduction_0to4h_usd"]
        b=r["reported_cost_reduction_4to8h_usd"]
        r["second_increment_over_first"]=b/a if abs(a)>1e-8 else np.nan
        out.append(r)
    result=pd.DataFrame(out).sort_values(["planning_year","synthetic_supply_shape"]).reset_index(drop=True)
    if len(result)!=9:raise ValueError("Expected nine year-shape groups")
    return result


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--cases",required=True,type=Path)
    p.add_argument("--csv",required=True,type=Path)
    p.add_argument("--json",required=True,type=Path)
    a=p.parse_args()
    result=decompose(pd.read_csv(a.cases))
    a.csv.parent.mkdir(parents=True,exist_ok=True)
    a.json.parent.mkdir(parents=True,exist_ok=True)
    result.to_csv(a.csv,index=False,float_format="%.12g")
    report={"status":"PAPER_S_SOURCE_OBJECTIVE_DECOMPOSITION_PASS",
            "source_cases":540,"year_shape_comparisons":len(result),
            "max_reconciliation_error_usd":float(max(result["reconciliation_error_0to4h_usd"].abs().max(),
                                                       result["reconciliation_error_4to8h_usd"].abs().max())),
            "cost_formula":"90*avoided_firm_MWh - 5*avoided_unused_MWh",
            "validated_physical_hourly_mismatch_mechanism":False,
            "actual_western_grid_or_investment_value":False}
    a.json.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))


if __name__=="__main__":
    main()
