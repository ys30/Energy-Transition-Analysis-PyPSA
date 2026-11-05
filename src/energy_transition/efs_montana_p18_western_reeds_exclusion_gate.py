"""Audit whether Montana raw ReEDS p35/p19 to final p18 is source-rule consistent.

Pinned build_shapes.py excludes p35 and p19 from Western raw reeds shapes.
We parse exact upstream Python AST and evaluate *observed raw county matches*
from independently validated NetCDF/GIS CI. This is NOT a reproduction of
interconnect clipping, nearest-neighbor fills or pre-county mode inputs.
"""
from __future__ import annotations
import argparse,ast,json
from pathlib import Path

PIN="338af9912addbaf038c6098fe27e1e6ef099d8aa"

def check(script:str,raw_county:dict):
    tree=ast.parse(script)
    candidates=[]
    for node in ast.walk(tree):
        if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=="reeds_exclusion" for t in node.targets):
            candidates.append(ast.literal_eval(node.value))
    if len(candidates)!=1 or "western" not in candidates[0]:
        raise ValueError("Pinned Western shape exclusion source code unavailable")
    west=candidates[0]["western"]
    if not isinstance(west,list) or not {"p35","p19"}.issubset(set(west)) or "p18" in west:
        raise ValueError("Expected pinned Western p35/p19 exclusion not verified")
    if 'shape_state_intersection.name.str.contains(' not in script or 'exclusion_dict[interconnect]' not in script:
        raise ValueError("Pinned shape filter source implementation changed")
    records=raw_county.get("reviewed_source_load_cases",[])
    mt=[r for r in records if r.get("original_firstbus_id")=="2077004"]
    if len(mt)!=1:raise ValueError("Missing Montana p18 independent source county")
    mt=mt[0]
    counts=mt["source_county_raw_polygon_single_cover_counts"]
    if counts!={"p35":8,"p19":1,"p18":1} or mt["source_county_final_reeds_zone_counts"]!={"p18":10}:
        raise ValueError("Pinned observed source county mass drift")
    allowed={zone:n for zone,n in counts.items() if zone not in west}
    return {
      "pinned_PyPSA_USA_commit":PIN,
      "observed_raw_Montana_p30071_source_county_bus_count":int(mt["source_county_bus_count"]),
      "raw_original_polygon_single_cover_count_by_zone":counts,
      "pinned_western_excluded_source_zone_names":west,
      "raw_county_bins_remaining_after_explicit_western_exclusion":allowed,
      "raw_county_only_surviving_zone_is_p18":allowed=={"p18":1},
      "archived_postprocessed_county_zone_counts":mt["source_county_final_reeds_zone_counts"],
      "pinned_county_majority_rule_is_consistent_with_observed_final_zone":allowed=={"p18":1},
      "posttrim_geometry_and_nearest_fill_reproduced":False,
      "actual_precountry_majority_zone_inputs_reconstructed":False,
      "utility_load_serving_polygon_certified":False,
      "physical_2030_2050_OPF_validated":False,
      "note":"Original excluded raw zone labels are source-verifiable and consistent with final p18 after processing; the exact posttrim/nearest-filled inputs to county mode have not been recovered.",
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--pinned-build-shapes",type=Path,required=True)
    p.add_argument("--source-county-report",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    r=check(a.pinned_build_shapes.read_text(),json.loads(a.source_county_report.read_text()))
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(r,indent=2)+"\n")
    print(json.dumps(r,indent=2))
if __name__=="__main__":main()
