"""Scenario-only Colstrip transformer parameter sweep; no generator dispatch or empirical calibration."""
import argparse,csv,json
from pathlib import Path
import pypsa
from .colstrip_hypothetical_interface import build

def sweep(base,out):
    combos=[(250,.05),(250,.10),(500,.05),(500,.10),(500,.20),(750,.10),(1000,.10)]
    out.mkdir(parents=True,exist_ok=True)
    rows=[]
    for capacity,x in combos:
        tag=f"S{int(capacity)}_X{int(x*100):02d}"
        nc=out/f"SCENARIO_ONLY_{tag}.nc"
        report=out/f"SCENARIO_ONLY_{tag}.json"
        build(base,nc,report,capacity=capacity,x=x)
        n=pypsa.Network(str(nc))
        bus="SCENARIO_ONLY_colstrip_500kV"
        tf="SCENARIO_ONLY_colstrip_500_to_345"
        assert len(n.buses)==10158 and len(n.transformers)==2081
        assert str(n.transformers.loc[tf,"bus0"])==bus
        assert str(n.transformers.loc[tf,"bus1"])=="2077254"
        assert float(n.transformers.loc[tf,"s_nom"])==capacity
        assert abs(float(n.transformers.loc[tf,"x"])-x)<1e-8
        assert not n.generators.bus.astype(str).eq(bus).any()
        rows.append({"scenario":tag,"capacity_mva_hypothetical":capacity,
          "reactance_pu_hypothetical":x,"bus_count":len(n.buses),
          "transformer_count":len(n.transformers),"roundtrip_valid":True,
          "generator_dispatch_performed":False,"physical_interconnection_verified":False})
    with (out/"SCENARIO_ONLY_sensitivity_summary.csv").open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    summary={"scenario_count":len(rows),"all_roundtrips_pass":True,
      "real_generator_bus_ties_verified":0,"optimization_performed":False,
      "physical_transformer_parameters_verified":False}
    (out/"SCENARIO_ONLY_sensitivity_summary.json").write_text(json.dumps(summary,indent=2)+"\n")
    print(json.dumps(summary,indent=2))
if __name__=="__main__":
    a=argparse.ArgumentParser();a.add_argument("--network",type=Path,required=True);a.add_argument("--out",type=Path,required=True)
    z=a.parse_args();sweep(z.network,z.out)
