"""Pinned EFS clock audit cannot promote unsupported UTC chronology."""
import pytest
from energy_transition.efs_pinned_upstream_clock_audit import audit_pinned_efs_clock


def fixtures():
    source='''class ReadEfs:
    def _apply_timezones(self, df):
        df.UtcHourID = df.LocalHourID + df.utc_shift
        df.UtcHourID = df.UtcHourID.map(lambda x: x if x < 8761 else x - 8760)
    def _build_datetime(self, df):
        df["hoy"] = pd.to_timedelta(df.UtcHourID - 1, unit="h")
        df["time"] = pd.to_datetime(2018, format="%Y") + df.hoy
        time = pd.to_datetime({"year": df.Year})
'''
    states=",".join(repr(s)+":'US/Mountain'" for s in
        ("AZ","CA","CO","ID","MT","NM","NV","OR","UT","WA","WY"))
    return source,"STATE_2_TIMEZONE={"+states+"}"


def test_fixed_offset_upstream_is_not_physical_utc_evidence():
    source,constants=fixtures()
    result=audit_pinned_efs_clock(source,constants)
    assert result["upstream_implementation_reconstructed"]
    assert result["fixed_offset_ignores_daylight_saving"]
    assert not result["original_efs_local_hour_timezone_verified"]
    assert not result["empirical_utc_alignment_admitted"]
    assert result["source_timezone_shifts_hours"]["AZ"]==7


def test_revised_upstream_time_algorithm_requires_review():
    source,constants=fixtures()
    with pytest.raises(ValueError,match="no longer matches"):
        audit_pinned_efs_clock(source.replace("x - 8760","x - 8784"),constants)


def test_missing_state_timezone_requires_review():
    source,constants=fixtures()
    with pytest.raises(ValueError,match="Unrecognized pinned source timezone"):
        audit_pinned_efs_clock(source,constants.replace("'AZ':'US/Mountain'","'AZ':'Unknown'"))
