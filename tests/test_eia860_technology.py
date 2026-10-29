import pandas as pd
from energy_transition.eia860_technology import classify_generators

def test_fuel_mapping_keeps_unknown_visible():
    sample = pd.DataFrame({
        "state": ["CA", "OR", "NM", "WY"],
        "fuel": ["SUN", "WND", "INVALID", "NG"],
        "capacity_mw": [100.0, 50.0, 20.0, -5.0],
    })
    mapped = classify_generators(sample)
    assert mapped.technology.iloc[0] == "solar"
    assert mapped.technology.iloc[1] == "wind"
    assert mapped.mapping_status.tolist() == [
        "mapped", "mapped", "unmapped_fuel", "invalid_capacity"
    ]
    assert mapped.loc[mapped.mapping_status.eq("mapped"), "capacity_mw"].sum() == 150.0
