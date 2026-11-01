"""Pinned upstream configuration checks without downloading a full network."""
from pathlib import Path

import pytest
from energy_transition.pypsa_usa_build_preflight import preflight, PIN


def make_checkout(tmp_path, *, horizons=None):
    root = tmp_path / "pypsa-usa"
    (root / "workflow" / "config").mkdir(parents=True)
    (root / "workflow" / "Snakefile").write_text(
        "\n".join(f'configfile: "config/config.{name}.yaml"' for name in
                  ("cluster", "common", "plotting", "api", "sector")))
    (root / "workflow" / "config" / "config.default.yaml").write_text(
        "scenario:\n"
        "  interconnect: [western]\n"
        f"  planning_horizons: {horizons or '[2030, 2040, 2050]'}\n"
        "electricity:\n"
        "  demand:\n"
        "    profile: efs\n"
        "    scenario:\n"
        "      efs_case: reference\n"
        "      efs_speed: moderate\n"
        "model_topology:\n"
        "  transmission_network: reeds\n"
        "  topological_boundaries: reeds_zone\n")
    for name in ("cluster", "common", "plotting", "api", "sector"):
        (root / "workflow" / "config" / f"config.{name}.yaml").write_text("{}\n")
    return root


def test_pinned_western_preflight(monkeypatch, tmp_path):
    root = make_checkout(tmp_path)
    monkeypatch.setattr(
        "energy_transition.pypsa_usa_build_preflight.subprocess.check_output",
        lambda args, **kwargs: "" if "status" in args else PIN + "\n")
    report = preflight(root)
    assert report["upstream_sha"] == PIN
    assert report["real_network_built"] is False
    assert len(report["config_file_sha256"]) == 6
    assert len(report["snakefile_sha256"]) == 64


def test_preflight_rejects_changed_planning_years(monkeypatch, tmp_path):
    root = make_checkout(tmp_path, horizons="[2035, 2050]")
    monkeypatch.setattr(
        "energy_transition.pypsa_usa_build_preflight.subprocess.check_output",
        lambda args, **kwargs: "" if "status" in args else PIN + "\n")
    with pytest.raises(ValueError, match="config mismatch"):
        preflight(root)


def test_preflight_rejects_wrong_upstream_revision(monkeypatch, tmp_path):
    root = make_checkout(tmp_path)
    monkeypatch.setattr(
        "energy_transition.pypsa_usa_build_preflight.subprocess.check_output",
        lambda *args, **kwargs: "0" * 40 + "\n")
    with pytest.raises(ValueError, match="commit mismatch"):
        preflight(root)


def test_preflight_rejects_dirty_tracked_checkout(monkeypatch, tmp_path):
    root = make_checkout(tmp_path)
    monkeypatch.setattr(
        "energy_transition.pypsa_usa_build_preflight.subprocess.check_output",
        lambda args, **kwargs: " M workflow/Snakefile" if "status" in args else PIN + "\n")
    with pytest.raises(ValueError, match="working tree has modifications"):
        preflight(root)


def test_preflight_rejects_nonmapping_merged_yaml(monkeypatch, tmp_path):
    root = make_checkout(tmp_path)
    (root / "workflow" / "config" / "config.api.yaml").write_text("- bad\n- yaml\n")
    monkeypatch.setattr(
        "energy_transition.pypsa_usa_build_preflight.subprocess.check_output",
        lambda args, **kwargs: "" if "status" in args else PIN + "\n")
    with pytest.raises(ValueError, match="must be a YAML mapping"):
        preflight(root)
