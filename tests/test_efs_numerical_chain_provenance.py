import json
import pytest
from energy_transition.efs_numerical_chain_provenance import report


def test_verified_numeric_chain_is_not_utc_admission(tmp_path):
    p=tmp_path/"raw";p.write_bytes(b"provenance")
    a=tmp_path/"source.json"
    a.write_text(json.dumps({"status":"SOURCE_STATE_TO_LAF_ZONE_HOURLY_MATCH",
      "mismatched_zonal_hour_values":0,"zonal_hour_rows_compared":100,
      "joint_utc_dispatch_admitted":False}))
    b=tmp_path/"archive.json"
    b.write_text(json.dumps({"status":"EXACT_ZONAL_TO_ARCHIVE_MW_MATCH",
      "actual_Western_OPF_admitted":False,
      "year_results":[{"year":y,"hourly_mw_mismatches":0,"hourly_load_values_compared":20}
                      for y in (2030,2040,2050)]}))
    out=report({"raw":p},a,b)
    assert out["input_artifacts"]["raw"]["bytes"]==10
    assert out["state_to_zonal_comparisons"]==100
    assert out["zone_to_netcdf_comparisons"]==60
    assert not out["full_western_physical_opf_admitted"]
    b.write_text(json.dumps({"status":"EXACT_ZONAL_TO_ARCHIVE_MW_MATCH",
      "actual_Western_OPF_admitted":False,
      "year_results":[{"year":y,"hourly_mw_mismatches":1,"hourly_load_values_compared":20}
                      for y in (2030,2040,2050)]}))
    with pytest.raises(ValueError,match="mismatches"):
        report({"raw":p},a,b)
