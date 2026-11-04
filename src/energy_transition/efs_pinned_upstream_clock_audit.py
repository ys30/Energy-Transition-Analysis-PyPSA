"""Evidence-only reconstruction of *pinned PyPSA-USA* EFS hour handling.

This models the historical upstream implementation, not a certified EFS
source timezone or daylight-saving interpretation.
"""
from __future__ import annotations
import ast
import hashlib
import json
from pathlib import Path

PIN="338af9912addbaf038c6098fe27e1e6ef099d8aa"
TIMEZONE_SHIFT={"US/Pacific":8,"US/Mountain":7,"US/Central":6,
                "US/Eastern":5,"US/Alaska":9,"Pacific/Honolulu":11}
WESTERN=("AZ","CA","CO","ID","MT","NM","NV","OR","UT","WA","WY")


def audit_pinned_efs_clock(demand_source: str, constants_source: str) -> dict:
    # Inspect exact pinned source contents, never evaluate upstream scripts.
    demand_tree=ast.parse(demand_source)
    constants_tree=ast.parse(constants_source)
    table=None
    for node in constants_tree.body:
        if isinstance(node,ast.Assign) and any(
            isinstance(t,ast.Name) and t.id=="STATE_2_TIMEZONE"
            for t in node.targets
        ):
            table=ast.literal_eval(node.value)
            break
    if not isinstance(table,dict):
        raise ValueError("Pinned upstream state timezone table not found")
    for state in WESTERN:
        if state not in table or table[state] not in TIMEZONE_SHIFT:
            raise ValueError(f"Unrecognized pinned source timezone: {state}")
    classes=[n for n in demand_tree.body if isinstance(n,ast.ClassDef)]
    methods=[n for c in classes for n in c.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))
             and n.name in ("_apply_timezones","_build_datetime")]
    if {m.name for m in methods}!={"_apply_timezones","_build_datetime"}:
        raise ValueError("Pinned EFS conversion methods not found")
    # These anchored tokens represent semantics of the pinned revision. A
    # future upstream change must be independently reviewed, not guessed.
    expected=[
        "df["UtcHourID"] = df.LocalHourID + df.utc_shift",
        "x if x < 8761 else x - 8760",
        "df.UtcHourID - 1",
        'pd.to_datetime(2018, format="%Y")',
        '"year": df.Year',
    ]
    if any(token not in demand_source for token in expected):
        raise ValueError("Pinned EFS UTC-hour algorithm no longer matches inspected source")
    return {
        "upstream_commit":PIN,
        "upstream_build_demand_sha256":hashlib.sha256(demand_source.encode()).hexdigest(),
        "upstream_constants_sha256":hashlib.sha256(constants_source.encode()).hexdigest(),
        "source_timezone_shifts_hours":{s:TIMEZONE_SHIFT[table[s]] for s in WESTERN},
        "clock_algorithm":"(LocalHourID + fixed_state_offset - 1) % 8760 + 1",
        "date_template_year":2018,
        "non_leap_hour_count":8760,
        "fixed_offset_ignores_daylight_saving":True,
        "source_state_timezone_table_ignores_multizone_exceptions":True,
        "upstream_implementation_reconstructed":True,
        "original_efs_local_hour_timezone_verified":False,
        "upstream_clock_equals_physical_simultaneous_utc_verified":False,
        "weather_and_generation_snapshots_synchronized":False,
        "empirical_utc_alignment_admitted":False,
        "note":"Compatibility with pinned upstream implementation is not provenance for the source dataset's time convention.",
    }


def write_report(demand_path:Path,constants_path:Path,out:Path)->None:
    result=audit_pinned_efs_clock(
        demand_path.read_text(encoding="utf-8"),
        constants_path.read_text(encoding="utf-8"))
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2))


if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("--demand-source",required=True,type=Path)
    p.add_argument("--constants-source",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()
    write_report(a.demand_source,a.constants_source,a.out)
