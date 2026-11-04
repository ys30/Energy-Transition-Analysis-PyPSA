"""Four-state LAF denominator-aligned candidate; NEVER an empirical admission.

Pinned network only. The two source-denominator exceptions are explicit
hypotheses constrained by exact source bus identity, Pd and LAF denominator.
Post-LAF offshore auxiliary buses are EXCLUDED, not zero-imputed.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd

SOURCE_DENOMS={"CA":67028.96,"NV":8033.08,"OR":9281.36,"WA":16058.07}
NATIVE={"California":"CA","Nevada":"NV","Oregon":"OR","Washington":"WA"}
EXCEPTION_IDS={"2030005":("CA","NV"),"2013019":("OR","WA")}
OFFSHORE_START=3008161


def four_state_candidate(buses:pd.DataFrame)->dict:
    required={"state","reeds_zone","reeds_state","Pd","LAF_state","substation_off"}
    if not required.issubset(buses.columns):
        raise ValueError("Required archived source fields missing")
    x=buses[buses["state"].isin(NATIVE)].copy()
    if set(x["state"])!=set(NATIVE):
        raise ValueError("Four-state source data incomplete")
    x["_native"]=x["state"].map(NATIVE)
    laf=pd.to_numeric(x.LAF_state,errors="coerce")
    pdv=pd.to_numeric(x.Pd,errors="coerce")
    ids=pd.to_numeric(x.index.astype(str),errors="coerce")
    null=laf.isna()
    offshore=x.substation_off.fillna(False).eq(True)
    offshore_id=pd.Series(np.asarray(ids)>=OFFSHORE_START,index=x.index)
    if not null.equals((offshore&offshore_id&pdv.eq(0))):
        raise ValueError("Null LAF must match exact generated offshore auxiliary signature")
    if (laf.dropna()<0).any() or not np.isfinite(laf.dropna().to_numpy()).all():
        raise ValueError("Bad non-null source LAF")
    nonaux=x.loc[~null].copy()
    nonaux["_laf"]=laf.loc[~null]
    nonaux["_pd"]=pdv.loc[~null]
    nonaux["_source"]=nonaux["_native"]
    for bus,(source,target) in EXCEPTION_IDS.items():
        if bus not in nonaux.index.astype(str):
            raise ValueError(f"Missing denominator exception bus: {bus}")
        row=nonaux.loc[bus]
        if row["_native"]!=target or row["_pd"]<=0 or row["_laf"]<=0:
            raise ValueError(f"Unexpected crossing bus: {bus}")
        if not np.isclose(row["_pd"]/row["_laf"],SOURCE_DENOMS[source],rtol=0,atol=0.01):
            raise ValueError(f"Crossing bus denominator mismatch: {bus}")
        nonaux.loc[bus,"_source"]=source
    positive=nonaux["_pd"].gt(0)&nonaux["_laf"].gt(0)
    if (nonaux.loc[nonaux["_pd"].gt(0),"_laf"].le(0)).any():
        raise ValueError("Positive Pd with nonpositive LAF")
    for source,denom in SOURCE_DENOMS.items():
        rows=nonaux.loc[positive&nonaux["_source"].eq(source)]
        if rows.empty:
            raise ValueError(f"No positive source allocation for {source}")
        observed_denoms=(rows["_pd"]/rows["_laf"]).to_numpy()
        if not np.allclose(observed_denoms,denom,rtol=0,atol=0.01):
            raise ValueError(f"Other unexplained full_state denominator records in {source}")
    weights=nonaux.groupby(["_source","reeds_zone"],sort=True)["_laf"].sum()
    totals=weights.groupby(level=0).sum()
    if set(totals.index)!=set(SOURCE_DENOMS) or not np.allclose(
        totals.loc[list(SOURCE_DENOMS)].to_numpy(),1,atol=1e-9,rtol=0):
        raise ValueError("Candidate source allocation does not conserve each state's full source mass")
    return {
        "candidate_only":True,
        "source_states":list(SOURCE_DENOMS),
        "offshore_auxiliaries_excluded_count":int(null.sum()),
        "offshore_auxiliaries_LAF_modified":False,
        "source_full_state_derived_from_pinned_denominator_inference":True,
        "source_full_state_original_labels_recovered":False,
        "source_geography_independently_validated":False,
        "crossing_bus_source_hypotheses":EXCEPTION_IDS,
        "source_state_weight_totals":{k:float(v) for k,v in totals.items()},
        "source_to_reeds_zone_candidate_weights":[
            {"source_state":str(src),"reeds_zone":str(zone),"weight":float(weight)}
            for (src,zone),weight in weights.items()],
        "EFS_demand_admitted":False,
        "empirically_validated_Western_model_solved":False,
        "warning":"Numerical conservation by inferred source denominator is not independent approval of native-to-ReEDS allocation geography.",
    }


def main():
    import pypsa
    p=argparse.ArgumentParser()
    p.add_argument("--network",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    result=four_state_candidate(pypsa.Network(str(a.network)).buses)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in result.items()
        if k!="source_to_reeds_zone_candidate_weights"},indent=2))

if __name__=="__main__":
    main()
