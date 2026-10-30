"""Validate shortage-penalty attribution in seasonal battery scenarios.

This gate catches incorrectly labeled economic benefits. It does not assert
that the assumed value of lost load is empirically justified.
"""
import argparse
import json
from pathlib import Path
import pandas as pd

def audit(frame, penalty_usd_per_mwh=10000.):
    d=frame.copy()
    required={"season","duration_h","operating_savings_usd","avoided_unserved_mwh",
              "avoided_unserved_penalty_usd","non_shortage_dispatch_savings_usd",
              "unserved_mwh","unserved_without_storage_mwh"}
    if missing:=required-set(d):
        raise ValueError(f"Missing savings attribution fields: {sorted(missing)}")
    if d.duplicated(["season","duration_h"]).any():
        raise ValueError("Duplicate season-duration rows")
    expected=d.avoided_unserved_mwh*penalty_usd_per_mwh
    identity=d.avoided_unserved_penalty_usd+d.non_shortage_dispatch_savings_usd
    if (expected-d.avoided_unserved_penalty_usd).abs().gt(.01).any():
        raise ValueError("Avoided shortage penalty inconsistent with assumed value of lost load")
    if (identity-d.operating_savings_usd).abs().gt(.01).any():
        raise ValueError("Total savings do not reconcile to shortage and dispatch components")
    if ((d.unserved_without_storage_mwh-d.unserved_mwh)-d.avoided_unserved_mwh).abs().gt(.001).any():
        raise ValueError("Avoided unmet load does not reconcile")
    d["shortage_affected"]=d[["unserved_mwh","unserved_without_storage_mwh"]].gt(.001).any(axis=1)
    d["interpretation"]=d.shortage_affected.map({
        True:"shortage_penalty_scenario_not_market_arbitrage",
        False:"no_shortage_assumed_dispatch_savings_only",
    })
    return d

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    d=audit(pd.read_csv(args.input))
    d.to_csv(args.output/"seasonal_savings_attribution_audit.csv",index=False)
    (args.output/"savings_audit_manifest.json").write_text(json.dumps({
       "source":str(args.input),"unserved_penalty_usd_per_mwh_assumed":10000,
       "formula":"total operating savings = avoided unserved penalty + non-shortage dispatch savings",
       "limits":"This arithmetic audit does not establish market value, validated reliability benefit, or battery investment profitability."
    },indent=2))
    print(d[["season","duration_h","shortage_affected","operating_savings_usd","avoided_unserved_penalty_usd","non_shortage_dispatch_savings_usd"]].to_string(index=False))
if __name__=="__main__":main()
