"""Compare identical EIA plant-generator IDs across years without conflating changing queues."""
import argparse
import json
from pathlib import Path
import pandas as pd

def compare(file_2023, file_2024, output):
    frames={}
    for year, path in ((2023,file_2023),(2024,file_2024)):
        df=pd.read_csv(path,dtype={"plant_id":"string","generator_id":"string"})
        needed={"plant_id","generator_id","nameplate_mw","reported_status","historical_operating_inventory_eligible"}
        if needed-set(df):raise ValueError(f"{year} missing {needed-set(df)}")
        if df[["plant_id","generator_id"]].isna().any().any() or df.duplicated(["plant_id","generator_id"]).any():
            raise ValueError(f"{year} invalid plant-generator keys")
        if not df.historical_operating_inventory_eligible.astype("string").str.lower().isin(["true","false"]).all():
            raise ValueError(f"{year} invalid eligibility values")
        df["op"]=df.historical_operating_inventory_eligible.astype("string").str.lower().eq("true")
        df["nameplate_mw"]=pd.to_numeric(df.nameplate_mw,errors="coerce")
        if df.loc[df.op,"nameplate_mw"].isna().any() or (df.loc[df.op,"nameplate_mw"]<=0).any():
            raise ValueError(f"{year} invalid OP capacity")
        frames[year]=df
    common_plants=set(frames[2023].plant_id)&set(frames[2024].plant_id)
    a=frames[2023].loc[frames[2023].plant_id.isin(common_plants)]
    b=frames[2024].loc[frames[2024].plant_id.isin(common_plants)]
    joined=a.merge(b,on=["plant_id","generator_id"],how="outer",suffixes=("_2023","_2024"),indicator=True,validate="one_to_one")
    for year in (2023,2024):
        eligible=joined[f"op_{year}"].fillna(False).astype(bool)
        joined[f"op_mw_{year}"]=joined[f"nameplate_mw_{year}"].where(eligible,0).fillna(0)
    joined["delta_op_mw"]=joined.op_mw_2024-joined.op_mw_2023
    op23=joined["op_2023"].fillna(False).astype(bool)
    op24=joined["op_2024"].fillna(False).astype(bool)
    joined["transition_class"]="neither_year_op"
    joined.loc[op23 & op24,"transition_class"]="continuing_op"
    joined.loc[~op23 & op24,"transition_class"]="entered_op"
    joined.loc[op23 & ~op24,"transition_class"]="exited_op"
    decomposition=joined.groupby("transition_class",as_index=False).agg(
        generator_rows=("plant_id","size"),
        op_2023_mw=("op_mw_2023","sum"),
        op_2024_mw=("op_mw_2024","sum"),
        delta_mw=("delta_op_mw","sum"))
    if abs(float(decomposition.delta_mw.sum())-float(joined.delta_op_mw.sum()))>1e-6:
        raise ValueError("OP transition decomposition does not reconcile")
    output.parent.mkdir(parents=True,exist_ok=True)
    joined.to_csv(output,index=False)
    decomposition.to_csv(output.with_name(output.stem+"_decomposition.csv"),index=False)
    both=joined.loc[joined._merge.eq("both")]
    result={
      "capacity_transition_decomposition":decomposition.to_dict(orient="records"),
      "common_priority_plant_ids":len(common_plants),
      "common_plant_generator_ids":len(both),
      "op_2023_mw_in_common_plants":float(joined.op_mw_2023.sum()),
      "op_2024_mw_in_common_plants":float(joined.op_mw_2024.sum()),
      "op_capacity_delta_mw_in_common_plants":float(joined.delta_op_mw.sum()),
      "matched_generator_both_op_mw_2023":float(both.loc[both.op_2023 & both.op_2024,"nameplate_mw_2023"].sum()),
      "matched_generator_both_op_mw_2024":float(both.loc[both.op_2023 & both.op_2024,"nameplate_mw_2024"].sum()),
      "real_bus_connections_verified":0,
      "scope":"priority intersection only; not Western system capacity and not net generation",
    }
    output.with_suffix(".json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))
    return result

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--year-2023",type=Path,required=True)
    parser.add_argument("--year-2024",type=Path,required=True)
    parser.add_argument("--out",type=Path,required=True)
    a=parser.parse_args()
    compare(a.year_2023,a.year_2024,a.out)
