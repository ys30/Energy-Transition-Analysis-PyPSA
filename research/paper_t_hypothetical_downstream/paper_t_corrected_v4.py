"""Paper T v4 synthetic-only seasonal daylight sensitivity; no real EFS/ReEDS hourly join."""
import argparse,csv,json
from pathlib import Path
import numpy as np
SCALES=(.5,1.,1.5,2.); PEAK_HOURS=(16,18,19,20,22); PHASES=(-2,0,2); LAGS=(-3,-2,0,2,3); N=8760
def profiles(peak_hour,scale,phase,mode="seasonal"):
 t=np.arange(N);day=t//24;h=t%24
 summer=(1+np.cos(2*np.pi*(day-200)/365))/2
 load=850+150*summer+300*np.exp(-.5*((h-peak_hour)/3.2)**2)+90*np.exp(-.5*((h-8)/2.2)**2)
 if mode=="seasonal":
  d=9+6*summer; pv=(850+450*summer)*np.maximum(0,np.sin(np.pi*(h-(12-d/2))/d))**1.65
 elif mode=="legacy":
  pv=(850+450*summer)*np.maximum(0,np.sin(np.pi*(h-6)/12))**1.65
 else:raise ValueError(mode)
 return load,np.roll(pv*scale,phase)
def calc(load,pv,lag):
 d=np.roll(load,lag);net=d-pv; idx=int(np.argmax(net))
 return dict(peak_mw=float(net[idx]),pv_at_peak_mw=float(pv[idx]),
 overlap_pct=float(100*np.minimum(d,pv).sum()/pv.sum()),
 annual_demand_mwh=float(d.sum()),annual_solar_mwh=float(pv.sum()))
def run(mode="seasonal"):
 out=[]
 for h in PEAK_HOURS:
  for phase in PHASES:
   for scale in SCALES:
    load,pv=profiles(h,scale,phase,mode);ref=calc(load,pv,0)
    for lag in LAGS:
     v=calc(load,pv,lag)
     out.append(dict(profile=mode,evening_peak_hour=h,solar_phase_h=phase,solar_scale=scale,
      demand_shift_h=lag,peak_mw=v["peak_mw"],peak_delta_mw=v["peak_mw"]-ref["peak_mw"],
      peak_delta_pct=100*(v["peak_mw"]/ref["peak_mw"]-1),pv_at_peak_mw=v["pv_at_peak_mw"],
      overlap_pct=v["overlap_pct"],overlap_delta_pp=v["overlap_pct"]-ref["overlap_pct"],
      annual_demand_mwh=v["annual_demand_mwh"],annual_solar_mwh=v["annual_solar_mwh"]))
 return out
def diagnose(rows):
 out=[]
 for h in PEAK_HOURS:
  for phase in PHASES:
   for lag in LAGS:
    r=[x for x in rows if (x["evening_peak_hour"],x["solar_phase_h"],x["demand_shift_h"])==(h,phase,lag)]
    out.append(dict(evening_peak_hour=h,solar_phase_h=phase,demand_shift_h=lag,
     peak_spread_mw=max(x["peak_mw"] for x in r)-min(x["peak_mw"] for x in r),
     delta_spread_mw=max(x["peak_delta_mw"] for x in r)-min(x["peak_delta_mw"] for x in r),
     any_pv_at_peak=any(x["pv_at_peak_mw"]>1e-8 for x in r)))
 return out
def write_csv(path,rows):
 with open(path,"w",newline="") as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--outdir",type=Path,default=Path("results/paper_t_v4"));out=ap.parse_args().outdir;out.mkdir(parents=True,exist_ok=True)
 old,new=run("legacy"),run("seasonal");g0,g1=diagnose(old),diagnose(new)
 assert len(new)==300 and len(g1)==75
 assert all(x["peak_spread_mw"]<1e-6 for x in g0)
 assert sum(x["peak_spread_mw"]>1e-6 for x in g1)==29
 assert sum(x["delta_spread_mw"]>1e-6 for x in g1)==37
 for rows,path in [(old,"legacy_300cases.csv"),(new,"v4_seasonal_300cases.csv"),(g1,"v4_scale_diagnostics_75groups.csv")]:write_csv(out/path,rows)
 summary={"classification":"HYPOTHETICAL SYNTHETIC ONLY","n_cases":len(new),"n_groups":len(g1),
 "absolute_peak_scale_sensitive_groups":29,"shift_effect_scale_sensitive_groups":37,
 "no_EFS_ReEDS_physical_hour_join":True}
 (out/"summary.json").write_text(json.dumps(summary,indent=2)+"\n");print(json.dumps(summary,indent=2))
if __name__=="__main__":main()
