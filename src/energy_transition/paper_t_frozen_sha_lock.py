"""Validate frozen original Paper T source supplement checksum lock.

This lock is committed to the source repository and *independent* of the
downloaded artifact manifest. A newly generated/changed source evidence file
must not silently replace an accepted figure/table.
"""
from __future__ import annotations
import argparse,hashlib,re
from pathlib import Path

REQUIRED={
"tables/T_S1_nonwrapping_33_state_year_lags.csv",
"tables/T_S2_idaho_original_subsector_annual_energy.csv",
"tables/T_S3_idaho_frozen_transport_crossyear.csv",
"tables/T_S4_idaho_reference_month_hour_marginals.csv",
"tables/T_S5_idaho_source_residual_overview.csv",
"provenance/nonwrapping_lag_source.json",
"provenance/idaho_subsector_original_source.json",
"provenance/idaho_marginal_original_source.json",
} | {f"figures/figure_T{i}_{name}.{ext}" for i,name in [
(1,"source_admission"),(2,"source_lag_2030"),
(3,"idaho_month_hour_marginals"),(4,"frozen_shift_holdout")]
for ext in ("svg","png")}

def audit(lock:Path,bundle:Path):
    entries={}
    for line in lock.read_text().splitlines():
        if not line.strip() or line.startswith("#"):continue
        match=re.fullmatch(r"([0-9a-f]{64})  ([A-Za-z0-9_./-]+)",line)
        if not match:raise ValueError("Invalid frozen checksum row")
        checksum,path=match.groups()
        if path in entries:raise ValueError("Repeated frozen checksum path")
        entries[path]=checksum
    if set(entries)!=REQUIRED:raise ValueError("Frozen source checksum scope is not exactly 16 approved files")
    for path,expected in entries.items():
        actual=bundle/path
        if not actual.is_file():raise ValueError("Missing accepted source file: "+path)
        digest=hashlib.sha256(actual.read_bytes()).hexdigest()
        if digest!=expected:raise ValueError("CHANGED accepted source evidence: "+path)
    return {"source_evidence_files_checked":len(entries),"hash_lock_matches_archived_source":True,
            "original_EFS2020_physical_UTC_certified":False,"permanent_DOI_registered":False}

def main():
    p=argparse.ArgumentParser();p.add_argument("--lock",required=True,type=Path)
    p.add_argument("--bundle",required=True,type=Path)
    a=p.parse_args()
    print(audit(a.lock,a.bundle))
if __name__=="__main__":main()
