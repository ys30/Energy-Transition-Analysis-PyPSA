"""Create an explicitly hypothetical Colstrip 500/345-kV PyPSA topology scenario.

NOT a recovered physical transformer or a calibrated generator interconnection.
No dispatch and no generator are added. Base network is never overwritten.
"""
import argparse,json
from pathlib import Path
import pypsa

def build(network,out,report,bus345="2077254",capacity=500.0,x=0.1,r=0.01):
    if capacity<=0 or x<=0 or r<0:raise ValueError("Invalid hypothetical transformer parameters")
    n=pypsa.Network(str(network))
    if bus345 not in n.buses.index:raise ValueError(f"Missing base-network 345-kV bus: {bus345}")
    if abs(float(n.buses.loc[bus345,"v_nom"])-345)>1e-6:raise ValueError("Selected base bus is not 345 kV")
    bus500="SCENARIO_ONLY_colstrip_500kV"
    tf="SCENARIO_ONLY_colstrip_500_to_345"
    if bus500 in n.buses.index or tf in n.transformers.index:raise ValueError("Scenario identifiers already exist")
    b=n.buses.loc[bus345]
    n.add("Bus",bus500,v_nom=500.0,x=float(b.x),y=float(b.y),carrier="AC")
    n.add("Transformer",tf,bus0=bus500,bus1=bus345,s_nom=capacity,x=x,r=r)
    out.parent.mkdir(parents=True,exist_ok=True)
    n.export_to_netcdf(str(out))
    result={"scenario_only":True,"physical_asset_verified":False,
       "generator_to_original_bus_verified":False,"dispatch_or_calibration_performed":False,
       "new_bus":bus500,"new_transformer":tf,"base_345kv_bus":bus345,
       "hypothetical_s_nom_mva":capacity,"hypothetical_x_pu":x,"hypothetical_r_pu":r,
       "base_bus_count":len(n.buses)-1,"scenario_bus_count":len(n.buses),
       "base_transformer_count":len(n.transformers)-1,"scenario_transformer_count":len(n.transformers)}
    report.parent.mkdir(parents=True,exist_ok=True)
    report.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))
if __name__=="__main__":
    a=argparse.ArgumentParser()
    a.add_argument("--network",type=Path,required=True);a.add_argument("--out",type=Path,required=True)
    a.add_argument("--report",type=Path,required=True);a.add_argument("--bus345",default="2077254")
    a.add_argument("--capacity",type=float,default=500.0);a.add_argument("--x",type=float,default=0.1)
    a.add_argument("--r",type=float,default=0.01)
    z=a.parse_args();build(z.network,z.out,z.report,z.bus345,z.capacity,z.x,z.r)
