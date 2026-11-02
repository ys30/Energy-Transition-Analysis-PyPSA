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
      "missing_line_endpoints":int((~n.lines.bus0.isin(n.buses.index)|~n.lines.bus1.isin(n.buses.index)).sum()),
      "missing_transformer_endpoints":int((~n.transformers.bus0.isin(n.buses.index)|~n.transformers.bus1.isin(n.buses.index)).sum()),
      "full_western_opf_executed":False,
      "historical_dispatch_calibrated":False,
      "full_opf_ready":bool(len(generators)>0 and len(loads)>0 and snaps>1 and len(n.generators_t.p_max_pu.columns)>0 and len(n.loads_t.p_set.columns)>0),
      "missing_required_inputs":[name for name,ready in {
        "generators":len(generators)>0,
        "loads":len(loads)>0,
        "multiple_snapshots":snaps>1,
        "generator_availability_timeseries":len(n.generators_t.p_max_pu.columns)>0,
        "load_timeseries":len(n.loads_t.p_set.columns)>0}.items() if not ready],
      "clearwater_generator_to_bus_verified":False}
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))
if __name__=="__main__":
    a=argparse.ArgumentParser();a.add_argument("--network",type=Path,required=True);a.add_argument("--out",type=Path,required=True)
    z=a.parse_args();inspect(z.network,z.out)
