"""Pinned PyPSA-USA EFS timezone implementation provenance audit.

Read the upstream exact immutable commit's build_demand.py / constants.py
text, never execute upstream imports or infer the EFS publisher's own clock.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from pathlib import Path

COMMIT="338af9912addbaf038c6098fe27e1e6ef099d8aa"
EXPECTED={"AZ":"US/Mountain","CA":"US/Pacific","CO":"US/Mountain",
          "ID":"US/Mountain","MT":"US/Mountain","NM":"US/Mountain",
          "NV":"US/Pacific","OR":"US/Pacific","UT":"US/Mountain",
          "WA":"US/Pacific","WY":"US/Mountain"}
OFFSETS={"US/Pacific":8,"US/Mountain":7,"US/Central":6,"US/Eastern":5}

def analyze(build:str,constants:str):
    required=[
      "class ReadEfs(ReadStrategy)",
      "def _apply_timezones(df: pd.DataFrame)",
      "df[\"UtcHourID\"] = df.LocalHourID + df.utc_shift",
      "df.UtcHourID.map(lambda x: x if x < 8761 else x - 8760)",
      "pd.to_datetime(2018, format=\"%Y\") + df.hoy",
      "EFS does not do leap-years",
    ]
    missing=[x for x in required if x not in build]
    if missing:raise ValueError("Pinned build_demand.py changed: "+repr(missing))
    if "STATE_2_TIMEZONE = {" not in constants:raise ValueError("Missing state-zone table")
    if "does not account for states with multiple time zones" not in constants:
        raise ValueError("Missing explicit upstream multi-time-zone caveat")
    block=constants.split("STATE_2_TIMEZONE = {",1)[1].split("\n}",1)[0]
    mapping=dict(re.findall(r'\"([A-Z]{2})\"\s*:\s*\"(US/[A-Za-z]+|Pacific/Honolulu)\"',block))
    for state,zone in EXPECTED.items():
        if mapping.get(state)!=zone:
            raise ValueError(f"Pinned upstream state timezone changed: {state}")
    for tz,hours in OFFSETS.items():
        pattern='if timezone == "'+tz+'":' if tz=="US/Pacific" else 'elif timezone == "'+tz+'":'
        if pattern not in build or 'return '+str(hours) not in build.split(pattern,1)[1][:55]:
            raise ValueError("Changed hardcoded offset: "+tz)
    return {
      "status":"PINNED_PYPSA_USA_EFS_CONVERSION_SOURCE_VERIFIED",
      "upstream_commit":COMMIT,
      "pinned_scripts":["workflow/scripts/build_demand.py","workflow/scripts/constants.py"],
      "build_demand_sha256":hashlib.sha256(build.encode()).hexdigest(),
      "constants_sha256":hashlib.sha256(constants.encode()).hexdigest(),
      "state_to_timezone":{s:mapping[s] for s in EXPECTED},
      "fixed_standard_timezone_offsets_to_utc_hours":OFFSETS,
      "upstream_single_timezone_assigned_to_Idaho":"US/Mountain",
      "upstream_explicitly_warns_multi_timezone_states_unhandled":True,
      "upstream_wraps_hour_of_year_at_8760":True,
      "upstream_builds_nonleap_template_using_2018":True,
      "upstream_code_is_official_EFS_2020_publisher_clock_definition":False,
      "source_minus2_minus3_offset_explained_by_this_code_alone":False,
      "Idaho_two_timezone_load_allocation_recovered":False,
      "EFS_UTC_join_authorized":False,
      "interpretation":"The pinned PyPSA-USA transformation applies one fixed state timezone offset (+7 mountain, +8 pacific) to 2020 EFS ordinal and wraps at 8760. This is a downstream model assumption, not original EFS2020 clock metadata."
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--build",required=True,type=Path)
    p.add_argument("--constants",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()
    r=analyze(a.build.read_text(),a.constants.read_text())
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(r,indent=2)+"\n")
    print(json.dumps(r,indent=2))
if __name__=="__main__":main()
