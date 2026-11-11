"""Paper T WP2: source-clock-audited observed load + real irradiance proxy.
Ruggles 2020-Oct AZPS UTC hour-ending load; NASA POWER Phoenix UTC hour-beginning GHI.
No EFS/ReEDS physical-hour join. Not actual PV generation or validated statewide PV.
"""
from __future__ import annotations
import argparse,csv,datetime as dt,hashlib,io,json,math,statistics,urllib.parse,urllib.request
from pathlib import Path

UPSTREAM_SHA="b80145df5f92aba56c52ed45281831b93543fb3b"
LOAD_URL=(f"https://raw.githubusercontent.com/truggles/EIA_Cleaned_Hourly_Electricity_Demand_Data/"
          f"{UPSTREAM_SHA}/data/release_2020_Oct/balancing_authorities/AZPS.csv")
POWER_ARGS={"parameters":"ALLSKY_SFC_SW_DWN","community":"RE","latitude":"33.4484",
            "longitude":"-112.0740","start":"20180101","end":"20181231",
            "format":"JSON","time-standard":"UTC"}
POWER_URL="https://power.larc.nasa.gov/api/temporal/hourly/point?"+urllib.parse.urlencode(POWER_ARGS)
START=dt.datetime(2018,1,1,tzinfo=dt.timezone.utc)
END=dt.datetime(2019,1,1,tzinfo=dt.timezone.utc)
LAGS=(-3,-2,0,2,3)
SCALES_MW=(500,1000,2000)
def get(url):
 request=urllib.request.Request(url,headers={"User-Agent":"PaperT-WP2-reproducibility/1.0"})
 with urllib.request.urlopen(request,timeout=180) as response:data=response.read()
 return data,hashlib.sha256(data).hexdigest()
def parse_load(data):
 rows=list(csv.DictReader(io.StringIO(data.decode("utf-8-sig"))))
 out={}
 for r in rows:
  stamp=dt.datetime.strptime(r["date_time"],"%Y-%m-%d %H:%M:%S").replace(tzinfo=dt.timezone.utc)
  if not START<=stamp<END:continue
  if stamp in out:raise ValueError("Non-unique load end-UTC")
  out[stamp]=(float(r["cleaned demand (MW)"]),r["category"])
 if len(out)!=8760:raise ValueError(f"Expected 8760 AZPS 2018 UTC timestamps, got {len(out)}")
 return out
def parse_power(data):
 response=json.loads(data)
 hourly=response["properties"]["parameter"]["ALLSKY_SFC_SW_DWN"]
 out={}
 for stamp,val in hourly.items():
  begin=dt.datetime.strptime(stamp,"%Y%m%d%H").replace(tzinfo=dt.timezone.utc)
  if START<=begin<END:
   if begin in out:raise ValueError("Non-unique POWER begin-UTC")
   out[begin]=float(val)
 if len(out)!=8760:raise ValueError(f"Expected 8760 NASA POWER 2018 UTC timestamps, got {len(out)}")
 return out
def prepare(load,ghi):
 # EIA hour-ending t and POWER hour-beginning t-1 describe same half-open [t-1,t) hour.
 hours=[START+dt.timedelta(hours=i) for i in range(8760)]
 row=[]
 for start in hours:
  ending=start+dt.timedelta(hours=1)
  if ending not in load or start not in ghi:continue
  l,category=load[ending];g=ghi[start]
  if not(math.isfinite(g) and g>=0 and math.isfinite(l) and l>0):continue
  if g>1400:raise ValueError("Implausible GHI >1400 W/m2")
  row.append({"start_utc":start.isoformat(),"end_utc":ending.isoformat(),
    "load_mw":l,"irradiance_w_m2":g,"quality_category":category})
 if len(row)<.98*8760:raise ValueError(f"Insufficient matched resource hours {len(row)}")
 return row
