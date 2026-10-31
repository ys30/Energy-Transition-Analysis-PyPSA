"""Cross-check hourly missingness windows against aligned D/NG/TI records."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import pandas as pd


def verify(hourly: pd.DataFrame, windows: pd.DataFrame) -> dict:
    required={"respondent","period","demand","generation","interchange"}
    if required-set(hourly.columns):
        raise ValueError("Missing hourly audit fields")
    x=hourly.copy()
    x["period"]=pd.to_datetime(x.period,utc=True,errors="raise")
    if x.duplicated(["respondent","period"]).any():
        raise ValueError("Duplicate BA-hour timestamps")
    for col in ("respondent","field","start_utc","end_utc_exclusive","missing_hours"):
        if col not in windows:
            raise ValueError(f"Missing gap window field: {col}")
    counts={}
    for ba,g in x.groupby("respondent"):
        counts[ba]={}
        for field in ("demand","generation","interchange"):
            observed=int(g[field].isna().sum())
            subset=windows.loc[windows.respondent.eq(ba)&windows.field.eq(field)]
            durations=0
            for w in subset.itertuples():
                start=pd.Timestamp(w.start_utc)
                end=pd.Timestamp(w.end_utc_exclusive)
                if start.tzinfo is None or end.tzinfo is None:
                    raise ValueError("Gap timestamps must be timezone aware")
                start,end=start.tz_convert("UTC"),end.tz_convert("UTC")
                duration=(end-start)/pd.Timedelta(hours=1)
                if duration<=0 or duration!=int(w.missing_hours):
                    raise ValueError(f"Invalid gap duration: {ba} {field}")
                selected=g.period.ge(start)&g.period.lt(end)
                if selected.sum()!=int(w.missing_hours) or not g.loc[selected,field].isna().all():
                    raise ValueError(f"Gap interval does not match source observations: {ba} {field}")
                durations+=int(w.missing_hours)
            if observed!=durations:
                raise ValueError(f"Gap window total mismatch: {ba} {field}: {durations} vs {observed}")
            counts[ba][field]=observed
    return {"verified":True,"missing_hours_by_ba_field":counts,
            "warning":"Consistency validation only, not external source restoration."}


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--hourly",type=Path,required=True)
    p.add_argument("--windows",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    result=verify(pd.read_csv(a.hourly),pd.read_csv(a.windows))
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))


if __name__=="__main__":
    main()
