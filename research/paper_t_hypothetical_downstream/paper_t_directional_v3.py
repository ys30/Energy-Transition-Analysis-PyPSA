"""Paper T bidirectional sensitivity: fully synthetic, not actual EFS/ReEDS hours."""
import argparse,csv,json
from pathlib import Path
from paper_t_robustness import build_scenario,shifted,calculate,SOLAR_SCALES,EVENING_PEAK_HOURS
LAGS=(-3,-2,0,2,3)
SOLAR_PHASE_SHIFTS=(-2,0,2)
def run():
    rows=[]
    for scale in SOLAR_SCALES:
      for peak in EVENING_PEAK_HOURS:
       demand,original_solar=build_scenario(scale,peak)
       for phase in SOLAR_PHASE_SHIFTS:
        solar=shifted(original_solar,phase)
        baseline=calculate(demand,solar,0)
        for lag in LAGS:
         r=calculate(demand,solar,lag)
         rows.append(dict(solar_scale=scale,evening_peak_hour=peak,
          solar_phase_shift_h=phase,demand_shift_h=lag,
          net_peak_mw=r['net_peak_mw'],net_peak_hour=r['net_peak_clock_hour'],
          peak_delta_mw=round(r['net_peak_mw']-baseline['net_peak_mw'],6),
          peak_delta_pct=round(100*(r['net_peak_mw']/baseline['net_peak_mw']-1),6),
          solar_overlap_pct=round(100*r['solar_overlap_fraction'],6),
          overlap_delta_pp=round(100*(r['solar_overlap_fraction']-baseline['solar_overlap_fraction']),6),
          solar_surplus_mwh=r['solar_surplus_mwh'],
          demand_energy_mwh=r['demand_energy_mwh'],solar_energy_mwh=r['solar_energy_mwh']))
    return rows
def summary(rows):
    out=[]
    for lag in LAGS:
     x=[r for r in rows if r['demand_shift_h']==lag]
     out.append(dict(demand_shift_h=lag,cases=len(x),
      peak_increase=sum(r['peak_delta_pct']>1e-6 for r in x),
      peak_decrease=sum(r['peak_delta_pct']< -1e-6 for r in x),
      peak_unchanged=sum(abs(r['peak_delta_pct'])<=1e-6 for r in x),
      peak_delta_pct_min=round(min(r['peak_delta_pct'] for r in x),4),
      peak_delta_pct_max=round(max(r['peak_delta_pct'] for r in x),4),
      overlap_increase=sum(r['overlap_delta_pp']>1e-6 for r in x),
      overlap_decrease=sum(r['overlap_delta_pp']< -1e-6 for r in x),
      overlap_delta_pp_min=round(min(r['overlap_delta_pp'] for r in x),4),
      overlap_delta_pp_max=round(max(r['overlap_delta_pp'] for r in x),4)))
    return out
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--outdir',type=Path,default=Path('results/paper_t_hypothetical_downstream/directional_v3'))
    out=ap.parse_args().outdir
    out.mkdir(parents=True,exist_ok=True)
    rows=run()
    with (out/'directional_grid.csv').open('w',newline='') as f:
     w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
    (out/'summary.json').write_text(json.dumps({'status':'SYNTHETIC ONLY, not an EFS/ReEDS timestamp join',
     'n_cases':len(rows),'solar_scales':SOLAR_SCALES,'evening_peak_hours':EVENING_PEAK_HOURS,
     'solar_phase_shifts_h':SOLAR_PHASE_SHIFTS,'demand_shifts_h':LAGS,
     'summary':summary(rows)},indent=2)+'\n')
    print(json.dumps(summary(rows),indent=2))
if __name__=='__main__':main()