def evaluate(rows,capacity,lag):
 # use common interior for all five lag scenarios to avoid boundary confounding.
 # Demand shifted by lag indices relative to fixed irradiance; no wrap.
 demand=[];solar=[];timestamps=[]
 for i in range(3,8760-3):
  shifted_index=i-lag
  # source rows must be gapless on whole 2018 calendar
  a=rows[shifted_index];b=rows[i]
  if a["load_mw"]<=0 or b["irradiance_w_m2"]<0:continue
  demand.append(a["load_mw"])
  solar.append(capacity*min(b["irradiance_w_m2"]/1000,1))
  timestamps.append(b["end_utc"])
 if not demand:raise ValueError("No comparable hours")
 net=[x-y for x,y in zip(demand,solar)]
 peak=max(net);idx=net.index(peak)
 return {"capacity_proxy_mw":capacity,"lag_h":lag,"compared_hours":len(demand),
   "net_peak_mw":peak,"net_peak_end_utc":timestamps[idx],
   "overlap_fraction":sum(min(x,y) for x,y in zip(demand,solar))/sum(solar),
   "potential_surplus_mwh":sum(max(0,y-x) for x,y in zip(demand,solar)),
   "demand_mwh":sum(demand),"solar_proxy_mwh":sum(solar)}
def main():
 parser=argparse.ArgumentParser();parser.add_argument("--outdir",type=Path,required=True)
 out=parser.parse_args().outdir;out.mkdir(parents=True,exist_ok=True)
 lb,lhash=get(LOAD_URL);pb,phash=get(POWER_URL)
 loads=parse_load(lb);power=parse_power(pb)
 # All timestamps, not only valid values, must have a complete hour-by-hour calendar.
 assert len(loads)==len(power)==8760
 rows=prepare(loads,power)
 if len(rows)!=8760:raise ValueError("No interpolation or missing hours allowed for shift comparisons")
 results=[evaluate(rows,c,lag) for c in SCALES_MW for lag in LAGS]
 for c in SCALES_MW:
  group=[r for r in results if r["capacity_proxy_mw"]==c]
  ref=next(r for r in group if r["lag_h"]==0)
  for r in group:
   r["peak_delta_mw"]=r["net_peak_mw"]-ref["net_peak_mw"]
   r["peak_delta_pct"]=100*(r["net_peak_mw"]/ref["net_peak_mw"]-1)
   r["overlap_delta_pp"]=100*(r["overlap_fraction"]-ref["overlap_fraction"])
   assert abs(r["solar_proxy_mwh"]-ref["solar_proxy_mwh"])<1e-5
   assert abs(r["demand_mwh"]-ref["demand_mwh"])<1e-5
 with (out/"azps_power_2018_15_scenarios.csv").open("w",newline="") as f:
  w=csv.DictWriter(f,fieldnames=list(results[0]));w.writeheader();w.writerows(results)
 (out/"source_evidence.json").write_text(json.dumps({
  "data_kind":"Observed EIA-derived demand + satellite/reanalysis GHI; assumed PV conversion proxy",
  "scope":"AZPS BA demand and single Phoenix coordinate solar proxy; NOT geographical PV fleet",
  "time_alignment":"EIA UTC hour-ending at t; POWER UTC hour-beginning at t-1; matched interval [t-1,t)",
  "reeds_efs_hour_claim":"No EFS or ReEDS original hourly physical join used or authorized",
  "source_urls":[LOAD_URL,POWER_URL],"sha256":[lhash,phash],
  "n_load_2018":len(loads),"n_ghi_2018":len(power),"matched_intervals":len(rows),
  "capacity_proxy_mw":SCALES_MW,"lags":LAGS,
  "common_nonwrap_support":"2018 UTC calendar indices 3..8756; 8754 hours for each scenario",
  "independent_review_required":True},indent=2)+"\n")
 print(json.dumps(results,indent=2))
if __name__=="__main__":main()
