import pytest
from energy_transition.pypsa_usa_dag_report import summarize, REQUIRED, EXPECTED_TARGET

def example():
    rules = "\n".join(f"rule {name}:\n    input: dummy" for name in sorted(REQUIRED - {"data_model"}))
    return rules + f"\nlocalrule data_model:\n    input: {EXPECTED_TARGET}\nJob stats:\n total   29\n"

def test_dag_evidence():
    result = summarize(example())
    assert result["jobs_total"] == 29
    assert result["data_model_input_network"] == EXPECTED_TARGET
    assert result["true_network_built"] is False

def test_reject_wrong_final_target():
    with pytest.raises(ValueError, match="Unexpected data_model target"):
        summarize(example().replace(EXPECTED_TARGET, "wrong.nc"))

def test_reject_missing_upstream_dependency():
    with pytest.raises(ValueError, match="Incomplete"):
        summarize(example().replace("rule retrieve_nrel_efs_data:", "rule other:"))
