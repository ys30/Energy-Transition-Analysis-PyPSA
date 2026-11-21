"""Official EIA-930A 2023 renewable BA/state and pseudo-tie evidence, no model validation.

Annual EIA-930A generator schedules are not a verified hour-by-hour
July 2023 installed fleet. This source-audited mapping is a *candidate*
capacity denominator and BA-state crosswalk, not an observed CF.
Source fields and provenance retained at generator row level.
"""
from __future__ import annotations
import argparse, hashlib, json, zipfile
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree as ET

from energy_transition.paper_s_eia930a_2023_workbook_inventory import (
    SOURCE_URL, MAIN, REL, PKG, local,
)

BAS=("PNM","PSCO","IPCO","WACM")
TARGET_SHEETS=("SCH 2","SCH 4")
TECH_TO_FUEL={
    "Onshore Wind Turbine":"wind",
    "Offshore Wind Turbine":"wind",
    "Solar Photovoltaic":"solar",
    "Solar Thermal with Energy Storage":"solar",
    "Solar Thermal without Energy Storage":"solar",
}
CUTOFF=(2023,7)

def _xlsx_sheet_sources(z):
    files=set(z.namelist())
    shared=[]
    if "xl/sharedStrings.xml" in files:
        root=ET.fromstring(z.read("xl/sharedStrings.xml"))
        for si in root.findall(f"{{{MAIN}}}si"):
            shared.append("".join(e.text or "" for e in si.iter() if local(e.tag)=="t"))
    rels=ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
    paths={}
    for x in rels:
        target=x.attrib.get("Target","")
        if target.startswith("/xl/"): target=target.lstrip("/")
        elif not target.startswith("xl/"): target="xl/"+target.lstrip("/")
        paths[x.attrib.get("Id")]=target
    wb=ET.fromstring(z.read("xl/workbook.xml"))
    out={}
    for sheet in wb.findall(f".//{{{MAIN}}}sheet"):
        name=sheet.attrib.get("name")
        path=paths.get(sheet.attrib.get(f"{{{REL}}}id"))
        if name in TARGET_SHEETS:
            if path not in files: raise ValueError("Missing source worksheet")
            out[name]=path
    if set(out)!=set(TARGET_SHEETS):raise ValueError("Required source schedule missing")
    return shared,out

def _rows(z,path,strings):
    root=ET.fromstring(z.read(path))
    for row in root.findall(f".//{{{MAIN}}}sheetData/{{{MAIN}}}row"):
        cells={}
        for c in row.findall(f"{{{MAIN}}}c"):
            coord=c.attrib.get("r","")
            col="".join(x for x in coord if x.isalpha())
            raw=c.find(f"{{{MAIN}}}v")
            inline=c.find(f"{{{MAIN}}}is")
            v=raw.text if raw is not None and raw.text is not None else ""
            if c.attrib.get("t")=="s" and v:v=strings[int(v)]
            elif inline is not None:v="".join(n.text or "" for n in inline.iter() if local(n.tag)=="t")
            cells[col]=v.strip() if isinstance(v,str) else v
        yield int(row.attrib["r"]),cells

def _float(value):
    if value in ("",None):return None
    try:
        v=float(value)
        if not (v>=0 and v<1e8):return None
        return v
    except (TypeError,ValueError):
        return None

def _int(value):
    if value in ("",None):return None
    try:
        v=int(float(value))
        return v
    except (TypeError,ValueError):return None

