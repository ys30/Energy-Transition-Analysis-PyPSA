"""Paper T: SYNTHETIC-ONLY factorial time-shift sensitivity. No real hourly join."""
import argparse, csv, json, math
from pathlib import Path
N=8760
SOLAR_SCALES=(0.5,1.0,1.5,2.0)
EVENING_PEAK_HOURS=(16,18,19,20,22)
LAGS=(0,-2,-3)
def build_scenario(scale, evening_hour):
    demand=[];solar=[]
    for t in range(N):
        day,hour=divmod(t,24)
        summer=(1+math.cos(2*math.pi*(day-200)/365))/2
        evening=math.exp(-0.5*((hour-evening_hour)/3.2)**2)
        morning=math.exp(-0.5*((hour-8)/2.2)**2)
        demand.append(850+150*summer+300*evening+90*morning)
        daylight=max(0.,math.sin(math.pi*(hour-6)/12))
        solar.append(scale*(850+450*summer)*daylight**1.65)
    return demand,solar
def shifted(x,lag):
    return [x[(t-lag)%len(x)] for t in range(len(x))]
def calculate(demand,solar,lag):
    d=shifted(demand,lag)
    net=[a-b for a,b in zip(d,solar)]
    overlap=sum(min(a,b) for a,b in zip(d,solar))
    return dict(lag_h=lag,net_peak_mw=round(max(net),6),
      net_peak_hour=net.index(max(net))%24,
      demand_energy_mwh=round(sum(d),6),
      solar_energy_mwh=round(sum(solar),6),
      overlap_pct=round(100*overlap/sum(solar),6),
      solar_surplus_mwh=round(sum(max(0,b-a) for a,b in zip(d,solar)),6))
def run():
    rows=[]
    for scale in SOLAR_SCALES:
        for hour in EVENING_PEAK_HOURS:
            d,s=build_scenario(scale,hour)
            vals=[calculate(d,s,lag) for lag in LAGS]
            base=vals[0]
            for r in vals:
                r.update(solar_scale=scale,evening_peak_hour=hour,
                 peak_delta_pct=round(100*(r['net_peak_mw']/base['net_peak_mw']-1),6),
                 overlap_delta_pp=round(r['overlap_pct']-base['overlap_pct'],6))
                rows.append(r)
    return rows
def summarize(rows):
    output=[]
    for lag in (-2,-3):
        x=[r for r in rows if r['lag_h']==lag]
        output.append(dict(lag_h=lag, scenarios=len(x),
          peak_decrease=sum(r['peak_delta_pct'] < -1e-7 for r in x),
          peak_unchanged=sum(abs(r['peak_delta_pct']) <= 1e-7 for r in x),
          peak_increase=sum(r['peak_delta_pct'] > 1e-7 for r in x),
          peak_delta_range_pct=[min(r['peak_delta_pct'] for r in x),max(r['peak_delta_pct'] for r in x)],
          overlap_increase=sum(r['overlap_delta_pp'] > 1e-7 for r in x),
          overlap_delta_range_pp=[min(r['overlap_delta_pp'] for r in x),max(r['overlap_delta_pp'] for r in x)]))
    return output
def main():
    p=argparse.ArgumentParser()
    p.add_argument('--outdir',type=Path,default=Path('results/paper_t_hypothetical_downstream/robustness'))
    out=p.parse_args().outdir
    out.mkdir(parents=True,exist_ok=True)
    rows=run()
    with (out/'robustness_grid.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    (out/'summary.json').write_text(json.dumps({'classification':'HYPOTHETICAL SYNTHETIC-ONLY',
      'not_a_real_EFS_ReEDS_join':True,'summary':summarize(rows)},indent=2)+'\n')
    print(json.dumps(summarize(rows),indent=2))
if __name__=='__main__':main()
