"""Field-level missingness of EIA-930 hourly BA D/NG/TI triples, without imputation."""
from __future__ import annotations
import argparse
from pathlib import Path
import pandas as pd


def summarize(frame: pd.DataFrame) -> pd.DataFrame:
    required={"respondent","period","demand","generation","interchange"}
    if required-set(frame):
        raise ValueError(f"Missing hourly balance fields: {sorted(required-set(frame))}")
    x=frame.copy()
    x["period"]=pd.to_datetime(x.period,utc=True,errors="raise")
    if x.duplicated(["respondent","period"]).any():
        raise ValueError("Duplicate BA-hour timestamps")
    flags=x[["demand","generation","interchange"]].isna()
    x["missing_fields"]=flags.apply(lambda row: "+".join(name for name,missing in row.items() if missing) or "complete",axis=1)
    x["month_utc"]=x.period.dt.strftime("%Y-%m")
    result=(x.groupby(["respondent","month_utc","missing_fields"],dropna=False)
            .size().rename("hour_count").reset_index())
    return result.sort_values(["respondent","month_utc","missing_fields"]).reset_index(drop=True)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--hourly",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    result=summarize(pd.read_csv(args.hourly))
    args.output.parent.mkdir(parents=True,exist_ok=True)
    result.to_csv(args.output,index=False)
    print(result.to_string(index=False))


if __name__=="__main__":
    main()
