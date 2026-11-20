"""Full-reference-year 8760h source-only renewable energy transfer mechanism.

Three exact SOC schedules, identical full-year weather/load input:
24h zero-SOC resets, 168h zero-SOC resets (final 24h tail), and 8760h
one zero-terminal year. This is MWh maximization, NOT annual economic LP.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
import h5py,numpy as np,pandas as pd
from energy_transition.paper_s_input_only_weekly_optimal import transport,STUDIES,KEY
from energy_transition.reeds2022_all_weather_year_720lp import WEATHER_YEARS
from energy_transition.reeds2022_four_weather_year_siting_lp import reaggregate_years,DESIGNS,POWER
from energy_transition.reeds2022_county_full_state_lp import modeled_hourly_cf
from energy_transition.reeds2022_county_ac_normalized_2030 import normalized_pv_ac_cf
from energy_transition.reeds_2022_clocked_demand_branch import verify_official_file,check_fixed_cst_native_labels

HORIZONS={"daily":24,"weekly":168,"annual":8760}

def solve_annual(load,cf,ratio):
    load=np.asarray(load,float);cf=np.asarray(cf,float)
    if (load.shape!=(8760,) or cf.shape!=(8760,) or not np.isfinite(load).all()
        or not np.isfinite(cf).all() or load.min()<0 or cf.min()<0 or cf.max()>1
        or ratio<=0 or load.max()<=0):
        raise ValueError("8760 source calendar load/CF validation failure")
    net=ratio*load.max()*cf-load
    surplus=np.maximum(net,0.);deficit=np.maximum(-net,0.)
    power=POWER*load.max()
    row={"source_hours":8760,"source_surplus_mwh":float(surplus.sum()),
         "source_deficit_mwh":float(deficit.sum())}
    for name,hours in HORIZONS.items():
        for duration in (4,8):
            r=transport(surplus,deficit,power,duration,reset_hours=hours)
            row[f"{name}_{duration}h_delivered_mwh"]=r["delivered_mwh"]
            row[f"{name}_{duration}h_charge_mwh"]=r["charged_mwh"]
            row[f"{name}_{duration}h_max_soc_mwh"]=r["max_soc_mwh"]
            row[f"{name}_{duration}h_balance_residual_mwh"]=r["equality_residual_mwh"]
        row[f"{name}_incremental_4to8_mwh"]=(
            row[f"{name}_8h_delivered_mwh"]-row[f"{name}_4h_delivered_mwh"])
        if row[f"{name}_incremental_4to8_mwh"]<-1e-4:
            raise ValueError("8h cannot provide less feasible delivered energy than 4h")
    for duration in (4,8):
        d=row[f"daily_{duration}h_delivered_mwh"]
        w=row[f"weekly_{duration}h_delivered_mwh"]
        a=row[f"annual_{duration}h_delivered_mwh"]
        if d>w+1e-3 or w>a+1e-3:
            raise ValueError("Annual >= weekly >= daily nesting of maximum delivered MWh violated")
    row["annual_minus_daily_incremental_mwh"]=(
        row["annual_incremental_4to8_mwh"]-row["daily_incremental_4to8_mwh"])
    row["annual_minus_weekly_incremental_mwh"]=(
        row["annual_incremental_4to8_mwh"]-row["weekly_incremental_4to8_mwh"])
    return row

def summarize(cases,lp):
    if cases[KEY].duplicated().any():
        raise ValueError("Duplicate yearly source case")
    required=KEY+["wind_share_ac","marginal_4to8_usd_added_kwh_year"]
    if not set(required).issubset(lp.columns):raise ValueError("Frozen LP fields missing")
    filtered=lp.loc[np.isclose(lp.wind_share_ac,.5),required]
    if filtered[KEY].duplicated().any():raise ValueError("Frozen LP keys not unique")
    joined=cases.merge(filtered.drop(columns=["wind_share_ac"]),on=KEY,how="left",
                      validate="one_to_one",indicator=True)
    if not joined._merge.eq("both").all():
        raise ValueError("All input-only rows must have original frozen LP value")
    joined=joined.drop(columns="_merge")
    metrics=[f"{h}_incremental_4to8_mwh" for h in HORIZONS]
    out=[];pairs=[]
    for (state,ratio),g in joined.groupby(["state","renewable_peak_ratio"]):
        paired=g.pivot(index="weather_year",columns="county_weight_scheme",
                       values=metrics+["marginal_4to8_usd_added_kwh_year"])
        target=(paired["marginal_4to8_usd_added_kwh_year"][DESIGNS[1]]-
                paired["marginal_4to8_usd_added_kwh_year"][DESIGNS[0]])
        for year in target.index:
            p={"state":state,"renewable_peak_ratio":ratio,"weather_year":int(year),
               "lp_spatial_effect_usd_kwh_year":float(target.loc[year])}
            for h in HORIZONS:
                m=paired[f"{h}_incremental_4to8_mwh"]
                p[f"{h}_spatial_effect_mwh"]=float((m[DESIGNS[1]]-m[DESIGNS[0]]).loc[year])
            pairs.append(p)
        x={"state":state,"renewable_peak_ratio":ratio,"n_matched_weather_years":len(target),
           "median_lp_spatial_effect_usd_kwh_year":float(target.median())}
        for h in HORIZONS:
            q=paired[f"{h}_incremental_4to8_mwh"]
            delta=q[DESIGNS[1]]-q[DESIGNS[0]]
            x[f"{h}_pearson_spatial_effect"]=(
                float(delta.corr(target))
                if len(target)>=5 and delta.std()>1e-9 and target.std()>1e-9 else np.nan)
            x[f"{h}_sign_agreement"]=int((np.sign(delta)==np.sign(target)).sum())
            x[f"{h}_median_spatial_effect_mwh"]=float(delta.median())
        out.append(x)
    return joined,pd.DataFrame(pairs),pd.DataFrame(out)

def run(wind_h5,pv_h5,wind_sc,pv_sc,county_shares,wind_ref,pv_ref,demand_h5,grid,out,states=("AZ","CO","ID","WY"),years=(2012,2023)):
    studies=[(s,r) for s,r in STUDIES if s in states]
    years=tuple(int(y) for y in years)
    if not studies or not years or len(years)!=len(set(years)) or any(y not in WEATHER_YEARS for y in years):
        raise ValueError("Invalid prespecified study slice")
    verify_official_file(Path(demand_h5))
    wind,_,tw=reaggregate_years(wind_h5,wind_sc,"wind",county_shares,wind_ref,years=WEATHER_YEARS)
    solar,_,tp=reaggregate_years(pv_h5,pv_sc,"pv",county_shares,pv_ref,years=WEATHER_YEARS)
    if not tw.equals(tp):raise ValueError("Wind and solar source clocks do not match")
    rows=[]
    with h5py.File(demand_h5) as h:
        g=h["2030"];check_fixed_cst_native_labels(g["datetime"][:])
        idx=pd.DatetimeIndex(pd.to_datetime([
            x.decode() if isinstance(x,bytes) else str(x) for x in g["datetime"][:]],utc=True))
        if not idx.equals(tw):raise ValueError("2030 demand and renewable source calendars differ")
        for state,ratio in studies:
            load=np.asarray(g[state][:],float)
            for year in years:
                for design in DESIGNS:
                    w=modeled_hourly_cf(wind[(year,design,state)],"trapezoid_with_first_endpoint")
                    p=normalized_pv_ac_cf(modeled_hourly_cf(solar[(year,design,state)],"trapezoid_with_first_endpoint"))
                    row=solve_annual(load,.5*w+.5*p,ratio)
                    rows.append({"state":state,"renewable_peak_ratio":ratio,
                                 "weather_year":year,"county_weight_scheme":design,**row})
                    print("PAPER_S_ANNUAL_INPUT_ONLY_CASE",state,year,design,flush=True)
    joined,pairs,summary=summarize(pd.DataFrame(rows),pd.read_csv(grid))
    if len(joined)!=len(studies)*len(years)*2 or len(pairs)!=len(studies)*len(years):
        raise ValueError("Incomplete source-backed annual case count")
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    joined.to_csv(out/"Y1_annual_input_only_case_results.csv",index=False)
    pairs.to_csv(out/"Y2_annual_paired_siting_effects.csv",index=False)
    summary.to_csv(out/"Y3_annual_group_summary.csv",index=False)
    (out/"Y0_manifest.json").write_text(json.dumps({
        "status":"ANNUAL_INPUT_ONLY_OPTIMAL_TRANSFER_CANDIDATE",
        "case_count":len(joined),"paired_count":len(pairs),"group_count":len(summary),
        "source_hours":8760,"states":[s for s,_ in studies],
        "years":list(years),"source_ac_wind_share":.5,
        "soc_boundaries_hours":{"daily":24,"weekly":168,"annual":8760},
        "weeks_are_52_168h_blocks_plus_final_24h_tail":True,
        "each_block_initial_and_terminal_soc_zero":True,
        "objective":"maximum_exogenous_renewable_surplus_to_deficit_mwh",
        "not_an_economic_objective":True,
        "annual_comparison_aligned_to_fixed_2030_reference_clock":True,
        "does_not_prove_causal_mechanism_or_field_profit":True,
        "frozen_lp_values_not_modified":True},indent=2)+"\n")
    print("PAPER_S_ANNUAL_INPUT_ONLY_TRANSPORT_PASS",len(joined),flush=True)

def main():
    p=argparse.ArgumentParser()
    for name in ("wind_h5","pv_h5","wind_sc","pv_sc","county_shares","wind_ref","pv_ref","demand_h5","grid","out"):
        p.add_argument("--"+name.replace("_","-"),type=Path,required=True)
    p.add_argument("--states",nargs="+",default=["AZ","CO","ID","WY"])
    p.add_argument("--years",nargs="+",type=int,default=[2012,2023])
    run(**vars(p.parse_args()))
if __name__=="__main__":main()
