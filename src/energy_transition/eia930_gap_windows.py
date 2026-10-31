"""Locate contiguous UTC data gaps in observed EIA-930 D, NG and TI series."""
from __future__ import annotations
import argparse
from pathlib import Path
import pandas as pd


def gap_windows(frame: pd.DataFrame) -> pd.DataFrame:
    needed={"respondent","period","demand","generation","interchange"}
    if needed-set(frame.columns):
        raise ValueError("Missing aligned EIA-930 hourly fields")
    x=frame.copy()
    x["period"]=pd.to_datetime(x.period,utc=True,errors="raise")
    if x.duplicated(["respondent","period"]).any():
        raise ValueError("Duplicate BA-hour input")
    windows=[]
    for ba,g in x.groupby("respondent"):
        g=g.sort_values("period")
        if not g.period.diff().dropna().eq(pd.Timedelta(hours=1)).all():
            raise ValueError(f"Non-contiguous hourly audit index: {ba}")
        for field in ("demand","generation","interchange"):
            missing=g[field].isna()
            if not missing.any():
                continue
            changes=missing.ne(missing.shift(fill_value=False)).cumsum()
            for _,segment in g.loc[missing].groupby(changes[missing]):
                start=segment.period.iloc[0]
                windows.append({"respondent":ba,"field":field,
                                "start_utc":start.isoformat(),
                                "end_utc_exclusive":(segment.period.iloc[-1]+pd.Timedelta(hours=1)).isoformat(),
                                "missing_hours":len(segment)})
    columns=["respondent","field","start_utc","end_utc_exclusive","missing_hours"]
    return pd.DataFrame(windows,columns=columns).sort_values(
        ["respondent","field","start_utc"]).reset_index(drop=True)


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--hourly",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    result=gap_windows(pd.read_csv(a.hourly))
    a.output.parent.mkdir(parents=True,exist_ok=True)
    result.to_csv(a.output,index=False)
    print(result.to_string(index=False))


if __name__=="__main__":
    main()
