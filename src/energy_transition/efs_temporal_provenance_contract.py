"""Explicit temporal provenance contract for any synchronized Western EFS load.

No UTC reconstruction is performed without independently verified source
clock metadata. This code rejects unsupported time assumptions by default.
"""
import argparse,json
from pathlib import Path
from datetime import datetime,timezone

REQUIRED={
 "source_dataset_doi","source_file","source_clock","calendar_year",
 "leap_day_rule","daylight_saving_rule","clock_reference_evidence_url",
 "clock_reference_evidence_quote","time_alignment_review_status"
}
SUPPORTED_CLOCKS={"UTC","UTC_FIXED_OFFSET"}
SUPPORTED_DST={"not_applied"}
SUPPORTED_LEAP={"8760_representative_nonleap"}

def verify(metadata):
 missing=sorted(REQUIRED-set(metadata))
 if missing:raise ValueError("Missing authoritative temporal fields: "+", ".join(missing))
 if metadata["time_alignment_review_status"]!="verified":
  raise ValueError("Timezone source evidence is NOT independently verified")
 if metadata["source_clock"] not in SUPPORTED_CLOCKS:
  raise ValueError("Unrecognized source-clock convention; no silent assumptions")
 if metadata["daylight_saving_rule"] not in SUPPORTED_DST:
  raise ValueError("DST interpretation needs a separate reviewed implementation")
 if metadata["leap_day_rule"] not in SUPPORTED_LEAP:
  raise ValueError("Leap-day treatment not independently established")
 if metadata["source_clock"]=="UTC_FIXED_OFFSET":
  if "utc_offset_hours" not in metadata or not isinstance(metadata["utc_offset_hours"],int):
   raise ValueError("Explicit integer UTC offset required")
  if not -12<=metadata["utc_offset_hours"]<=14:
   raise ValueError("UTC offset outside admissible bound")
 if not str(metadata["clock_reference_evidence_url"]).startswith("https://"):
  raise ValueError("Clock reference evidence URL required")
 if len(str(metadata["clock_reference_evidence_quote"]).strip())<20:
  raise ValueError("Authoritative evidence text is insufficient")
 return {"provenance_review":"verified_metadata_supplied",
  "source_clock":metadata["source_clock"],
  "algorithm_utc_conversion_performed":False,
  "ready_for_time_mapping_implementation":True}

def main():
 p=argparse.ArgumentParser()
 p.add_argument("--metadata",type=Path,required=True)
 p.add_argument("--out",type=Path,required=True)
 a=p.parse_args()
 r=verify(json.loads(a.metadata.read_text()))
 a.out.write_text(json.dumps(r,indent=2)+"\n");print(json.dumps(r,indent=2))
if __name__=="__main__":main()
