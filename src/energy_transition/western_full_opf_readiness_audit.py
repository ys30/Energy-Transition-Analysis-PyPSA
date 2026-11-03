"""Read-only readiness audit for full Western PyPSA OPF; does NOT run OPF."""
import argparse,json
from pathlib import Path
import pypsa
import pandas as pd

def inspect(network,out):
    n=pypsa.Network(str(network))
    snaps=len(n.snapshots)
    generators=n.generators
    loads=n.loads
    dynamic_load_names=set(map(str,n.loads_t.p_set.columns)) if hasattr(n.loads_t,"p_set") else set()
    static_only_loads=sorted(set(map(str,loads.index))-dynamic_load_names)
    static_only_load_records=[{"load_id":name,
        "static_p_set_mw":float(pd.to_numeric(pd.Series([loads.loc[name,"p_set"]]),errors="coerce").fillna(0).iloc[0]),
        "bus_id":str(loads.loc[name,"bus"])} for name in static_only_loads]
    # PyPSA supports valid static p_set values as well as snapshot-specific p_set.
    # Audit their effective values rather than equating absent dynamic columns to missing energy.
    static_load_values=pd.to_numeric(loads.p_set,errors="coerce") if "p_set" in loads else pd.Series(dtype=float)
    static_only_nonzero=[name for name in static_only_loads
        if abs(float(static_load_values.loc[name]))>1e-9
        if pd.notna(static_load_values.loc[name])]
    static_only_zero=[name for name in static_only_loads
        if pd.notna(static_load_values.loc[name]) and abs(float(static_load_values.loc[name]))<=1e-9]
    static_only_invalid=[name for name in static_only_loads
        if pd.isna(static_load_values.loc[name])]
    dynamic_load= n.loads_t.p_set if hasattr(n.loads_t,"p_set") else pd.DataFrame(index=n.snapshots)
    dynamic_invalid_columns=[str(name) for name in dynamic_load.columns
        if pd.to_numeric(dynamic_load[name],errors="coerce").isna().any()]
    effective_load=dynamic_load.reindex(index=n.snapshots,columns=loads.index)
    for name in static_only_loads:
        effective_load[name]=static_load_values.loc[name]
    effective_load=effective_load.apply(pd.to_numeric,errors="coerce")
    effective_load_invalid_cells=int(effective_load.isna().sum().sum())
    # Sum is MW across hourly snapshots, numerically MWh only if every snapshot
    # represents one hour and no weights differ. This audit does not certify such semantics.
    unweighted_snapshot_load_sum=float(effective_load.sum().sum()) if not effective_load.empty else 0.0
    timeline_note=("8760 ordinal local hours in leap year; NOT full-year calendar-aligned"
        if snaps==8760 and any(str(t).startswith("2040-") for t in n.snapshots) else None)
    dynamic_generator_names=set(map(str,n.generators_t.p_max_pu.columns)) if hasattr(n.generators_t,"p_max_pu") else set()
    static_only_generators=sorted(set(map(str,generators.index))-dynamic_generator_names)
    missing_line_endpoints=int((~n.lines.bus0.isin(n.buses.index)|~n.lines.bus1.isin(n.buses.index)).sum())
    missing_transformer_endpoints=int((~n.transformers.bus0.isin(n.buses.index)|~n.transformers.bus1.isin(n.buses.index)).sum())
    # The presence of one dynamic column does not certify all load or generator components.
    gates={
        "generators":len(generators)>0,
        "loads":len(loads)>0,
        "multiple_snapshots":snaps>1,
        "generator_availability_timeseries_complete":len(generators)>0 and not static_only_generators,
        "load_timeseries_complete":len(loads)>0 and not static_only_loads,
        "load_numeric_values_complete":len(loads)>0 and effective_load_invalid_cells==0,
        "line_endpoints_valid":missing_line_endpoints==0,
        "transformer_endpoints_valid":missing_transformer_endpoints==0,
        "calendar_semantics_verified":timeline_note is None,
        # Capacity, marginal costs, and operational constraints still need independent
        # source and scenario validation; this audit cannot establish these.
        "generator_operational_inputs_verified":False,
        "transmission_operational_limits_verified":False,
    }
    report={
      "network_file":str(network.name),
      "bus_count":len(n.buses),
      "line_count":len(n.lines),
      "transformer_count":len(n.transformers),
      "generator_count":len(generators),
      "load_count":len(loads),
      "snapshot_count":snaps,
      "snapshot_first":str(n.snapshots[0]) if snaps else None,
      "snapshot_last":str(n.snapshots[-1]) if snaps else None,
      "generator_carrier_counts":generators.carrier.astype(str).value_counts().head(25).to_dict() if "carrier" in generators else {},
      "load_nominal_p_set_sum_mw":float(pd.to_numeric(loads.p_set,errors="coerce").sum()) if "p_set" in loads else None,
      "generator_nominal_p_sum_mw":float(pd.to_numeric(generators.p_nom,errors="coerce").sum()) if "p_nom" in generators else None,
      "generator_time_series_columns":len(n.generators_t.p_max_pu.columns) if hasattr(n.generators_t,"p_max_pu") else 0,
      "load_time_series_columns":len(n.loads_t.p_set.columns) if hasattr(n.loads_t,"p_set") else 0,
      "static_only_load_components":static_only_load_records,
      "static_only_nonzero_load_ids":static_only_nonzero,
      "static_only_zero_load_ids":static_only_zero,
      "static_only_invalid_load_ids":static_only_invalid,
      "dynamic_load_columns_with_invalid_values":dynamic_invalid_columns,
      "effective_load_invalid_cells":effective_load_invalid_cells,
      "unweighted_snapshot_load_sum_mw":unweighted_snapshot_load_sum,
      "unweighted_snapshot_load_sum_is_certified_annual_mwh":False,
      "time_axis_caution":timeline_note,
      "missing_line_endpoints":missing_line_endpoints,
      "missing_transformer_endpoints":missing_transformer_endpoints,
      "generator_components_without_dynamic_availability":static_only_generators,
      "load_components_without_dynamic_profile":static_only_loads,
      "readiness_gates":gates,
      "full_western_opf_executed":False,
      "historical_dispatch_calibrated":False,
      "full_opf_ready":all(gates.values()),
      "missing_required_inputs":[name for name,ready in gates.items() if not ready],
      "clearwater_generator_to_bus_verified":False}
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))
if __name__=="__main__":
    a=argparse.ArgumentParser();a.add_argument("--network",type=Path,required=True);a.add_argument("--out",type=Path,required=True)
    z=a.parse_args();inspect(z.network,z.out)
