"""Actual-publisher ReEDS wind/PV BA source intake and audit.

Only source HDF5 exact MD5 and calendar checks authorize 'authentic resource
downloaded'. An instantaneous CF is never declared hour-energy equivalent
to an hour-ending demand without a separate interval contract.
"""
from __future__ import annotations
import argparse,hashlib,json,re
from pathlib import Path
import numpy as np
import pandas as pd

SOURCES={
 "wind":{"record":"https://zenodo.org/records/18422200",
 "h5":"cf_wind-ons_reference_ba.h5","md5":"8fd010e1d38f9a8591ba58c9eff1a368",
 "capacity":"sc_wind-ons_reference_ba.csv","capacity_md5":"f5b5665c7133978bb09c3bb12c77dfba"},
 "pv":{"record":"https://zenodo.org/records/18407660",
 "h5":"cf_upv_reference_ba.h5","md5":"398165a0a7ec5c21d3e891a28162a217",
 "capacity":"sc_upv_reference_ba.csv","capacity_md5":"d2545544d96ffb1a4645750830856606"},
}
CROSSWALK_MD5="f269adef29b6d96317a845f6129b5ad9"
CROSSWALK_NAME="county2zone.csv"
HOURS=8760

def file_md5(path):
 h=hashlib.md5()
 with Path(path).open("rb") as f:
  for b in iter(lambda:f.read(1<<20),b""):h.update(b)
 return h.hexdigest()

def require_md5(path,expected):
 value=file_md5(path)
 if value!=expected:raise ValueError(f"Publisher MD5 mismatch for {path}: {value}")
 return value

def decode(values):
 return [v.decode("utf8") if isinstance(v,bytes) else str(v) for v in values]

def inspect_weather_index(raw):
 labels=decode(raw)
 index=pd.to_datetime(labels,errors="raise")
 if len(index)!=len(set(labels)) or index.isna().any():
  raise ValueError("Missing or duplicate raw 15-weather-year CF index")
 years=np.asarray(index.year)
 choices=np.flatnonzero(years==2012)
 if len(choices)!=HOURS or not np.array_equal(choices,np.arange(choices[0],choices[0]+HOURS)):
  raise ValueError("Expected contiguous authentic 2012 weather-year 8760 hours")
 target=pd.date_range("2012-01-01",periods=HOURS,freq="h")
 native=pd.DatetimeIndex(index[choices])
 if native.tz is None:
  if not native.equals(target):raise ValueError("CST naive 2012 CF calendar mismatch")
  time_note="Publisher-defined fixed CST (UTC-06:00), native labels are timezone-naive"
 else:
  target=target.tz_localize("Etc/GMT+6")
  if not native.equals(target):raise ValueError("CST aware 2012 CF calendar mismatch")
  time_note="Publisher-defined fixed CST (UTC-06:00), native labels offset-aware"
 return choices,{"index_rows_total":len(labels),"index_first":labels[0],
  "index_last":labels[-1],"2012_first":labels[choices[0]],
  "2012_last":labels[choices[-1]],"2012_rows":len(choices),
  "2012_Feb29_included":True,"2012_Dec31_excluded":True,
  "hour_tag_semantics":"instantaneous at exact hour per publisher",
  "publisher_time_standard":"fixed CST UTC-06:00",
  "native_label_interpretation":time_note,
  "demand_hour_ending_join_certified":False}

def inspect(path,tech,capacity_csv,crosswalk_csv):
 import h5py
 spec=SOURCES[tech]
 hashes={"profile":require_md5(path,spec["md5"]),
         "capacity":require_md5(capacity_csv,spec["capacity_md5"]),
         "county2zone":require_md5(crosswalk_csv,CROSSWALK_MD5)}
 with h5py.File(path,"r") as hf:
  keys=list(hf.keys())
  if not {"data","columns","index_0"}.issubset(keys):
   raise ValueError("ReEDS H5 missing publisher-documented data,columns,index_0")
  data=hf["data"];names=decode(hf["columns"][:])
  times,clock=inspect_weather_index(hf["index_0"][:])
  if len(data.shape)!=2 or data.shape[0]!=clock["index_rows_total"] or data.shape[1]!=len(names):
   raise ValueError("HDF5 shape/column indexes are inconsistent")
  if len(names)!=len(set(names)):raise ValueError("Duplicate source technology/resource-class BA columns")
  # Publisher uses encoded integer CF values in some releases: do not assume
  # numeric data are direct [0,1] until inspected.
  offsets=(0,24,168,4380,8759)
  row_idx=[int(times[k]) for k in offsets]
  samples=np.vstack([np.asarray(data[i],dtype=float) for i in row_idx])
  if not np.isfinite(samples).all():raise ValueError("Nonfinite publisher resource sample")
  cap=pd.read_csv(capacity_csv);zone=pd.read_csv(crosswalk_csv)
  report={"status":"OFFICIAL_2012_REEDS_CF_SOURCE_INTAKE_AUTHENTICATED",
   "technology":tech,"source_record":spec["record"],"profile_filename":spec["h5"],
   "verified_original_md5s":hashes,"h5_keys":keys,
   "dataset_shape":list(data.shape),"dataset_dtype":str(data.dtype),
   "source_column_count":len(names),"source_columns_first_12":names[:12],
   "source_column_regexp_class_region_matches":sum(bool(re.fullmatch(r"[^|]+\|p\d+",x)) for x in names),
   "native_CF_sample_min":float(samples.min()),"native_CF_sample_max":float(samples.max()),
   "native_CF_sample_quantiles":np.quantile(samples,[0,.25,.5,.75,.99,1]).astype(float).tolist(),
   "capacity_csv_columns":list(cap.columns),"capacity_csv_first_3":cap.head(3).astype(str).to_dict("records"),
   "county2zone_csv_columns":list(zone.columns),"county2zone_csv_first_3":zone.head(3).astype(str).to_dict("records"),
   "native_weather_clock":clock,
   "2012_capacity_factor_rescaled_and_aggregated":False,
   "official_demand_and_weather_hour_interval_equivalence_verified":False,
   "source_BA_to_state_allocation_verified":False,
   "weather_adjusted_LP_completed":False}
 return report

def main():
 p=argparse.ArgumentParser()
 p.add_argument("--wind-h5",type=Path,required=True)
 p.add_argument("--pv-h5",type=Path,required=True)
 p.add_argument("--wind-capacity",type=Path,required=True)
 p.add_argument("--pv-capacity",type=Path,required=True)
 p.add_argument("--county2zone",type=Path,required=True)
 p.add_argument("--out",type=Path,required=True)
 a=p.parse_args()
 a.out.mkdir(parents=True,exist_ok=True)
 for tech,path,sc in (("wind",a.wind_h5,a.wind_capacity),("pv",a.pv_h5,a.pv_capacity)):
  report=inspect(path,tech,sc,a.county2zone)
  (a.out/f"reeds2022_{tech}_actual_original_source_intake.json").write_text(json.dumps(report,indent=2)+"\n")
  print(tech,"original source verified",report["source_column_count"],
    "columns; 2012:",report["native_weather_clock"]["2012_first"],
    "to",report["native_weather_clock"]["2012_last"],
    "raw CF observed maximum",report["native_CF_sample_max"])
 print("ORIGINAL_WIND_AND_PV_SOURCE_BYTES_AND_CALENDAR_VERIFIED_NO_UNAUTHORIZED_HOUR_JOIN")
if __name__=="__main__":main()
