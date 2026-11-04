"""Read-only second EFS representative-bus counterfactual.

Compare original first-bus load placement, single max-original-Pd
*connected* bus, and multibus Pd-weighted placement from a previously CI
verified zone table. This is a provenance-bounded spatial experiment only.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
import pandas as pd
import numpy as np

def compare(source):
    need={"Load_id","original_bus_id","candidate_buses_source_ids",
          "candidate_bus_pd_shares","original_zone_annual_mwh",
          "share_of_zone_load_relocated_from_original_bus",
          "fallback_original_bus_no_positive_pd_candidate"}
    if need-set(source):raise ValueError("Archived firstbus candidate schema incomplete")
    d=source.copy()
    if len(d)!=20 or d.Load_id.duplicated().any():raise ValueError("Source zone cohort mismatch")
    records=[]
    for r in d.itertuples(index=False):
        ids=str(r.candidate_buses_source_ids).split(";")
        try: weights=[float(x) for x in str(r.candidate_bus_pd_shares).split(";")]
        except ValueError as exc:raise ValueError("Invalid source Pd weight string") from exc
        if len(ids)!=len(weights) or len(ids)!=len(set(ids)) or any(not z for z in ids):
            raise ValueError("Malformed candidate bus IDs")
        if not np.isfinite(weights).all() or min(weights)<0 or abs(sum(weights)-1)>1e-8:
            raise ValueError("Nonconservative candidate source weights")
        energy=float(r.original_zone_annual_mwh)
        if not np.isfinite(energy) or energy<0:raise ValueError("Invalid original EFS zonal energy")
        fallback=str(r.fallback_original_bus_no_positive_pd_candidate).lower()=="true"
        if fallback and (len(ids)!=1 or ids[0]!=str(r.original_bus_id) or weights[0]!=1):
            raise ValueError("Fallback source state changed")
        max_idx=int(np.argmax(weights))
        top=ids[max_idx]
        single_reassigned=(top!=str(r.original_bus_id))
        pd_weighted_share=1-float(weights[ids.index(str(r.original_bus_id))]) if str(r.original_bus_id) in ids else 1.
        old=float(r.share_of_zone_load_relocated_from_original_bus)
        if abs(pd_weighted_share-old)>1e-7:raise ValueError("Archived multibus source weights inconsistent")
        records.append({
          "Load_id":str(r.Load_id),
          "original_first_bus_id":str(r.original_bus_id),
          "single_largest_positive_pd_connected_bus_id":top,
          "candidate_eligible_bus_count":len(ids),
          "original_zone_annual_mwh":energy,
          "single_bus_source_candidate_changed":single_reassigned,
          "multibus_share_changed":pd_weighted_share,
          "single_largest_pd_annual_mwh_relocated":energy if single_reassigned else 0.,
          "multiple_pd_weighted_annual_mwh_relocated":energy*pd_weighted_share,
          "fallback_original_bus_no_positive_pd_candidate":fallback,
          "single_largest_pd_source_bus_is_utility_certified":False,
        })
    out=pd.DataFrame(records)
    old_total=float(out.original_zone_annual_mwh.sum())
    singles=float(out.single_largest_pd_annual_mwh_relocated.sum())
    multiples=float(out.multiple_pd_weighted_annual_mwh_relocated.sum())
    return out,{
       "original_zone_count":len(out),
       "candidate_fallback_zones":int(out.fallback_original_bus_no_positive_pd_candidate.sum()),
       "zones_differing_under_single_max_pd":int(out.single_bus_source_candidate_changed.sum()),
       "zones_differing_under_pd_weighted_multibus":int(out.multibus_share_changed.gt(1e-10).sum()),
       "original_2030_archived_annual_mwh":old_total,
       "single_max_pd_annual_mwh_on_different_bus":singles,
       "multi_pd_weighted_annual_mwh_on_different_bus":multiples,
       "single_max_pd_reallocated_share":singles/old_total,
       "multi_pd_weighted_reallocated_share":multiples/old_total,
       "original_20_zonal_hourly_load_profiles_altered":False,
       "original_archive_modified":False,
       "utility_load_delivery_points_certified":False,
       "real_generator_poi_attached":False,
       "full_western_opf_solved":False,
       "note":"Bus ID relocation fractions describe counterfactual model placement, not actual physical relocation, overload or unserved electricity."
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--firstbus-candidates",required=True,type=Path)
    p.add_argument("--outdir",required=True,type=Path)
    a=p.parse_args()
    rows,report=compare(pd.read_csv(a.firstbus_candidates,dtype={"original_bus_id":"string"}))
    a.outdir.mkdir(parents=True,exist_ok=True)
    rows.to_csv(a.outdir/"efs_2030_three_bus_placement_rules.csv",index=False)
    (a.outdir/"efs_2030_three_bus_placement_rules.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))
if __name__=="__main__":main()
