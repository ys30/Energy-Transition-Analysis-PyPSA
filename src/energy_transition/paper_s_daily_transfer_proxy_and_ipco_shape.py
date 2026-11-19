"""Paper S: genuine 2023 source-year IPCO BA shape proxy and daily energy proxy.
All scientific gates fail closed. Proxy is NOT physical delivered 4->8h energy.
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
import h5py,numpy as np,pandas as pd
from energy_transition.reeds2022_four_weather_year_siting_lp import reaggregate_years,DESIGNS,POWER,RTE,HOURS
from energy_transition.reeds2022_all_weather_year_720lp import WEATHER_YEARS
from energy_transition.reeds2022_eia2025_spatial_reweighted_lp import county_tech_weights
from energy_transition.reeds2022_county_state_resources import validate_capacity_key_match
from energy_transition.reeds2022_real_resource_intake import require_md5,decode
from energy_transition.reeds2022_county_full_state_lp import modeled_hourly_cf
from energy_transition.reeds2022_county_ac_normalized_2030 import normalized_pv_ac_cf
from energy_transition.reeds_2022_clocked_demand_branch import verify_official_file,check_fixed_cst_native_labels

PINS={"wind":("0670813d0a18b688d698ca24cf67fb92","49ab4e41dc386453b5fd32e5810774d4"),
      "pv":("aba834ea4c592023bca47de2ba79e7ec","e10b1a64f3a67d163e739b735938eb78")}
KEY=["state","weather_year","renewable_peak_ratio","wind_share_ac","county_weight_scheme"]
TZ="Etc/GMT+6"

def daily_proxy(load,cf,ratio=1.5):
    """Day-restricted instantaneous-available surplus, not an implementable schedule.
    Battery power and chronological surplus/deficit ordering are NOT enforced.
    It is NOT an upper bound on a full-year LP allowing cross-day energy.
    """
    load=np.asarray(load,float);cf=np.asarray(cf,float)
    if load.shape!=(8760,) or cf.shape!=(8760,) or np.any((cf<0)|(cf>1)) or np.any(load<0):
        raise ValueError("Invalid source daily arrays")
    available=ratio*load.max()*cf
    surplus=np.maximum(available-load,0).reshape(365,24).sum(axis=1)
    deficit=np.maximum(load-available,0).reshape(365,24).sum(axis=1)
    eta_d=np.sqrt(RTE)
    usable=np.minimum(RTE*surplus,deficit)
    four=4*POWER*load.max()*eta_d
    eight=8*POWER*load.max()*eta_d
    return pd.DataFrame({"fixed_2012_support_day":np.arange(1,366),
        "surplus_mwh":surplus,"deficit_mwh":deficit,
        "unconstrained_same_day_deliverable_mwh":usable,
        "incremental_4to8_daily_proxy_mwh":np.clip(usable-four,0,eight-four)})

def chronological_daily_policy(load, cf, ratio=1.5, duration_h=4.):
    """Feasible deterministic surplus-first hourly policy; independently of LP prices.

    Reset SOC to zero each 24h block. This policy never imports firm
    generation for charging and never stores across days. Not a globally
    optimal 24h or annual dispatch, nor an upper bound for the full-year LP.
    """
    load=np.asarray(load,float);cf=np.asarray(cf,float)
    if (load.shape!=(8760,) or cf.shape!=(8760,) or
        not np.isfinite(load).all() or not np.isfinite(cf).all() or
        (load<0).any() or (cf<-1e-10).any() or (cf>1+1e-10).any() or
        ratio<=0 or duration_h<=0):
        raise ValueError("Invalid chronological source arrays")
    eta=np.sqrt(RTE)
    power=POWER*load.max()
    cap=power*duration_h
    net=ratio*load.max()*cf-load
    delivered=np.zeros(365,float)
    input_charge=np.zeros(365,float)
    wasted_soc=np.zeros(365,float)
    max_balance_error=0.
    for day in range(365):
        soc=0.
        for net_mw in net[day*24:(day+1)*24]:
            before=soc
            if net_mw>=0:
                charge=min(float(net_mw),power,max(0.,(cap-soc)/eta))
                soc+=eta*charge
                input_charge[day]+=charge
                err=abs(soc-before-eta*charge)
            else:
                discharge=min(float(-net_mw),power,max(0.,soc*eta))
                soc-=discharge/eta
                delivered[day]+=discharge
                err=abs(soc-before+discharge/eta)
            max_balance_error=max(max_balance_error,err)
            if soc < -1e-5 or soc > cap+1e-5:
                raise ValueError("Chronological policy SOC bounds violated")
        wasted_soc[day]=max(0.,soc)
    if max_balance_error>1e-6:
        raise ValueError("Chronological policy balance failure")
    return pd.DataFrame({
        "fixed_2012_support_day":np.arange(1,366),
        "delivered_deficit_mwh":delivered,
        "accepted_surplus_charge_mwh":input_charge,
        "end_of_day_discarded_soc_mwh":wasted_soc,
    })


def chronological_comparison(load,cf,ratio=1.5):
    """Same exogenous renewable/load inputs; separate feasible 4h/8h policies."""
    four=chronological_daily_policy(load,cf,ratio,4.)
    eight=chronological_daily_policy(load,cf,ratio,8.)
    out=pd.DataFrame({
        "fixed_2012_support_day":four.fixed_2012_support_day,
        "four_h_feasible_delivered_mwh":four.delivered_deficit_mwh,
        "eight_h_feasible_delivered_mwh":eight.delivered_deficit_mwh,
        "four_h_end_day_soc_discard_mwh":four.end_of_day_discarded_soc_mwh,
        "eight_h_end_day_soc_discard_mwh":eight.end_of_day_discarded_soc_mwh,
    })
    out["incremental_eight_minus_four_policy_delivered_mwh"]=(
        out.eight_h_feasible_delivered_mwh-out.four_h_feasible_delivered_mwh)
    if (out.incremental_eight_minus_four_policy_delivered_mwh < -1e-5).any():
        raise ValueError("Larger energy capacity unexpectedly decreased greedy delivered energy")
    return out


def daily_run(wind_h5,pv_h5,wind_sc,pv_sc,county_shares,wind_ref,pv_ref,demand_h5,grid,out):
    verify_official_file(Path(demand_h5))
    wind,_,tw=reaggregate_years(wind_h5,wind_sc,"wind",county_shares,wind_ref,years=WEATHER_YEARS)
    solar,_,tp=reaggregate_years(pv_h5,pv_sc,"pv",county_shares,pv_ref,years=WEATHER_YEARS)
    if not tw.equals(tp):raise ValueError("Wind/PV model source index drift")
    records=[];day_records=[];chronological_rows=[];chronological_days=[]
    with h5py.File(demand_h5) as h:
        group=h["2030"];check_fixed_cst_native_labels(group["datetime"][:])
        idx=pd.DatetimeIndex(pd.to_datetime([x.decode() if isinstance(x,bytes) else str(x)
                                             for x in group["datetime"][:]],utc=True))
        if not idx.equals(tw):raise ValueError("2030 fixed reference demand clock mismatch")
        for state in ("AZ","CO","ID","WY"):
            load=np.asarray(group[state][:],float)
            for yr in WEATHER_YEARS:
                for scheme in DESIGNS:
                    w=modeled_hourly_cf(wind[(yr,scheme,state)],"trapezoid_with_first_endpoint")
                    p=normalized_pv_ac_cf(modeled_hourly_cf(solar[(yr,scheme,state)],"trapezoid_with_first_endpoint"))
                    cf=.5*w+.5*p
                    for ratio in (1.5,2.):
                        d=daily_proxy(load,cf,ratio)
                        chrono=chronological_comparison(load,cf,ratio)
                        chronological_rows.append(dict(
                            state=state,weather_year=yr,county_weight_scheme=scheme,
                            renewable_peak_ratio=ratio,wind_share_ac=.5,
                            annual_feasible_policy_4to8_delta_mwh=float(chrono.incremental_eight_minus_four_policy_delivered_mwh.sum()),
                            days_positive_feasible_policy=int((chrono.incremental_eight_minus_four_policy_delivered_mwh>1e-8).sum()),
                            policy_total_four_h_delivered_mwh=float(chrono.four_h_feasible_delivered_mwh.sum()),
                            policy_total_eight_h_delivered_mwh=float(chrono.eight_h_feasible_delivered_mwh.sum())))
                        key=dict(state=state,weather_year=yr,county_weight_scheme=scheme,
                                 renewable_peak_ratio=ratio,wind_share_ac=.5)
                        records.append({**key,"annual_daily_transfer_proxy_mwh":float(d.incremental_4to8_daily_proxy_mwh.sum()),
                                        "days_with_nonzero_proxy":int((d.incremental_4to8_daily_proxy_mwh>0).sum())})
                        for k,v in key.items():
                            d[k]=v
                            chrono[k]=v
                        day_records.append(d)
                        chronological_days.append(chrono)
    x=pd.DataFrame(records);days=pd.concat(day_records,ignore_index=True)
    chron=pd.DataFrame(chronological_rows)
    chronological_day_frame=pd.concat(chronological_days,ignore_index=True)
    if len(chron)!=240 or len(chronological_day_frame)!=87600 or chron.duplicated(KEY).any():
        raise ValueError("Chronological output coverage incomplete")
    if len(x)!=240 or len(days)!=240*365 or x.duplicated(KEY).any():raise ValueError("Missing source cases")
    year=x.pivot(index=KEY[:4],columns="county_weight_scheme",values="annual_daily_transfer_proxy_mwh")
    if year.isna().any().any():raise ValueError("Missing matching siting weight")
    paired=year.reset_index()
    paired["EIA_minus_potential_proxy_mwh"]=paired[DESIGNS[1]]-paired[DESIGNS[0]]
    prior=pd.read_csv(grid)
    expected=set(KEY+["marginal_4to8_usd_added_kwh_year","firm_generation_4h_mwh","firm_generation_8h_mwh"])
    if not expected.issubset(prior.columns):raise ValueError("Not an original 1080 duration outcome CSV")
    prior=prior[prior.renewable_peak_ratio.isin((1.5,2.))&prior.wind_share_ac.eq(.5)]
    joined=x.merge(prior[list(expected)],on=KEY,validate="one_to_one")
    if len(joined)!=240:raise ValueError("Missing actual frozen LP outcomes")
    joined["actual_4to8_firm_displacement_mwh"]=joined.firm_generation_4h_mwh-joined.firm_generation_8h_mwh
    chron_join=chron.merge(prior[list(expected)],on=KEY,validate="one_to_one")
    if len(chron_join)!=240:raise ValueError("Chronological policy missing LP comparisons")
    chron_join["actual_lp_firm_displacement_mwh"]=(
        chron_join.firm_generation_4h_mwh-chron_join.firm_generation_8h_mwh)
    pairing=chron_join.pivot(index=KEY[:4],columns="county_weight_scheme",
        values=["annual_feasible_policy_4to8_delta_mwh","marginal_4to8_usd_added_kwh_year"])
    if len(pairing)!=120 or pairing.isna().any().any():
        raise ValueError("Chronological paired LP comparison coverage failure")
    paired_chron=pairing.reset_index()
    paired_chron.columns=["_".join(str(y) for y in x if y != "") if isinstance(x,tuple) else x for x in paired_chron.columns]
    paired_chron["policy_eia_minus_potential_mwh"]=(
        paired_chron["annual_feasible_policy_4to8_delta_mwh_"+DESIGNS[1]]-
        paired_chron["annual_feasible_policy_4to8_delta_mwh_"+DESIGNS[0]])
    paired_chron["value_eia_minus_potential_usd_kwh_year"]=(
        paired_chron["marginal_4to8_usd_added_kwh_year_"+DESIGNS[1]]-
        paired_chron["marginal_4to8_usd_added_kwh_year_"+DESIGNS[0]])
    folder=Path(out);folder.mkdir(parents=True,exist_ok=True)
    for filename,data in (("D1_daily_proxy_cases.csv",x),("D2_daily_proxy_source_days.csv.gz",days),
                          ("D3_daily_proxy_within_year_paired.csv",paired),
                          ("D4_proxy_vs_actual_frozen_LP.csv",joined),
                          ("C1_chronological_policy_240_cases.csv",chron),
                          ("C2_chronological_policy_87600_days.csv.gz",chronological_day_frame),
                          ("C3_chronological_policy_vs_LP.csv",chron_join),
                          ("C4_chronological_policy_120_paired_differences.csv",paired_chron)):
        data.to_csv(folder/filename,index=False,compression="gzip" if filename.endswith(".gz") else None)
    (folder/"D0_manifest.json").write_text(json.dumps({
        "data_kind":"daily_surplus_deficit_mechanism_proxy_NOT_LP_dispatch",
        "all_years_mapped_to_fixed_2012_calendar":True,
        "2030_fixed_reference_load":True,"new_LP_solved":False,
        "same_day_proxy_ignores_intra_day_sequence":True,
        "same_day_proxy_ignores_charging_power":True,
        "same_day_proxy_ignores_cross_day_SOC":True,
        "chronological_policy_is_input_only":True,
        "chronological_policy_hourly_power_soc_feasible":True,
        "chronological_policy_daily_empty_initial_soc":True,
        "chronological_policy_daily_terminal_soc_discarded":True,
        "chronological_policy_is_NOT_global_optimum":True,
        "chronological_policy_is_NOT_full_year_upper_bound":True},indent=2)+"\n")
    print("PAPER_S_DAILY_PROXY_240_CASES_VERIFIED",len(days),flush=True)

def original_2023(h5,sc,tech,site_csv):
    """2023 original native CST, NO conversion through synthetic 2012 weather support."""
    require_md5(h5,PINS[tech][0]);require_md5(sc,PINS[tech][1])
    src=pd.read_csv(sc,dtype=str)
    if list(src.columns)!=["class|region","MW"]:raise ValueError("Supply-curve format mismatch")
    site=pd.read_csv(site_csv,dtype={"county_fips":"string"})
    with h5py.File(h5) as f:
        native=pd.DatetimeIndex(pd.to_datetime(decode(f["index_0"][:]),errors="raise"))
        if native.isna().any() or native.has_duplicates:raise ValueError("Native source datetime invalid")
        if native.tz is None:utc=native.tz_localize(TZ).tz_convert("UTC")
        else:
            if any(t.utcoffset().total_seconds()!=-21600 for t in native):
                raise ValueError("Publisher time offset not fixed CST")
            utc=native.tz_convert("UTC")
        indices=np.flatnonzero(native.year==2023)
        if len(indices)!=8760 or not np.array_equal(indices,np.arange(indices[0],indices[0]+8760)):
            raise ValueError("No complete original 2023 native weather-year support")
        cols=decode(f["columns"][:])
        key=validate_capacity_key_match(cols,src["class|region"].tolist(),
                    pd.to_numeric(src.MW,errors="raise"),
                    capacity_basis="dc" if tech=="pv" else "ac",tech=tech)
        if list(key.column)!=cols:raise ValueError("HDF source column order drift")
        weights=county_tech_weights(key,site,tech,"ID")
        outputs={k:np.empty(8760) for k in DESIGNS}
        for off in range(0,8760,168):
            block=np.asarray(f["data"][indices[off:off+168],:],float)
            if not np.isfinite(block).all() or block.min()<-1e-12 or block.max()>1+1e-8:
                raise ValueError("Invalid authentic 2023 native CF")
            for k,w in zip(DESIGNS,weights):outputs[k][off:off+len(block)]=block@w
    if tech=="pv":outputs={k:normalized_pv_ac_cf(v) for k,v in outputs.items()}
    return pd.DataFrame({"utc":utc[indices],**outputs})

def shape_metrics(obs,model):
    obs=np.asarray(obs,float);model=np.asarray(model,float)
    if len(obs)<1000 or not np.isfinite(obs).all() or not np.isfinite(model).all() or obs.mean()<=0 or model.mean()<=0:
        raise ValueError("Invalid or zero-mean measured vs predicted same-hour shape")
    a=obs/obs.mean();b=model/model.mean()
    return dict(pearson=float(np.corrcoef(a,b)[0,1]),
                normalized_MAE=float(np.mean(np.abs(a-b))),
                normalized_RMSE=float(np.sqrt(np.mean((a-b)**2))))

def ipco_run(wind_h5,pv_h5,wind_sc,pv_sc,county_shares,observations,out):
    data=pd.read_csv(observations)
    if not {"ba_code","fuel","utc_hour_end","reported_mw","adjusted_mw"}.issubset(data.columns):
        raise ValueError("Missing authenticated EIA930 fields")
    observed=data[data.ba_code.eq("IPCO")&data.fuel.isin(["solar","wind"])].copy()
    observed["utc_hour_end"]=pd.to_datetime(observed.utc_hour_end,utc=True)
    if len(observed)<16000 or observed.duplicated(["fuel","utc_hour_end"]).any():
        raise ValueError("Invalid full-year IPCO EIA930 source population")
    rows=[];coverage=[];diurnal=[];duration=[];all_pairs=[]
    for fuel,tech in (("wind","wind"),("solar","pv")):
        pred=original_2023(wind_h5 if tech=="wind" else pv_h5,
                           wind_sc if tech=="wind" else pv_sc,tech,county_shares)
        observed_fuel=observed[observed.fuel.eq(fuel)]
        for shift in (0,-1,1,-6,6):
            v=pred.copy();v["utc"]=v.utc+pd.Timedelta(hours=shift)
            j=v.merge(observed_fuel,left_on="utc",right_on="utc_hour_end",validate="one_to_one")
            if len(j)<8500:raise ValueError("Unexpected 2023 UTC source join coverage")
            for variant in ("reported_mw","adjusted_mw"):
                for filter_name in ("all_finite","nonnegative_observed"):
                    selected=j[variant].notna()&np.isfinite(j[variant])
                    if filter_name=="nonnegative_observed":selected&=j[variant].ge(0)
                    f=j.loc[selected].copy()
                    coverage.append(dict(fuel=fuel,shift_hours=shift,variant=variant,
                                         filter_name=filter_name,joined_hours=len(j),usable_hours=len(f),
                                         negative_source_rows=int(j[variant].lt(0).sum())))
                    if len(f)<1000:continue
                    for scheme in DESIGNS:
                        try:m=shape_metrics(f[variant],f[scheme])
                        except ValueError:continue
                        rows.append(dict(fuel=fuel,shift_hours=shift,variant=variant,
                                         filter_name=filter_name,scheme=scheme,n=len(f),**m))
                        if shift==0 and variant=="adjusted_mw" and filter_name=="nonnegative_observed":
                            f["a"]=f[variant]/f[variant].mean()
                            f["b"]=f[scheme]/f[scheme].mean()
                            f["cst_hour"]=f.utc.dt.tz_convert(TZ).dt.hour
                            for hr,g in f.groupby("cst_hour"):
                                diurnal.append(dict(fuel=fuel,scheme=scheme,cst_hour=int(hr),
                                    observed_mean=float(g.a.mean()),predicted_mean=float(g.b.mean())))
                            a=np.sort(f.a.values)[::-1];b=np.sort(f.b.values)[::-1]
                            for q in np.linspace(0,1,101):
                                pos=int(q*(len(a)-1))
                                duration.append(dict(fuel=fuel,scheme=scheme,descending_quantile=float(q),
                                    observed_norm=float(a[pos]),predicted_norm=float(b[pos])))
        ref=pred.merge(observed_fuel,left_on="utc",right_on="utc_hour_end",validate="one_to_one")
        ref["fuel"]=fuel;all_pairs.append(ref)
    result=pd.DataFrame(rows)
    if result.empty:raise ValueError("No actual observed shape comparisons")
    compare=result.pivot(index=["fuel","shift_hours","variant","filter_name"],
                         columns="scheme",values="pearson").reset_index()
    compare["EIA_minus_potential_pearson"]=compare[DESIGNS[1]]-compare[DESIGNS[0]]
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    for filename,d in (("I1_IPCO_metrics.csv",result),("I2_IPCO_source_hours.csv",pd.DataFrame(coverage)),
        ("I3_IPCO_UTC_shift_placebos.csv",compare),("I4_IPCO_hour_of_day.csv",pd.DataFrame(diurnal)),
        ("I5_IPCO_duration_shapes.csv",pd.DataFrame(duration)),
        ("I6_IPCO_original2023_matched_pairs.csv.gz",pd.concat(all_pairs,ignore_index=True))):
        d.to_csv(out/filename,index=False,compression="gzip" if filename.endswith(".gz") else None)
    (out/"I0_manifest.json").write_text(json.dumps({
       "status":"EXPLORATORY_BA_STATE_SHAPE_PROXY_NOT_VERIFIED_EXTERNAL_VALIDATION",
       "source_year":2023,"native_fixed_CST_UTC_offset_hours":-6,
       "source_CF_instantaneous_vs_EIA_hourly_reported":True,
       "shape_normalized_on_each_same_valid_hour_support":True,
       "2025_weighted_ID_state_not_equal_2023_IPCO_BA":True,
       "zero_capacity_denominator_required":False,"no_claim_of_actual_2023_fleet_skill":True},indent=2)+"\n")
    print("PAPER_S_IPCO_NATIVE_2023_SHAPE_DIAGNOSTIC_COMPLETE",len(result),flush=True)

def main():
    p=argparse.ArgumentParser()
    for s in ("wind_h5","pv_h5","wind_sc","pv_sc","county_shares","out"):
        p.add_argument("--"+s.replace("_","-"),type=Path,required=True)
    for s in ("wind_ref","pv_ref","demand_h5","frozen_grid","observed"):
        p.add_argument("--"+s.replace("_","-"),type=Path)
    p.add_argument("--mode",required=True,choices=("daily","ipco"))
    a=p.parse_args()
    if a.mode=="daily":
        if any(getattr(a,k) is None for k in ("wind_ref","pv_ref","demand_h5","frozen_grid")):
            raise ValueError("Daily mode requires original 2012 clock and frozen LP outcomes")
        daily_run(a.wind_h5,a.pv_h5,a.wind_sc,a.pv_sc,a.county_shares,
                  a.wind_ref,a.pv_ref,a.demand_h5,a.frozen_grid,a.out)
    else:
        if a.observed is None:raise ValueError("IPCO mode requires full-year EIA930 source observations")
        ipco_run(a.wind_h5,a.pv_h5,a.wind_sc,a.pv_sc,a.county_shares,a.observed,a.out)
if __name__=="__main__":main()
