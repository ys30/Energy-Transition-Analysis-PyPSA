"""Audit actual EIA plant identifier serialization, without changing empirical volumes."""
import argparse,json,re
from pathlib import Path
import pandas as pd


def audit(frame: pd.DataFrame) -> dict:
    if "plant_id" not in frame:
        raise ValueError("Missing plant_id")
    raw=frame["plant_id"].astype("string").str.strip()
    if raw.isna().any() or raw.eq("").any():
        raise ValueError("Blank plant identifiers")
    suffix=raw.str.fullmatch(r"[0-9]+\.0").fillna(False)
    normalized=raw.str.replace(r"\.0$","",regex=True)
    nonnumeric=~normalized.str.fullmatch(r"[0-9]+").fillna(False)
    if nonnumeric.any():
        raise ValueError("Non-numeric plant identifiers")
    mapping=pd.DataFrame({"raw":raw,"canonical":normalized}).drop_duplicates()
    collisions=mapping.groupby("canonical")["raw"].nunique()
    conflicting=collisions[collisions.gt(1)]
    return {
        "source_rows":len(frame),
        "raw_unique_plant_ids":int(raw.nunique()),
        "canonical_unique_plant_ids":int(normalized.nunique()),
        "decimal_suffix_source_rows":int(suffix.sum()),
        "canonical_ids_with_multiple_raw_forms":int(len(conflicting)),
        "canonical_id_collisions":conflicting.index.tolist(),
        "caution":"Identifier format audit only; no change to EIA923/EIA930 generation accounting",
    }


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--input",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    report=audit(pd.read_csv(args.input,dtype={"plant_id":"string"}))
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))


if __name__=="__main__":
    main()