def collect(path):
    path=Path(path)
    with zipfile.ZipFile(path) as z:
        strings,sheets=_xlsx_sheet_sources(z)
        output=[]
        headers={}
        for sheet,path_in_zip in sheets.items():
            for row,c in _rows(z,path_in_zip,strings):
                if row==1:
                    headers[sheet]=c
                    continue
                ba=c.get("A","")
                if ba not in BAS:continue
                if sheet=="SCH 2":
                    idx=dict(tech="G",cap_eia860="H",state="I",county="J",
                             year="M",month="N",cap_eia930a="O",altstate="P",
                             altcounty="Q",plant="C",gen="D",
                             altplant="E",altgen="F",dynamic=None)
                else:
                    idx=dict(tech="I",cap_eia860="J",state="K",county="L",
                             year="O",month="P",cap_eia930a="Q",altstate="R",
                             altcounty="S",plant="C",gen="D",
                             altplant="E",altgen="F",dynamic="H")
                tech=c.get(idx["tech"],"")
                fuel=TECH_TO_FUEL.get(tech)
                if not fuel:continue
                state=c.get(idx["state"]) or c.get(idx["altstate"])
                county=c.get(idx["county"]) or c.get(idx["altcounty"])
                capacity_eia860=_float(c.get(idx["cap_eia860"]))
                capacity_eia930a=_float(c.get(idx["cap_eia930a"]))
                year=_int(c.get(idx["year"]))
                month=_int(c.get(idx["month"]))
                before_july=bool(year is not None and month is not None
                                 and (year,month)<=CUTOFF)
                # Sheet 4 has a different relationship to SCH2.
                # Do not add its capacities into the SCH2 denominator.
                output.append({
                    "sheet":sheet,"original_excel_row":row,"ba_code":ba,
                    "fuel":fuel,"generator_technology":tech,
                    "EIA_plant_id":c.get(idx["plant"],""),
                    "EIA_generator_id":c.get(idx["gen"],""),
                    "EIA930A_plant_id":c.get(idx["altplant"],""),
                    "EIA930A_generator_id":c.get(idx["altgen"],""),
                    "EIA860_state":c.get(idx["state"],""),
                    "EIA930A_state":c.get(idx["altstate"],""),
                    "state_for_geography":state,"county_for_geography":county,
                    "EIA860_nameplate_mw":capacity_eia860,
                    "EIA930A_nameplate_mw":capacity_eia930a,
                    "operating_year_in_source":year,"operating_month_in_source":month,
                    "operating_by_july_2023_candidate":before_july,
                    "related_BAs_pseudotie_dynamic":c.get(idx["dynamic"],"") if idx["dynamic"] else "",
                    "capacity_column_used":"EIA860" if capacity_eia860 is not None else ("EIA930A" if capacity_eia930a is not None else "unavailable"),
                    "candidate_capacity_mw":capacity_eia860 if capacity_eia860 is not None else capacity_eia930a,
                    "source_cell_BA":f"A{row}",
                    "source_cell_capacity":f"{idx['cap_eia860'] if capacity_eia860 is not None else idx['cap_eia930a']}{row}",
                    "source_cell_technology":f"{idx['tech']}{row}",
                })
    if not output:raise ValueError("No target BA wind/solar generator rows")
    return output,headers

def aggregate(rows):
    from collections import defaultdict
    combined=defaultdict(lambda:{"rows":0,"capacity_mw":0.0,"unknown_capacity_rows":0,
                                 "no_pre_july_date_rows":0,"distinct_generator_keys":set()})
    audit=Counter()
    for row in rows:
        audit[(row["sheet"],row["ba_code"],row["fuel"])]+=1
        if row["sheet"]!="SCH 2":continue
        if not row["operating_by_july_2023_candidate"]:continue
        key=(row["ba_code"],row["fuel"],row["state_for_geography"] or "UNRESOLVED")
        d=combined[key]
        d["rows"]+=1
        gen=(row["EIA_plant_id"],row["EIA_generator_id"]) if row["EIA_plant_id"] and row["EIA_generator_id"] else (row["EIA930A_plant_id"],row["EIA930A_generator_id"])
        if not gen[0] or not gen[1]:
            d["unknown_capacity_rows"]+=1
            continue
        if gen in d["distinct_generator_keys"]:
            raise ValueError("Duplicate same BA/state/fuel generator identifier in SCH 2")
        d["distinct_generator_keys"].add(gen)
        if row["candidate_capacity_mw"] is None:d["unknown_capacity_rows"]+=1
        else:d["capacity_mw"]+=row["candidate_capacity_mw"]
    table=[]
    for (ba,fuel,state),v in sorted(combined.items()):
        table.append({"ba_code":ba,"fuel":fuel,"generator_state":state,
            "source_SCH2_generator_rows":v["rows"],
            "candidate_nameplate_mw":round(v["capacity_mw"],5),
            "rows_with_unresolved_capacity_or_id":v["unknown_capacity_rows"],
            "year_month_filter":"known operation date at or before July 2023",
            "nominal_capacity_only":True})
    audit_rows=[{"schedule":s,"ba_code":ba,"fuel":fuel,"raw_source_rows":v}
                for (s,ba,fuel),v in sorted(audit.items())]
    return table,audit_rows

