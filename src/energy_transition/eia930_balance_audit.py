"""Audit observed EIA-930 BA interchange and accounting balance (2024).

Official EIA-930 series D=reported demand, NG=net generation, TI=total interchange.
Positive TI denotes net exports and negative TI net imports. The usual
EIA identity is D = NG - TI, but processing stages may not be consistent.
"""
import argparse,json
from pathlib import Path
import pandas as pd
from .eia930_generation_audit import fetch_net_generation,API
from .eia930_west import fetch_eia_demand
import urllib.parse,urllib.request,os

def fetch_ti(year,bas):
    key=os.environ["EIA_API_KEY"]
    params=[("api_key",key),("frequency","hourly"),("data[0]","value"),
            ("facets[type][]","TI"),("start",f"{year}-01-01T00"),
            ("end",f"{year}-12-31T23"),("length","5000"),
            ("sort[0][column]","period"),("sort[0][direction]","asc")]
    params.extend(("facets[respondent][]",b) for b in bas)
    rows=[];offset=0
    while True:
        url=API+"?"+urllib.parse.urlencode(params+[("offset",str(offset))])
        with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"pypsa-west-balance-audit/0.1"}),timeout=90) as f:
            response=json.load(f)["response"]
        page=response["data"]
        if not page:break
        rows.extend(page);offset+=len(page)
        if offset>=int(response.get("total",offset)):break
    if not rows:raise ValueError("No EIA-930 TI observations")
    df=pd.DataFrame(rows)[["period","respondent","value"]]
    df["period"]=pd.to_datetime(df.period,utc=True)
    df["value"]=pd.to_numeric(df.value,errors="coerce")
    if df.duplicated(["respondent","period"]).any():raise ValueError("Duplicate interchange observations")
    return df

def balance_audit(demand,generation,interchange,bas,year):
    idx=pd.MultiIndex.from_product([bas,pd.date_range(f"{year}-01-01",f"{year+1}-01-01",freq="h",inclusive="left",tz="UTC")],names=["respondent","period"])
    outputs={}
    for label,df in [("demand",demand),("generation",generation),("interchange",interchange)]:
        required={"respondent","period","value"}
        if required-set(df):
            raise ValueError(f"{label}: missing respondent/period/value columns")
        source=df.copy()
        source["period"]=pd.to_datetime(source["period"],utc=True,errors="coerce")
        if source["period"].isna().any():
            raise ValueError(f"{label}: invalid hourly timestamps")
        if source.duplicated(["respondent","period"]).any():
            raise ValueError(f"{label}: duplicate BA-hour observations")
        source["value"]=pd.to_numeric(source["value"],errors="coerce")
        import numpy as np
        if np.isinf(source["value"].to_numpy(dtype=float)).any():
            raise ValueError(f"{label}: infinite observed values")
        # Missing measurements are retained as NaN, never imputed to zero.
        outputs[label]=source.set_index(["respondent","period"])["value"].reindex(idx)
    merged=pd.DataFrame(outputs).reset_index()
    merged["residual_d_minus_ng_minus_ti"]=merged.demand-merged.generation-merged.interchange
    merged["residual_d_minus_ng_plus_ti"]=merged.demand-merged.generation+merged.interchange
    audit=merged.groupby("respondent").agg(
      expected_hours=("period","size"),
      complete_triples=("residual_d_minus_ng_minus_ti","count"),
      missing_demand=("demand",lambda v:int(v.isna().sum())),
      missing_generation=("generation",lambda v:int(v.isna().sum())),
      missing_interchange=("interchange",lambda v:int(v.isna().sum())),
      sum_observed_demand_mwh=("demand","sum"),
      sum_observed_generation_mwh=("generation","sum"),
      sum_observed_interchange_mwh=("interchange","sum"),
      mae_d_minus_ng_minus_ti=("residual_d_minus_ng_minus_ti",lambda v:float(v.abs().mean())),
      mae_d_minus_ng_plus_ti=("residual_d_minus_ng_plus_ti",lambda v:float(v.abs().mean()))
    ).reset_index()
    # Quantify official and opposite-sign diagnostic residuals on common complete
    # hours, never sum independently incomplete
    # annual series into an alleged energy-balance identity.
    valid=merged.dropna(subset=["demand","generation","interchange"])
    common=valid.groupby("respondent").agg(
        common_demand_mwh=("demand","sum"),
        common_generation_mwh=("generation","sum"),
        common_interchange_mwh=("interchange","sum"),
        common_residual_minus_mwh=("residual_d_minus_ng_minus_ti","sum"),
        common_residual_plus_mwh=("residual_d_minus_ng_plus_ti","sum"))
    audit=audit.merge(common.reset_index(),on="respondent",how="left")
    audit["complete_triple_share"]=audit.complete_triples/audit.expected_hours
    audit["candidate_plus_mae_share_of_load"]=audit.mae_d_minus_ng_plus_ti/(
        audit.common_demand_mwh/audit.complete_triples)
    audit["candidate_minus_mae_share_of_load"]=audit.mae_d_minus_ng_minus_ti/(
        audit.common_demand_mwh/audit.complete_triples)
    audit["official_balance_residual_mwh"]=audit.common_residual_plus_mwh
    audit["official_balance_mae_mw"]=audit.mae_d_minus_ng_plus_ti
    audit["official_balance_mae_share_of_load"]=audit.candidate_plus_mae_share_of_load
    # A zero/negative or undefined average load cannot normalize an error.
    # Require finite residual diagnostics before any screening-only outcome.
    import numpy as np
    audit["accounting_gate"]=audit.apply(
        lambda r: "review_required" if (
            r.complete_triple_share < 0.99 or
            not np.isfinite(r.official_balance_mae_share_of_load) or
            r.common_demand_mwh <= 0 or
            r.official_balance_mae_share_of_load > 0.10
        ) else "screening_only_not_verified", axis=1)
    return merged,audit

