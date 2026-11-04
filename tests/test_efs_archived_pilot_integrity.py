"""Fail-closed EFS archived seven-state pilot arithmetic tests."""
import pandas as pd
import pytest
from energy_transition.efs_archived_pilot_integrity import audit_archived_pilot,STATE_NAMES


def fixtures():
    source=[]
    zonal=[]
    for year in (2030,2040,2050):
        for code,state in STATE_NAMES.items():
            for hour in range(3):
                source.append({"year":year,"state":code,"local_hour_id":hour,"load_mw":100+hour})
                for zone in ("p1","p2"):
                    zonal.append({"year":year,"state":state,"local_hour_id":hour,
                                  "reeds_zone":zone,"allocated_mw":(100+hour)*0.4})
    return pd.DataFrame(source),pd.DataFrame(zonal)


def test_seven_state_pilot_accepts_consistent_arithmetic_without_utc_claims():
    src,z=fixtures()
    report=audit_archived_pilot(src,z)
    assert len(report["state_year_results"])==21
    assert report["scope_state_count"]==7
    assert report["actual_western_opf_solved"] is False
    assert report["utc_alignment_verified"] is False
    assert report["source_laf_provenance_verified"] is False
    assert report["state_year_results"][0]["inferred_archived_allocation_factor"]==pytest.approx(0.8)


def test_duplicate_source_hour_rejected():
    src,z=fixtures()
    with pytest.raises(ValueError,match="Duplicate"):
        audit_archived_pilot(pd.concat([src,src.iloc[[0]]]),z)


def test_zone_hour_omission_rejected():
    src,z=fixtures()
    z=z.drop(index=z.index[0])
    with pytest.raises(ValueError,match="Incomplete zone"):
        audit_archived_pilot(src,z)


def test_nonconserving_hour_rejected():
    src,z=fixtures()
    z.loc[z.index[0],"allocated_mw"]+=10
    with pytest.raises(ValueError,match="inconsistent"):
        audit_archived_pilot(src,z)


def test_extra_year_rejected():
    src,z=fixtures()
    src.loc[src.index[0],"year"]=2024
    with pytest.raises(ValueError,match="planning years"):
        audit_archived_pilot(src,z)
