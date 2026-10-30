"""Experimental 8,760/8,784-hour BA dispatch with observed EIA-930 demand.

This is an assumption-driven hourly benchmark, NOT calibrated historical
generation or verified network/energy-system investment results. Each BA
is modeled separately; no invented transmission interchange capacities.
"""
from __future__ import annotations
import argparse
import calendar
import json
from pathlib import Path
import numpy as np
import pandas as pd


def validate_hourly_demand(data, year, bas):
    if not bas or len(set(bas)) != len(bas):
        raise ValueError("BA selection must be nonempty and unique")
    required={"respondent","period","value"}
    if required-set(data):
        raise ValueError("Demand requires respondent, period and value")
    source=data[list(required)].copy()
    source["period"]=pd.to_datetime(source.period,utc=True,errors="coerce")
    source["value"]=pd.to_numeric(source.value,errors="coerce")
    hours=pd.date_range(f"{year}-01-01",f"{year+1}-01-01",freq="h",inclusive="left",tz="UTC")
    if source.period.isna().any() or not source.respondent.isin(bas).all():
        raise ValueError("Invalid timestamp or unexpected BA")
    if not source.period.isin(hours).all() or source.duplicated(["respondent","period"]).any():
        raise ValueError("Demand must have unique in-year UTC hourly timestamps")
    if not np.isfinite(source.value.to_numpy(dtype=float)).all() or (source.value<=0).any():
        raise ValueError("All demand MW must be finite and positive; no silent imputation")
    demand=source.pivot(index="period",columns="respondent",values="value").reindex(
        index=hours,columns=bas)
    if demand.isna().any().any():
        raise ValueError("Full chronological year required for each BA; no representative hours")
    return demand


def solve_hourly_demand(demand, year, *, gas_capacity_mw=None):
    """Solve independent BA energy dispatch under transparent assumed gas supply."""
    import pypsa
    expected=pd.date_range(f"{year}-01-01",f"{year+1}-01-01",freq="h",inclusive="left",tz="UTC")
    if not demand.index.equals(expected) or demand.empty:
        raise ValueError("Full chronological UTC-year demand required")
    if not np.isfinite(demand.to_numpy(dtype=float)).all() or (demand<=0).any().any():
        raise ValueError("Demand must be finite and positive")
    network=pypsa.Network()
    # PyPSA may strip timezone metadata on snapshots; save explicit UTC
    # interpretation in the provenance rather than assuming local time.
    network.set_snapshots(expected.tz_localize(None))
    for ba in demand.columns:
        if not isinstance(ba,str) or not ba.strip():
            raise ValueError("Nonblank BA identifiers required")
        network.add("Bus",ba)
        network.add("Load",f"{ba}_load",bus=ba,p_set=demand[ba].to_numpy(dtype=float))
        # Sufficient capacity is intentionally assumed for feasibility.
        cap=(float(gas_capacity_mw[ba]) if gas_capacity_mw is not None
             else float(demand[ba].max())*1.1)
        if not np.isfinite(cap) or cap<=0:
            raise ValueError("Assumed gas capacity must be finite and positive")
        network.add("Generator",f"{ba}_gas",bus=ba,p_nom=cap,marginal_cost=65)
        network.add("Generator",f"{ba}_unserved",bus=ba,p_nom=float(demand[ba].max())*2,
                    marginal_cost=10000)
    status,condition=network.optimize(solver_name="highs")
    if status!="ok" or condition!="optimal":
        raise RuntimeError(f"Hourly PyPSA solve failed: {status}, {condition}")
    return network


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--demand",type=Path,required=True)
    parser.add_argument("--year",type=int,default=2024)
    parser.add_argument("--bas",nargs="+",default=["CISO","BPAT"])
    parser.add_argument("--output",type=Path,default=Path("outputs/hourly_dispatch_pilot"))
    args=parser.parse_args()
    data=pd.read_csv(args.demand)
    demand=validate_hourly_demand(data,args.year,args.bas)
    network=solve_hourly_demand(demand,args.year)
    args.output.mkdir(parents=True,exist_ok=True)
    network.export_to_netcdf(args.output/"hourly_network.nc")
    manifest={
        "year":args.year,"bas":args.bas,"hours":8784 if calendar.isleap(args.year) else 8760,
        "demand":"EIA-930 supplied BA hourly demand, subject to upstream QC",
        "model":"Independent BA gas-only dispatch with assumed marginal cost and ample gas capacity",
        "timezone":"Naive PyPSA snapshots represent UTC, and require explicit tagging when read",
        "limitations":"Not a historical generation calibration; no observed technology supply, storage or BA interchange; no cost savings or emissions inferences."
    }
    (args.output/"provenance.json").write_text(json.dumps(manifest,indent=2))
    print(json.dumps(manifest,indent=2))


if __name__=="__main__":
    main()
