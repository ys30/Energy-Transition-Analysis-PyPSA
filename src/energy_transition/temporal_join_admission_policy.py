"""A reusable, fail-closed temporal-join admission policy.

Purpose: express testable *metadata/evidence gates*, distinct from a numerical
best-fit lag. This is source-agnostic policy code. It DOES NOT infer a clock
mapping or independently establish provenance; evidence flags must originate
from independently verified source records.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

GATES={
    "source_integrity": "Independent original file authenticity, hashes and scenario identity verified",
    "native_calendar": "Native hour-ending/start, calendar, leap handling, DST and physical timezone explicitly documented for BOTH inputs",
    "physical_crosswalk": "Authoritative reversible source-hour to common physical timestamp mapping verified for BOTH inputs",
    "weather_year": "Representative weather or chronological year semantics compatible and independently documented",
    "geography": "Geographical footprint and substate aggregation compatible or documented with validated disaggregation",
    "join_uniqueness": "One-to-one temporal/spatial keys verified with no duplication or silently fabricated boundary observations",
}
DEFAULT_PASSPORT={
    "source_pair":"Original EFS2020 Reference/Moderate vs published ReEDS2022 EFS_REFERENCE",
    "evidence":{
        "source_integrity":{"passed":True,"basis":"Original source archive and ReEDS HDF5 publisher MD5 audited"},
        "native_calendar":{"passed":False,"basis":"ReEDS2022 2012 CST reference known; original EFS2020 physical LocalHourID unresolved"},
        "physical_crosswalk":{"passed":False,"basis":"Fitted -2/-3 index shifts are numeric optimizers, not publisher-certified timestamps"},
        "weather_year":{"passed":False,"basis":"Original EFS2020 weather-year mapping not authenticated"},
        "geography":{"passed":False,"basis":"Idaho original sector/subsector values do not identify substate physical-timezone footprints"},
        "join_uniqueness":{"passed":False,"basis":"No admitted physical timestamp join; 2040 synthetic label issue is documented"}
    },
    "descriptive_numeric_comparison_permitted":True,
    "derived_figure_reproduction_permitted":True,
    "physical_weather_or_generation_join_requested":True
}
def assess(passport):
    if set(passport.get("evidence",{}))!=set(GATES):
        raise ValueError("Evidence passport must explicitly cover all six gates")
    details={}
    for gate,description in GATES.items():
        item=passport["evidence"][gate]
        if not isinstance(item,dict) or type(item.get("passed")) is not bool or not str(item.get("basis","")).strip():
            raise ValueError("Evidence gate requires explicit boolean and nonempty independent basis: "+gate)
        details[gate]={"passed":item["passed"],"requirement":description,"basis":item["basis"]}
    approved=all(x["passed"] for x in details.values())
    return {
      "source_pair":passport.get("source_pair","unspecified"),
      "physical_hour_join_admitted":approved,
      "failed_gates":[g for g,item in details.items() if not item["passed"]],
      "gate_results":details,
      "fitted_source_index_lag_counts_as_authoritative_clock":False,
      "no_automatic_imputation_for_failed_gates":True,
      "decision":"ADMIT_PHYSICAL_JOIN" if approved else "BLOCK_PHYSICAL_JOIN",
      "reusable_policy_contract":True,
      "this_passport_is_not_source_clock_certification":True,
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--passport",type=Path)
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()
    passport=json.loads(a.passport.read_text()) if a.passport else DEFAULT_PASSPORT
    result=assess(passport)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))
    if result["decision"]!="BLOCK_PHYSICAL_JOIN" and not a.passport:
        raise RuntimeError("EFS/ReEDS default passport must fail-closed")
if __name__=="__main__":main()
