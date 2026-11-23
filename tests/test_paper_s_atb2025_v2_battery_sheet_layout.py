"""Structural tests for v2 source-cell inventory, never synthetic cost results."""
from __future__ import annotations
import zipfile
from pathlib import Path
import pytest
from energy_transition.paper_s_atb2025_v2_battery_sheet_layout import (
    shared_strings,sheet_paths,read_rows,TARGET_SHEETS,REQUIRED_SHA256
)


def test_expected_updated_edition_digest_is_64_lowercase_hex():
    assert len(REQUIRED_SHA256)==64
    assert all(c in '0123456789abcdef' for c in REQUIRED_SHA256)


def test_target_sheets_require_capacity_expansion_and_cost_aggregation():
    assert 'Utility-Scale Battery - R&D' in TARGET_SHEETS
    assert 'Utility-Scale Battery - Expand' in TARGET_SHEETS
    assert 'Summary_CAPEX' in TARGET_SHEETS
    assert 'Summary_FOM' in TARGET_SHEETS


def test_parse_minimal_xlsx_source_cells(tmp_path:Path):
    root='http://schemas.openxmlformats.org/spreadsheetml/2006/main'
    rel='http://schemas.openxmlformats.org/officeDocument/2006/relationships'
    pkg='http://schemas.openxmlformats.org/package/2006/relationships'
    wb=f'<workbook xmlns="{root}" xmlns:r="{rel}"><sheets><sheet name="Utility-Scale Battery - R&amp;D" sheetId="1" r:id="rId1"/></sheets></workbook>'
    relationships=f'<Relationships xmlns="{pkg}"><Relationship Id="rId1" Target="worksheets/sheet1.xml" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet"/></Relationships>'
    sh=f'<worksheet xmlns="{root}"><sheetData><row r="1"><c r="A1" t="s"><v>0</v></c><c r="B1"><f>2+2</f><v>4</v></c></row></sheetData></worksheet>'
    strings=f'<sst xmlns="{root}"><si><t>2030</t></si></sst>'
    p=tmp_path/'minimal.xlsx'
    with zipfile.ZipFile(p,'w') as z:
        z.writestr('xl/workbook.xml',wb)
        z.writestr('xl/_rels/workbook.xml.rels',relationships)
        z.writestr('xl/worksheets/sheet1.xml',sh)
        z.writestr('xl/sharedStrings.xml',strings)
    with zipfile.ZipFile(p) as z:
        assert shared_strings(z)==['2030']
        path=sheet_paths(z)['Utility-Scale Battery - R&D']
        rows=list(read_rows(z,path,shared_strings(z)))
    assert len(rows)==1
    assert rows[0][0]==1
    assert rows[0][1][0]['cached_value']=='2030'
    assert rows[0][1][1]['cached_value']=='4'
    assert rows[0][1][1]['formula']=='2+2'
