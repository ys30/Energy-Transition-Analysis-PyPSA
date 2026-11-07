"""External NASA POWER hourly UTC vs LST source-clock case study.

Source: https://power.larc.nasa.gov/docs/services/api/temporal/hourly/
The publisher says LST is derived from UTC on longitude-based 15-degree swaths;
the hourly API defaults to LST. Both responses describe *one POWER product*,
so these are not independent meteorological observations.

Reproducibility gate: real API JSON files, independently retrieved, strict
missing-value and timestamp coverage checks, exact publisher offset for a
longitude centered on a 15-degree band, and hash preservation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

BASE="https://power.larc.nasa.gov/api/temporal/hourly/point"
START="20240115"
END="20240118"
LAT=35.0
LON=-105.0
VARIABLE="T2M"
SENTINEL=-999.0

def request_url(standard: str) -> str:
    if standard not in ("UTC","LST"):
        raise ValueError("NASA time-standard must be explicitly UTC or LST")
    params={
       "parameters":VARIABLE,"community":"RE","latitude":LAT,"longitude":LON,
       "start":START,"end":END,"format":"JSON","time-standard":standard}
    return BASE+"?"+urlencode(params)

def fetch_json(standard,timeout=60):
    request=Request(request_url(standard),headers={"User-Agent":"ProjectB-PaperT-provenance-audit/1.0"})
    with urlopen(request,timeout=timeout) as response:
        raw=response.read()
    if len(raw)>5_000_000:raise ValueError("Unexpectedly large NASA POWER response")
    payload=json.loads(raw)
    if not isinstance(payload,dict):raise ValueError("Unexpected NASA source response")
    return payload,raw

def parse_hourly(payload):
    source=payload.get("properties",{}).get("parameter",{}).get(VARIABLE)
    if not isinstance(source,dict):raise ValueError("No real NASA POWER T2M hourly data")
    parsed={}
    for key,value in source.items():
        if len(key)!=10 or not key.isdigit():raise ValueError("Unexpected NASA hour index")
        timestamp=datetime.strptime(key,"%Y%m%d%H")
        if timestamp in parsed:raise ValueError("Duplicate NASA hour label")
        if not isinstance(value,(float,int)) or not math.isfinite(value) or value<=SENTINEL:
            raise ValueError("Missing or invalid real NASA weather value")
        parsed[timestamp]=float(value)
    if len(parsed)!=96:raise ValueError("NASA 4-day source has missing or extra hours")
    first=datetime.strptime(START,"%Y%m%d")
    if set(parsed)!={first+timedelta(hours=h) for h in range(96)}:
        raise ValueError("NASA hourly chronology incomplete or nonsequential")
    return parsed

def audit(utc,lst):
    u=parse_hourly(utc);l=parse_hourly(lst)
    # Choose longitude exactly on NASA's 15-degree band center so the
    # published integer swath shift has no half-band rounding ambiguity.
    if LON%15!=0:raise ValueError("This validation point must be on a swath center")
    offset=int(LON/15) # LST = UTC + offset (civil and DST are not involved).
    joined=[(ts,x,l[ts+timedelta(hours=offset)]) for ts,x in u.items()
            if ts+timedelta(hours=offset) in l]
    naive=[abs(u[ts]-l[ts]) for ts in u]
    # Strict apples-to-apples comparison on precisely the same UTC anchors
    # as the 89 pairs surviving the physical UTC→LST mapping.
    paired_naive=[abs(u[ts]-l[ts]) for ts,_,_ in joined]
    physically=[abs(x-y) for ts,x,y in joined]
    if len(joined)!=96-abs(offset):raise ValueError("Unexpected NASA nonwrapping overlap")
    max_aligned=max(physically)
    # Strict checks use real API values, never manufactured alignment.
    if max_aligned>1e-6:
        raise ValueError(f"NASA UTC/LST publisher conversion failed against source data: max={max_aligned}")
    naive_mae=sum(naive)/len(naive)
    paired_naive_mae=sum(paired_naive)/len(paired_naive)
    true_mae=sum(physically)/len(physically)
    if naive_mae<=1e-5:
        raise ValueError("Selected NASA source sample has no measurable naive clock mismatch")
    return {
      "status":"NASA_POWER_REAL_UTC_LST_SOURCE_CLOCK_TEST_PASS",
      "source":"NASA POWER Hourly API",
      "official_documentation":"https://power.larc.nasa.gov/docs/services/api/temporal/hourly/",
      "source_family_independent_of_EFS_ReEDS":True,
      "UTC_and_LST_independent_physical_observations":False,
      "publisher_declared_transform":"UTC→LST longitude 15-degree swath",
      "source_year":2024,"requested_date_start":START,"requested_date_end":END,
      "latitude":LAT,"longitude":LON,"variable":VARIABLE,
      "utc_hours":len(u),"lst_hours":len(l),
      "publisher_expected_LST_minus_UTC_hours":offset,
      "nonwrapping_matched_hours":len(joined),
      "naive_equal_hour_label_mae_celsius":naive_mae,
      "naive_equal_label_on_same_89_utc_anchors_mae_celsius":paired_naive_mae,
      "matched_utc_anchors_for_both_comparison_arms":len(joined),
      "publisher_time_normalized_hour_mae_celsius":true_mae,
      "max_publisher_time_normalized_difference_celsius":max_aligned,
      "original_EFS2020_physical_clock_certified":False,
      "comparison_is_real_API_data":True,
      "this_test_does_not_authorize_EFS_hourly_weather_join":True,
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",required=True,type=Path)
    p.add_argument("--utc-file",type=Path)
    p.add_argument("--lst-file",type=Path)
    a=p.parse_args()
    if bool(a.utc_file)!=bool(a.lst_file):
        raise ValueError("Both source files must be supplied together")
    if a.utc_file:
        u_raw=a.utc_file.read_bytes();l_raw=a.lst_file.read_bytes()
        u=json.loads(u_raw);l=json.loads(l_raw)
    else:
        u,u_raw=fetch_json("UTC");l,l_raw=fetch_json("LST")
    report=audit(u,l)
    report["source_UTC_response_sha256"]=hashlib.sha256(u_raw).hexdigest()
    report["source_LST_response_sha256"]=hashlib.sha256(l_raw).hexdigest()
    a.out.mkdir(parents=True,exist_ok=True)
    (a.out/"nasa_power_hourly_UTC_original.json").write_bytes(u_raw)
    (a.out/"nasa_power_hourly_LST_original.json").write_bytes(l_raw)
    (a.out/"nasa_power_UTC_LST_source_clock_result.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))
if __name__=="__main__":main()
