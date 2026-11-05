import json
from pathlib import Path
from types import SimpleNamespace

import pandas as pd
import pytest

from energy_transition.eia860_archived_candidate_structural_gate import assess

ROOT = Path(__file__).resolve().parents[1]

def source_inputs():
    ledger = json.loads((ROOT/"data/eia860_top3_official_transmission_evidence.json").read_text())
    provenance = json.loads((ROOT/"docs/western_source_network_provenance.json").read_text())
    return ledger, provenance

def fixture_network():
    buses = pd.DataFrame({"v_nom": [115., 115., 115.]},
                         index=["2053003", "2053019", "2053021"])
    lines = pd.DataFrame({"bus0":["2053003","2053021"],"bus1":["2053019","2053003"]},
                         index=["l1","l2"])
    transformers = pd.DataFrame(columns=["bus0","bus1"])
    links = pd.DataFrame(columns=["bus0","bus1"])
    return SimpleNamespace(buses=buses, lines=lines, transformers=transformers, links=links)

def test_archived_candidate_is_not_real_poi():
    ledger, provenance = source_inputs()
    report = assess(fixture_network(), ledger, provenance)
    assert report["incident_lines"] == 2
    assert report["incident_transformers"] == 0
    assert report["line_neighbor_ids"] == ["2053019","2053021"]
    assert report["historical_nameplate_reviewed_mw"] == pytest.approx(1647.7)
    assert report["independently_verified_electrical_poi_count"] == 0
    assert report["admitted_real_generator_mw"] == 0
    assert not report["full_western_opf_admitted"]

def test_reject_unexpected_voltage():
    ledger, provenance = source_inputs()
    network = fixture_network()
    network.buses.at["2053003","v_nom"] = 230.
    with pytest.raises(ValueError, match="voltage changed"):
        assess(network, ledger, provenance)

def test_reject_topology_drift():
    ledger, provenance = source_inputs()
    network = fixture_network()
    network.lines.loc["l3"]=["2053003","2053019"]
    with pytest.raises(ValueError, match="topology differs"):
        assess(network, ledger, provenance)

def test_reject_unsupported_admission():
    ledger, provenance = source_inputs()
    provenance["eia860_electrical_interconnection_approved"] = True
    with pytest.raises(ValueError, match="Unsupported"):
        assess(fixture_network(), ledger, provenance)