def audit_generator_overlap(rows):
    """Detect cross-BA assignments without arbitrarily de-duplicating BA data.

    Plant/generator IDs may appear in Schedule 2 for more than one BA; those
    observations require evidence review before using capacity totals.
    """
    from collections import defaultdict
    seen=defaultdict(lambda:{"bas":set(),"source_rows":[],"fuel":set(),"states":set()})
    missing_ids=[]
    for r in rows:
        if r["sheet"]!="SCH 2" or not r["operating_by_july_2023_candidate"]:
            continue
        plant=r["EIA_plant_id"] or r["EIA930A_plant_id"]
        gen=r["EIA_generator_id"] or r["EIA930A_generator_id"]
        if not plant or not gen:
            missing_ids.append({"BA":r["ba_code"],"source_row":r["original_excel_row"],
                                "fuel":r["fuel"],"state":r["state_for_geography"]})
            continue
        key=(str(plant),str(gen))
        obj=seen[key]
        obj["bas"].add(r["ba_code"])
        obj["source_rows"].append(f'{r["sheet"]}!{r["original_excel_row"]}')
        obj["fuel"].add(r["fuel"])
        obj["states"].add(r["state_for_geography"] or "UNRESOLVED")
    overlaps=[]
    for (plant,gen),v in sorted(seen.items()):
        if len(v["bas"])>1:
            overlaps.append({
                "EIA_or_EIA930A_plant_id":plant,"generator_id":gen,
                "reporting_BAs":";".join(sorted(v["bas"])),
                "fuel_labels":";".join(sorted(v["fuel"])),
                "generator_states":";".join(sorted(v["states"])),
                "source_excel_rows":";".join(v["source_rows"]),
                "requires_cross_BA_accounting_review":True,
            })
    return overlaps,missing_ids


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--file",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    rows,headers=collect(a.file)
    caps,audit=aggregate(rows)
    overlaps,unresolved_ids=audit_generator_overlap(rows)
    a.out.mkdir(parents=True,exist_ok=True)
    import csv
    for name,data in [
        ("eia930a_2023_four_BA_wind_solar_generator_evidence.csv",rows),
        ("eia930a_2023_four_BA_SCH2_renewable_state_capacity_candidates.csv",caps),
        ("eia930a_2023_four_BA_schedule4_pseudotie_audit_counts.csv",audit),
        ("eia930a_2023_cross_BA_generator_duplicate_candidates.csv",overlaps),
        ("eia930a_2023_missing_generator_ids.csv",unresolved_ids)]:
        if not data:continue
        with (a.out/name).open("w",newline="") as f:
            w=csv.DictWriter(f,fieldnames=data[0].keys());w.writeheader();w.writerows(data)
    manifest={
        "status":"OFFICIAL_EIA930A_2023_BA_STATE_CAPACITY_CANDIDATE_ONLY",
        "source_url":SOURCE_URL,"source_sha256":hashlib.sha256(a.file.read_bytes()).hexdigest(),
        "source_workbook_sheets":list(headers),
        "BA_codes":list(BAS),"generator_evidence_rows":len(rows),
        "SCH2_state_capacity_candidates":len(caps),
        "cross_BA_generator_overlap_candidates":len(overlaps),
        "generator_rows_without_verified_ids":len(unresolved_ids),
        "cross_BA_overlaps_not_deduplicated_or_apportioned":True,
        "SCH4_relationship_only_not_added_to_denominator":True,
        "candidate_not_confirmed_in_service_2023_July_hourly":True,
        "capacity_unit":"MW (nameplate)","EIA930_generation_unit":"MW (net reported)",
        "BA_state_capacity_is_real_hourly_capacity_factor":False,
        "direct_ReEDS_model_validation":False,
    }
    (a.out/"eia930a_2023_four_BA_mapping_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print("EIA930A_2023_BA_STATE_CAPACITY_AUDIT",json.dumps(manifest))
if __name__=="__main__":main()
