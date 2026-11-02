"""Audit reporting-month exposure of changed generators without assuming daily dispatch."""
import argparse,json
from pathlib import Path

CASES=[("66183","CWE","operating",207.9),("66811","CW3","operating",100.0),("2454","1","retirement",75.0)]

def audit(folder,out):
    rows=[]
    for plant,generator,event,mw in CASES:
        path=folder/f"plant_{plant}_generator_{generator}_2024.json"
        data=json.loads(path.read_text())
        records=[r for r in data["generator_records"] if str(r["generator_id"]).strip()==generator]
        if len(records)!=1:raise ValueError(f"Expected one verified source record: {plant}/{generator}")
        rec=records[0]
        fields=rec["source_date_fields"]
        month=int(str(fields[f"{event} month"]).strip())
        year=int(str(fields[f"{event} year"]).strip())
        if year!=2024 or not 1<=month<=12:raise ValueError("Invalid source event year/month")
        # A month-level reporting date does not specify the operational day.
        # Only months strictly after commissioning or strictly before retirement are unambiguous.
        for m in range(1,13):
            if event=="operating":
                status="before_commissioning" if m<month else ("transition_month_unknown_day" if m==month else "after_commissioning")
            else:
                status="before_retirement" if m<month else ("transition_month_unknown_day" if m==month else "after_retirement")
            rows.append({"plant_id":plant,"generator_id":generator,"nameplate_mw":mw,
                         "year":2024,"month":m,"event":event,"reported_event_month":month,
                         "temporal_class":status,"measured_generation_mwh":None,
                         "verified_bus_connection":False})
    out.parent.mkdir(parents=True,exist_ok=True)
    import csv
    with out.open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    report={"case_count":len(CASES),"rows":len(rows),
            "operating_dates_reported":{"66183/CWE":"2024-01","66811/CW3":"2024-09"},
            "retirement_dates_reported":{"2454/1":"2024-01"},
            "month_of_event_not_assumed_full_month":True,
            "observed_eia923_generation_not_yet_joined":True,
            "empirical_network_dispatch_approved":False}
    out.with_suffix(".json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--source-dir",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args();audit(a.source_dir,a.out)
