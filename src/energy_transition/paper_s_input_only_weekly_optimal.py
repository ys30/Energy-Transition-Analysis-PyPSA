"""Input-only chronological surplus-to-deficit LP, 24h vs 168h SOC horizons.
Not a cost optimum, full-year transfer maximum, or causal attribution.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np,pandas as pd,h5py
from scipy.optimize import linprog
from scipy.sparse import coo_matrix
from energy_transition.reeds2022_four_weather_year_siting_lp import reaggregate_years,DESIGNS,POWER,RTE
from energy_transition.reeds2022_all_weather_year_720lp import WEATHER_YEARS
from energy_transition.reeds2022_county_full_state_lp import modeled_hourly_cf
from energy_transition.reeds2022_county_ac_normalized_2030 import normalized_pv_ac_cf
from energy_transition.reeds_2022_clocked_demand_branch import verify_official_file,check_fixed_cst_native_labels

STUDIES=(("AZ",1.5),("CO",2.),("ID",1.5),("WY",1.5))
KEY=["state","renewable_peak_ratio","weather_year","county_weight_scheme"]

def transport(surplus,deficit,power,duration,*,daily=False):
    s=np.asarray(surplus,float);d=np.asarray(deficit,float);n=len(s)
    if (not n or n%24 or s.shape!=d.shape or not np.isfinite(s).all() or not np.isfinite(d).all()
        or (s<0).any() or (d<0).any() or ((s>1e-10)&(d>1e-10)).any()
        or not np.isfinite(power) or not np.isfinite(duration) or power<=0 or duration<=0):
        raise ValueError("Invalid ordered renewable surplus and deficit")
    eta=np.sqrt(RTE);cap=power*duration
    rr=[];cc=[];vv=[];bounds=[]
    def add(r,c,v):rr.append(r);cc.append(c);vv.append(v)
    for t in range(n):
        add(t,3*t,-eta);add(t,3*t+1,1/eta);add(t,3*t+2,1.)
        if t:add(t,3*(t-1)+2,-1.)
        bounds.extend([(0,min(float(s[t]),power)),(0,min(float(d[t]),power)),(0,cap)])
    ends=list(range(23,n,24)) if daily else [n-1]
    for i,t in enumerate(ends):add(n+i,3*t+2,1.)
    A=coo_matrix((vv,(rr,cc)),shape=(n+len(ends),3*n)).tocsr()
    c=np.zeros(3*n);c[1::3]=-1.
    sol=linprog(c,A_eq=A,b_eq=np.zeros(A.shape[0]),bounds=bounds,method="highs")
    if not sol.success:raise RuntimeError("Input-only transport HiGHS: "+sol.message)
    x=sol.x.reshape(n,3);resid=float(np.abs(A@sol.x).max())
    if (resid>1e-5 or (x<-1e-6).any() or x[:,2].max()>cap+1e-5
        or any(abs(x[t,2])>1e-5 for t in ends)):
        raise ValueError("Transport balance/boundary gate failed")
    return {"delivered_mwh":float(x[:,1].sum()),"charged_mwh":float(x[:,0].sum()),
            "max_soc_mwh":float(x[:,2].max()),"equality_residual_mwh":resid}

def one_week(load,cf,ratio,annual_peak):
    load=np.asarray(load,float);cf=np.asarray(cf,float)
    if (load.shape!=(168,) or cf.shape!=(168,) or not np.isfinite(load).all()
        or not np.isfinite(cf).all() or (load<0).any() or (cf<0).any()
        or (cf>1).any() or annual_peak<=0 or ratio<=0):
        raise ValueError("Require authentic contiguous 168h data and annual peak")
    net=ratio*annual_peak*cf-load;s=np.maximum(net,0);d=np.maximum(-net,0)
    p=POWER*annual_peak;z={}
    for horizon in ("daily","weekly"):
        a=transport(s,d,p,4,daily=horizon=="daily")
        b=transport(s,d,p,8,daily=horizon=="daily")
        if a["delivered_mwh"]>b["delivered_mwh"]+1e-4:
            raise ValueError("8h nested feasible set failure")
        z[horizon+"_4h_delivered_mwh"]=a["delivered_mwh"]
        z[horizon+"_8h_delivered_mwh"]=b["delivered_mwh"]
        z[horizon+"_incremental_4to8_mwh"]=b["delivered_mwh"]-a["delivered_mwh"]
        z[horizon+"_equality_residual_mwh"]=max(a["equality_residual_mwh"],b["equality_residual_mwh"])
    for duration in (4,8):
        if z[f"daily_{duration}h_delivered_mwh"]>z[f"weekly_{duration}h_delivered_mwh"]+1e-4:
            raise ValueError("Weekly total must dominate day-reset maximum")
    z["weekly_minus_daily_incremental_4to8_mwh"]=z["weekly_incremental_4to8_mwh"]-z["daily_incremental_4to8_mwh"]
    return z

def report(cases,prior):
    if len(cases)!=120 or cases[KEY].duplicated().any():
        raise ValueError("Expected 120 source scenario cases")
    if not set(KEY+["marginal_4to8_usd_added_kwh_year"]).issubset(prior.columns):
        raise ValueError("Frozen 1080 duration values missing")
    # The frozen design grid contains 1,080 unique cases; this experiment
    # selects 120 of them. Validate uniqueness without requiring identical
    # unfiltered populations or permitting an accidental many-to-many join.
    if prior[KEY].duplicated().any():
        raise ValueError("Duplicate cases in frozen 1,080-row LP grid")
    matched=cases[KEY].merge(
        prior[KEY+["marginal_4to8_usd_added_kwh_year"]],
        on=KEY,how="left",validate="one_to_one",indicator=True)
    if len(matched)!=120 or not matched["_merge"].eq("both").all():
        raise ValueError("Missing frozen LP source matches")
    if not np.isfinite(matched.marginal_4to8_usd_added_kwh_year.to_numpy(dtype=float)).all():
        raise ValueError("Nonfinite frozen LP value in matched subset")
    joined=cases.merge(
        matched.drop(columns=["_merge"]),on=KEY,validate="one_to_one")
    rows=[];pair=[]
    for (state,ratio),g in joined.groupby(["state","renewable_peak_ratio"]):
        if (len(g)!=30 or set(g.weather_year)!=set(WEATHER_YEARS)
            or set(g.county_weight_scheme)!=set(DESIGNS)):
            raise ValueError("Missing weather years/weights")
        p=g.pivot(index="weather_year",columns="county_weight_scheme",values=[
            "daily_incremental_4to8_mwh","weekly_incremental_4to8_mwh",
            "marginal_4to8_usd_added_kwh_year"])
        lp=p["marginal_4to8_usd_added_kwh_year"][DESIGNS[1]]-p["marginal_4to8_usd_added_kwh_year"][DESIGNS[0]]
        row={"state":state,"renewable_peak_ratio":ratio,"weather_years":15,
             "median_annual_lp_spatial_effect":float(lp.median())}
        for horizon in ("daily","weekly"):
            q=p[horizon+"_incremental_4to8_mwh"][DESIGNS[1]]-p[horizon+"_incremental_4to8_mwh"][DESIGNS[0]]
            row[horizon+"_correlation_with_annual_lp"]=float(q.corr(lp)) if q.std()>1e-9 else np.nan
            row[horizon+"_same_sign_years"]=int((np.sign(q)==np.sign(lp)).sum())
            row[horizon+"_median_siting_effect_mwh"]=float(q.median())
            for year in lp.index:
                pair.append({"state":state,"renewable_peak_ratio":ratio,"weather_year":year,
                             "horizon":horizon,"input_only_spatial_effect_mwh":float(q.loc[year]),
                             "full_year_lp_spatial_effect":float(lp.loc[year])})
        rows.append(row)
    if len(rows)!=4 or len(pair)!=120:raise ValueError("Missing mechanism summaries")
    return joined,pd.DataFrame(pair),pd.DataFrame(rows)

def run(wind_h5,pv_h5,wind_sc,pv_sc,county_shares,wind_ref,pv_ref,demand_h5,grid,out,start_hour=0):
    if start_hour<0 or start_hour+168>8760 or start_hour%24:raise ValueError("Invalid source week start")
    verify_official_file(Path(demand_h5))
    wind,_,tw=reaggregate_years(wind_h5,wind_sc,"wind",county_shares,wind_ref,years=WEATHER_YEARS)
    pv,_,tp=reaggregate_years(pv_h5,pv_sc,"pv",county_shares,pv_ref,years=WEATHER_YEARS)
    if not tw.equals(tp):raise ValueError("Source clock mismatch")
    rows=[]
    with h5py.File(demand_h5) as h:
        g=h["2030"];check_fixed_cst_native_labels(g["datetime"][:])
        idx=pd.DatetimeIndex(pd.to_datetime([v.decode() if isinstance(v,bytes) else str(v) for v in g["datetime"][:]],utc=True))
        if not idx.equals(tw):raise ValueError("2030 reference demand clock mismatch")
        for state,ratio in STUDIES:
            demand=np.asarray(g[state][:],float);peak=float(demand.max())
            if demand.shape!=(8760,) or peak<=0:raise ValueError("Demand length/peak drift")
            for year in WEATHER_YEARS:
                for scheme in DESIGNS:
                    w=modeled_hourly_cf(wind[(year,scheme,state)],"trapezoid_with_first_endpoint")
                    p=normalized_pv_ac_cf(modeled_hourly_cf(pv[(year,scheme,state)],"trapezoid_with_first_endpoint"))
                    mix=.5*w+.5*p
                    row=one_week(demand[start_hour:start_hour+168],mix[start_hour:start_hour+168],ratio,peak)
                    rows.append({"state":state,"renewable_peak_ratio":ratio,"weather_year":year,
                                 "county_weight_scheme":scheme,"fixed_hour_start":start_hour,**row})
    cases,pair,summary=report(pd.DataFrame(rows),pd.read_csv(grid))
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    cases.to_csv(out/"W1_120_source_week_cases.csv",index=False)
    pair.to_csv(out/"W2_120_paired_horizon_rows.csv",index=False)
    summary.to_csv(out/"W3_four_state_horizon_summary.csv",index=False)
    (out/"W0_manifest.json").write_text(json.dumps({
        "cases":len(cases),"paired_rows":len(pair),"state_groups":len(summary),
        "source_hours_per_case":168,"fixed_reference_hour_start":start_hour,
        "both_horizons_initial_and_terminal_soc_zero":True,
        "daily_horizon_is_seven_24h_independent_cycles":True,
        "weekly_horizon_is_one_contiguous_168h_cycle":True,
        "objective_is_maximum_renewable_surplus_served_deficit_not_cost":True,
        "comparison_to_full_year_lp_is_descriptive_only":True,
        "weekly_minus_daily_4to8_increment_need_not_be_positive":True,
        "full_year_maximum_renewable_delivery_claimed":False},indent=2)+"\n")
    print("PAPER_S_168H_INPUT_ONLY_TRANSPORT_120_CASES_PASS",len(cases))

def main():
    p=argparse.ArgumentParser()
    for name in ("wind_h5","pv_h5","wind_sc","pv_sc","county_shares","wind_ref","pv_ref","demand_h5","grid","out"):
        p.add_argument("--"+name.replace("_","-"),type=Path,required=True)
    p.add_argument("--start-hour",type=int,default=0)
    run(**vars(p.parse_args()))
if __name__=="__main__":main()
