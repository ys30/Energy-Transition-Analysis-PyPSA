import pandas as pd
import pytest
from energy_transition.efs_2030_load_bus_distance_thresholds import summarize

TOTAL=274706987.114121

def source():
    d=[]
    for i in range(20):
        annual=TOTAL/19 if i else 0.
        d.append({"Load_id":f"EFS_2030_p{i}_New Mexico",
                  "original_bus_id":f"a{i}",
                  "single_max_pd_candidate_bus_id":f"a{i}" if i==0 else f"b{i}",
                  "single_bus_straight_line_coordinate_distance_km":0. if i==0 else i*25.,
                  "original_annual_mwh":annual,
                  "candidate_id_changed":i!=0})
    return pd.DataFrame(d)

def test_source_thresholds_preserve_cohort_and_weights():
    ranked,r=summarize(source())
    assert r["original_source_load_zone_count"]==20
    assert r["positive_source_load_zone_count"]==19
    assert r["original_source_annual_load_mwh"]==pytest.approx(TOTAL)
    threshold_100=r["strict_threshold_summary"][2]
    assert threshold_100["source_zones_above_threshold"]==15
    assert threshold_100["fraction_of_total_source_efs_annual_load"]==pytest.approx(15/19)
    assert r["top_three_source_distances"][0]["single_bus_straight_line_coordinate_distance_km"]==475.
    assert not r["full_western_opf_solved"]

def test_source_distance_changed_id_mismatch_fails():
    d=source()
    d.loc[3,"candidate_id_changed"]=False
    with pytest.raises(ValueError,match="flags inconsistent"):
        summarize(d)

def test_wrong_source_annual_totals_rejected():
    d=source()
    d.loc[1,"original_annual_mwh"]*=.5
    with pytest.raises(ValueError,match="annual source demand"):
        summarize(d)
