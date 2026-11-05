import pytest
from energy_transition.pinned_pypsa_usa_efs_clock_source_audit import analyze

def valid():
    build='''class ReadEfs(ReadStrategy):
def _apply_timezones(df: pd.DataFrame):
    if timezone == "US/Pacific":
        return 8
    elif timezone == "US/Mountain":
        return 7
    elif timezone == "US/Central":
        return 6
    elif timezone == "US/Eastern":
        return 5
df["UtcHourID"] = df.LocalHourID + df.utc_shift
df.UtcHourID.map(lambda x: x if x < 8761 else x - 8760)
pd.to_datetime(2018, format="Y") + df.hoy
EFS does not do leap-years
'''.replace('format="Y"','format="%Y"')
    const='''# does not account for states with multiple time zones
STATE_2_TIMEZONE = {
'''+''.join(f'    "{s}": "{tz}",\n' for s,tz in {
'AZ':'US/Mountain','CA':'US/Pacific','CO':'US/Mountain','ID':'US/Mountain',
'MT':'US/Mountain','NM':'US/Mountain','NV':'US/Pacific','OR':'US/Pacific',
'UT':'US/Mountain','WA':'US/Pacific','WY':'US/Mountain'}.items())+'}\n'
    return build,const

def test_idaho_assumption_is_not_a_publisher_clock():
    a,b=valid()
    r=analyze(a,b)
    assert r["upstream_single_timezone_assigned_to_Idaho"]=="US/Mountain"
    assert r["upstream_explicitly_warns_multi_timezone_states_unhandled"]
    assert r["upstream_wraps_hour_of_year_at_8760"]
    assert not r["EFS_UTC_join_authorized"]
    assert not r["source_minus2_minus3_offset_explained_by_this_code_alone"]

def test_missing_source_logic_fails():
    a,b=valid()
    with pytest.raises(ValueError,match="Pinned build_demand"):
        analyze(a.replace("x - 8760","x - 8761"),b)

def test_changed_idaho_timezone_fails():
    a,b=valid()
    with pytest.raises(ValueError,match="Idaho|ID"):
        analyze(a,b.replace('"ID": "US/Mountain"','"ID": "US/Pacific"'))

def test_missing_multi_zone_caveat_fails():
    a,b=valid()
    with pytest.raises(ValueError,match="caveat"):
        analyze(a,b.replace("does not account for states with multiple time zones","different phrase"))
