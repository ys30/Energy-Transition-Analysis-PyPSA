"""Fail-closed end-to-end 11-state candidate/hour indexing tests."""
import numpy as np
import pandas as pd
import pytest

from energy_transition.efs_eleven_state_candidate_clock import (
    analyze_combined_source, STATE_NAMES, EXISTING, CANDIDATE, YEARS,
)

def fixture():
    hours=np.arange(1,8761,dtype=np.int64)
    src_parts=[]
    pilot_parts=[]
    for year in YEARS:
        for state in STATE_NAMES:
            load=np.ones(len(hours))*100.0
            # Distinct local-hour source shapes create nontrivial +7/+8
            # cross-offset coincident peak sensitivity.
            load[99]=(1000 if state in CANDIDATE else 900)
            frame=pd.DataFrame({"year":year,"state":state,
                                "local_hour_id":hours,"load_mw":load})
            src_parts.append(frame)
            if state in EXISTING:
                part=frame.rename(columns={"load_mw":"allocated_mw"}).copy()
                part["state"]=STATE_NAMES[state]
                part["reeds_zone"]="p"+str(sorted(STATE_NAMES).index(state)+1)
                pilot_parts.append(part)
    source=pd.concat(src_parts,ignore_index=True)
    seven=pd.concat(pilot_parts,ignore_index=True)
    weights=[{"source_state":s,"reeds_zone":"p"+str(i+35),"weight":1.0}
             for i,s in enumerate(sorted(CANDIDATE))]
    report={"candidate_only":True,"EFS_demand_admitted":False,
            "source_geography_independently_validated":False,
            "offshore_auxiliaries_excluded_count":157,
            "offshore_auxiliaries_LAF_modified":False,
            "source_state_weight_totals":{s:1.0 for s in CANDIDATE},
            "source_to_reeds_zone_candidate_weights":weights}
    return source,seven,report


def test_11_state_candidate_preserves_yearly_mwh_and_reports_mixed_peak():
    source,seven,weights=fixture()
    r=analyze_combined_source(source,seven,weights)
    assert r["source_state_hour_count"]==11*3*8760
    assert r["combined_zonal_state_hour_rows"]==11*3*8760
    assert r["candidate_state_source_to_zone_conservation_verified"]
    assert not r["empirically_admitted_11_state_load"]
    assert not r["source_EFS_localhour_to_actual_UTC_verified"]
    for y in r["planning_year_results"]:
        assert y["annual_allocated_mwh"]==pytest.approx(y["annual_allocated_compat_mwh"])
        assert y["mixed_offset_peak_delta_mw"] < 0


def test_candidate_source_zone_weights_must_sum_to_one():
    src,seven,report=fixture()
    report["source_to_reeds_zone_candidate_weights"][0]["weight"]=0.9
    with pytest.raises(ValueError,match="do not conserve"):
        analyze_combined_source(src,seven,report)


def test_prior_seven_state_archive_must_be_unchanged():
    src,seven,report=fixture()
    seven.loc[seven.index[0],"allocated_mw"]*=0.8
    with pytest.raises(ValueError,match="Seven-state archived ratio changed"):
        analyze_combined_source(src,seven,report)


def test_missing_source_hour_is_rejected():
    src,seven,report=fixture()
    src=src.drop(index=src.index[0])
    with pytest.raises(ValueError,match="Missing/noncontiguous local-hour"):
        analyze_combined_source(src,seven,report)


def test_zero_source_weight_zone_is_preserved_as_metadata_not_synthetic_hourly_load():
    src,seven,report=fixture()
    report["source_to_reeds_zone_candidate_weights"].append(
        {"source_state":"CA","reeds_zone":"p0","weight":0.0})
    r=analyze_combined_source(src,seven,report)
    assert r["candidate_zero_weight_zones_recorded_but_not_allocated"]==1
    assert r["combined_zonal_state_hour_rows"]==11*3*8760
    assert not r["empirically_admitted_11_state_load"]
