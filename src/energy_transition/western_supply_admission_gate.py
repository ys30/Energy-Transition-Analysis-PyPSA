"""Cross-source Western generation admission audit; never creates missing assets.

Read-only check of PyPSA network readiness plus an explicit optional
generation evidence manifest. 'No manifest' is a measurable blocked state,
not an excuse to substitute illustrated renewable curves.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd


def _manifest_gate(manifest: dict | None) -> dict:
    required = {
        "generator_asset_source": str,
        "generator_asset_revision": str,
        "generator_asset_year": int,
        "generator_to_bus_mapping_source": str,
        "capacity_source": str,
        "technology_fuel_source": str,
        "hourly_wind_availability_source": str,
        "hourly_solar_availability_source": str,
        "dispatchable_generator_constraints_source": str,
        "fuel_cost_and_marginal_cost_source": str,
        "snapshot_alignment_evidence": str,
        "source_geography_evidence": str,
    }
    if manifest is None:
        missing=sorted(required)
        return {"manifest_provided":False,"missing_manifest_fields":missing,
                "field_types_valid":False,"source_claims_independently_verified":False}
    missing=[k for k,typ in required.items()
             if not isinstance(manifest.get(k),typ)
             or (typ is str and not manifest.get(k).strip())]
    return {"manifest_provided":True,"missing_manifest_fields":missing,
            "field_types_valid":not missing,
            "source_claims_independently_verified":False}


def inspect_western_supply(n, *, manifest:dict|None=None)->dict:
    buses=set(map(str,n.buses.index))
    generators=n.generators
    gen_count=len(generators)
    generator_buses=set(map(str,generators.bus)) if gen_count else set()
    orphan_buses=sorted(generator_buses-buses)
    p_nom=pd.to_numeric(generators.p_nom,errors="coerce") if gen_count else pd.Series(dtype=float)
    valid_capacity=bool(gen_count and p_nom.notna().all()
                        and np.isfinite(p_nom.to_numpy(dtype=float)).all()
                        and p_nom.gt(0).all())
    carrier=pd.Series(generators.carrier,dtype="object").fillna("").astype(str).str.strip() if gen_count and "carrier" in generators else pd.Series(dtype=str)
    valid_carriers=bool(gen_count and len(carrier)==gen_count and carrier.ne("").all())
    dynamic=n.generators_t.p_max_pu if hasattr(n.generators_t,"p_max_pu") else pd.DataFrame(index=n.snapshots)
    gen_names=set(map(str,generators.index))
    dynamic_names=set(map(str,dynamic.columns))
    missing_dynamic=sorted(gen_names-dynamic_names)
    dynamic_extra=sorted(dynamic_names-gen_names)
    dynamic_complete=False
    if gen_count and len(n.snapshots)>0 and not missing_dynamic and not dynamic_extra:
        a=dynamic.reindex(index=n.snapshots,columns=generators.index)
        try:
            v=a.to_numpy(dtype=float)
            dynamic_complete=bool(v.shape==(len(n.snapshots),gen_count) and
                                  np.isfinite(v).all() and
                                  ((v>=0)&(v<=1)).all())
        except (ValueError,TypeError):
            dynamic_complete=False
    loads=n.loads
    load_count=len(loads)
    snapshot_count=len(n.snapshots)
    # Numeric gates are necessary, NOT proof of empirical generator or snapshot sources.
    numeric={
        "network_has_buses":bool(buses),
        "network_has_loads":load_count>0,
        "network_has_generators":gen_count>0,
        "generator_buses_exist":gen_count>0 and not orphan_buses,
        "generator_capacities_positive_and_finite":valid_capacity,
        "generator_carriers_present":valid_carriers,
        "every_generator_has_complete_0_to_1_dynamic_availability":dynamic_complete,
        "multiple_network_snapshots":snapshot_count>1,
    }
    md=_manifest_gate(manifest)
    return {
        "bus_count":len(buses),"line_count":len(n.lines),
        "transformer_count":len(n.transformers),
        "generator_count":gen_count,"load_count":load_count,
        "snapshot_count":snapshot_count,
        "generator_nominal_capacity_mw":float(p_nom.sum()) if gen_count else 0.,
        "orphan_generator_buses":orphan_buses,
        "generators_without_dynamic_availability":missing_dynamic,
        "unmatched_availability_columns":dynamic_extra,
        "numerical_prerequisites":numeric,
        "evidence_manifest":md,
        "source_generator_fleet_verified":False,
        "source_wind_solar_hourly_profiles_verified":False,
        "efs_to_supply_utc_alignment_verified":False,
        "source_generator_to_bus_geography_verified":False,
        "transmission_operational_limits_verified":False,
        "empirical_western_opf_admitted":False,
        "empirical_western_opf_executed":False,
        "blocked_on":[name for name,v in numeric.items() if not v]+
                     ["generator_and_availability_source_provenance",
                      "common_utc_generator_load_snapshot_contract",
                      "generator_to_bus_and_branch_operating_validation"],
        "note":"Sourced BA 2024 observations and illustrative wind/solar profiles cannot be silently imported as validated 2030/2040/2050 Western generator forecasts.",
    }


def main():
    import pypsa
    p=argparse.ArgumentParser()
    p.add_argument("--network",type=Path,required=True)
    p.add_argument("--manifest",type=Path)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    m=json.loads(a.manifest.read_text()) if a.manifest else None
    r=inspect_western_supply(pypsa.Network(str(a.network)),manifest=m)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(r,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in r.items() if k not in (
        "orphan_generator_buses","generators_without_dynamic_availability",
        "unmatched_availability_columns")},indent=2))

if __name__=="__main__":
    main()
