"""Cross-check BPAT/CISO EIA-930 reporting stages using public Catalyst PUDL.

Query public columnar PUDL data with DuckDB predicate pushdown. No data
imputation is performed here. This is independent of the EIA API pipeline.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import pandas as pd

PARQUET = "https://pudl.catalyst.coop/nightly/core_eia930__hourly_operations.parquet"
STAGES = ("reported", "adjusted", "imputed_eia")
FIELDS = ("demand", "net_generation", "interchange")


def evaluate(df, bas=("BPAT", "CISO"), year=2024):
    required={"datetime_utc","balancing_authority_code_eia"} | {
      f"{item}_{stage}_mwh" for item in FIELDS for stage in STAGES
    }
    if required-set(df):
        raise ValueError(f"PUDL core table missing columns: {sorted(required-set(df))}")
    x=df.copy()
    x["datetime_utc"]=pd.to_datetime(x["datetime_utc"],utc=True)
    x=x[x.balancing_authority_code_eia.isin(bas) & x.datetime_utc.dt.year.eq(year)]
    if x.duplicated(["balancing_authority_code_eia","datetime_utc"]).any():
        raise ValueError("Duplicate PUDL BA-hour keys")
    rows=[]
    for ba in bas:
        b=x[x.balancing_authority_code_eia.eq(ba)]
        for stage in STAGES:
            names=[f"{v}_{stage}_mwh" for v in FIELDS]
            valid=b.dropna(subset=names).copy()
            residual=valid[names[0]]-valid[names[1]]+valid[names[2]]
            rows.append({
              "ba_code":ba,"stage":stage,"year":year,
              "source_hours":len(b),"complete_hours":len(valid),
              "residual_sum_mwh":float(residual.sum()),
              "residual_mae_mw":float(residual.abs().mean()) if len(residual) else None,
              "residual_median_mw":float(residual.median()) if len(residual) else None,
              "positive_residual_share":float(residual.gt(0).mean()) if len(residual) else None,
              "status":"descriptive_report_stage_comparison_not_line_capacity",
            })
    return pd.DataFrame(rows)


def fetch(year, bas):
    import duckdb
    con=duckdb.connect()
    con.execute("INSTALL httpfs; LOAD httpfs;")
    cols=["datetime_utc","balancing_authority_code_eia"] + [
      f"{name}_{stage}_mwh" for stage in STAGES for name in FIELDS
    ]
    # Query only a target-year slice; avoid downloading the full nationwide table.
    ba_list=", ".join("'"+b.replace("'","''")+"'" for b in bas)
    query=(f"SELECT {', '.join(cols)} FROM read_parquet(?) "
      f"WHERE balancing_authority_code_eia IN ({ba_list}) "
      "AND datetime_utc >= ? AND datetime_utc < ?")
    return con.execute(query,[PARQUET, f"{year}-01-01",f"{year+1}-01-01"]).df()


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--year",type=int,default=2024)
    p.add_argument("--bas",nargs="+",default=["BPAT","CISO"])
    p.add_argument("--output",type=Path,default=Path("outputs/pudl_ba_stage"))
    args=p.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    frame=fetch(args.year,args.bas)
    report=evaluate(frame,args.bas,args.year)
    report.to_csv(args.output/"pudl_ba_stage_residuals.csv",index=False)
    (args.output/"provenance.json").write_text(json.dumps({
      "source":PARQUET,"year":args.year,"bas":args.bas,
      "method":"Within each reporting stage, calculate D-NG+TI on common nonnull BA-hours.",
      "limitations":["PUDL is independently processed EIA-930, not independent physical metering.",
      "EIA-930 datetime is hour-ending UTC; verify one-hour offset when aligning EIA API.",
      "Do not infer transmission capacity or replace original reported data."],
    },indent=2))
    print(report.to_string(index=False))


if __name__=="__main__": main()
