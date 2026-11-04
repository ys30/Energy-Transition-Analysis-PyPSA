"""No real-Western OPF can be admitted from a topology/load-only network."""
import pandas as pd
import pytest
from energy_transition.western_supply_admission_gate import inspect_western_supply


class StaticFrame:
    def __init__(self, table=None):
        self.p_max_pu=table if table is not None else pd.DataFrame()


class FakeNetwork:
    def __init__(self, populated=False):
        self.buses=pd.DataFrame(index=["bus1","bus2"])
        self.lines=pd.DataFrame(index=["line1"])
        self.transformers=pd.DataFrame()
        self.snapshots=pd.Index([1,2,3])
        self.loads=pd.DataFrame({"bus":["bus1"]},index=["load1"])
        if populated:
            self.generators=pd.DataFrame(
                {"bus":["bus2"],"p_nom":[100.],"carrier":["wind"]},index=["wind1"])
            self.generators_t=StaticFrame(pd.DataFrame(
                {"wind1":[0.2,0.5,0.9]},index=self.snapshots))
        else:
            self.generators=pd.DataFrame(columns=["bus","p_nom","carrier"])
            self.generators_t=StaticFrame()


def test_load_only_network_has_missing_supply_evidence():
    r=inspect_western_supply(FakeNetwork())
    assert r["generator_count"]==0
    assert not r["numerical_prerequisites"]["network_has_generators"]
    assert not r["evidence_manifest"]["manifest_provided"]
    assert not r["empirical_western_opf_admitted"]
    assert not r["source_generator_fleet_verified"]


def test_numerically_plausible_generator_does_not_prove_empirical_provenance():
    r=inspect_western_supply(FakeNetwork(populated=True))
    assert all(r["numerical_prerequisites"].values())
    assert not r["empirical_western_opf_admitted"]
    assert not r["source_wind_solar_hourly_profiles_verified"]


def test_missing_availability_is_reported_not_assumed_flat():
    n=FakeNetwork(populated=True)
    n.generators_t.p_max_pu=pd.DataFrame(index=n.snapshots)
    r=inspect_western_supply(n)
    assert r["generators_without_dynamic_availability"]==["wind1"]
    assert not r["numerical_prerequisites"][
        "every_generator_has_complete_0_to_1_dynamic_availability"]


def test_invalid_availability_rejected():
    n=FakeNetwork(populated=True)
    n.generators_t.p_max_pu.loc[1,"wind1"]=1.2
    r=inspect_western_supply(n)
    assert not r["numerical_prerequisites"][
        "every_generator_has_complete_0_to_1_dynamic_availability"]


def test_manifest_without_independent_verification_does_not_admit():
    n=FakeNetwork(populated=True)
    m={"generator_asset_source":"EIA"}
    r=inspect_western_supply(n,manifest=m)
    assert "capacity_source" in r["evidence_manifest"]["missing_manifest_fields"]
    assert not r["evidence_manifest"]["source_claims_independently_verified"]
    assert not r["empirical_western_opf_admitted"]