def monthly_balance_audit(frame):
    """Summarize official residuals only over the same valid hourly triples."""
    x=frame.copy()
    x["month"]=pd.to_datetime(x["period"],utc=True).dt.strftime("%Y-%m")
    x["complete_triple"]=x[["demand","generation","interchange"]].notna().all(axis=1)
    valid=x[x.complete_triple].copy()
    monthly=valid.groupby(["respondent","month"],as_index=False).agg(
        common_hours=("period","size"),
        demand_mwh=("demand","sum"),
        generation_mwh=("generation","sum"),
        interchange_mwh=("interchange","sum"),
        official_residual_mwh=("residual_d_minus_ng_plus_ti","sum"),
        official_mae_mw=("residual_d_minus_ng_plus_ti",lambda v:float(v.abs().mean()))
    )
    expected=x.groupby(["respondent","month"]).size().rename("expected_hours").reset_index()
    monthly=expected.merge(monthly,on=["respondent","month"],how="left")
    monthly["missing_triples"]=monthly.expected_hours-monthly.common_hours.fillna(0)
    monthly["coverage"]=monthly.common_hours/monthly.expected_hours
    monthly["residual_share_of_demand"]=monthly.official_residual_mwh/monthly.demand_mwh
    import numpy as np
    monthly["quality_flag"]=monthly.apply(
        lambda row: "review_required" if (
            row.coverage < 0.99 or
            pd.isna(row.demand_mwh) or row.demand_mwh <= 0 or
            not np.isfinite(row.residual_share_of_demand) or
            abs(row.residual_share_of_demand) > 0.10
        ) else "screening_only_not_verified", axis=1)
    return monthly


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--year",type=int,default=2024)
    p.add_argument("--bas",nargs="+",default=["CISO","BPAT"])
    p.add_argument("--output",type=Path,default=Path("outputs/eia930_balance"))
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
    d=fetch_eia_demand(a.year,a.bas)
    ng=fetch_net_generation(a.year,a.bas)
    ti=fetch_ti(a.year,a.bas)
    frame,audit=balance_audit(d,ng,ti,a.bas,a.year)
    frame.to_csv(a.output/"hourly_balance_audit.csv",index=False)
    audit.to_csv(a.output/"ba_balance_summary.csv",index=False)
    monthly_balance_audit(frame).to_csv(a.output/"monthly_balance_audit.csv",index=False)
    (a.output/"provenance.json").write_text(json.dumps({
      "source":API,"types":["D","NG","TI"],
      "official_identity":"Demand = Net Generation - Total Interchange; positive TI is net exports and negative TI is net imports.",
      "official_definition":"https://www.eia.gov/electricity/930-content/about.html",
      "warning":"Demand may include audited imputations; NG/TI incomplete hours retained. Official identity is assessed only on common nonmissing hours. Processing stages of D, NG and TI require independent reconciliation.",
      "interpretation":"D - NG + TI is the official EIA-930 accounting residual. Anomalies may reflect data reporting, pseudo-ties or dynamic schedules; do not infer transmission capacity."
    },indent=2))
    print(audit.to_string(index=False))
if __name__=="__main__":main()
