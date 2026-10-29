"""Summarize EIA-930 API/PUDL same-hour stage-alignment reproducibility.

This gate validates source/timestamp agreement, NEVER BA energy accounting
or transmission calibration.
"""
import argparse
import json
from pathlib import Path
import pandas as pd

def assess(frame, tolerance_mw=0.1):
    needed={"ba_code","stage","series","api_shift_hours","same_hour_pairs","mae_mw"}
    if needed-set(frame):raise ValueError(f"Missing comparison fields: {needed-set(frame)}")
    records=[]
    for (ba,stage,series),group in frame.groupby(["ba_code","stage","series"]):
        eligible=group[group.same_hour_pairs.gt(0)]
        if eligible.empty:continue
        best=eligible.sort_values(["mae_mw","api_shift_hours"]).iloc[0]
        zero=eligible[eligible.api_shift_hours.eq(0)]
        z=zero.iloc[0] if len(zero) else None
        records.append({"ba_code":ba,"stage":stage,"series":series,
            "best_shift_hours":int(best.api_shift_hours),
            "best_mae_mw":float(best.mae_mw),
            "zero_shift_mae_mw":float(z.mae_mw) if z is not None else None,
            "zero_shift_pairs":int(z.same_hour_pairs) if z is not None else 0,
            "zero_shift_within_tolerance":bool(z is not None and z.mae_mw<=tolerance_mw),
            "warning":"Cross-source agreement only; does not validate physical energy balance."})
    return records

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--comparison",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    rows=assess(pd.read_csv(args.comparison))
    (args.output/"source_alignment_gate.json").write_text(json.dumps({
      "mae_tolerance_mw":0.1,"records":rows,
      "policy":"Never interpret matched source fields as independently validated BA balance or line capacity."
    },indent=2))
    print(pd.DataFrame(rows).to_string(index=False))
if __name__=="__main__":main()
