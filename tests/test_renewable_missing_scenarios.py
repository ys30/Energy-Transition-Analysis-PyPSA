import pandas as pd
from energy_transition.renewable_missing_scenarios import scenarios

def test_scenario_fills_only_missing_source_rows():
    h=pd.date_range("2024-01-01", "2025-01-01",freq="h",inclusive="left",tz="UTC")
    rows=[{"period":hour,"respondent":ba,"fueltype":fuel,"value":-2. if fuel=="SUN" else 5.}
          for hour in h for ba in ("CISO","BPAT") for fuel in ("SUN","WND")]
    data=pd.DataFrame(rows)
    data=data[~((data.period==h[10])&(data.respondent=="BPAT")&(data.fueltype=="SUN"))]
    all_results,summary=scenarios(data)
    assert summary.imputed_ba_fuel_hours.tolist()==[1,1,1]
    assert all_results.groupby("method").is_imputed.sum().eq(1).all()
    assert all_results.loc[~all_results.is_imputed & all_results.fueltype.eq("SUN"),"value_mwh"].eq(-2).all()
    assert all_results.loc[all_results.is_imputed & all_results.method.eq("zero_bound"),"value_mwh"].eq(0).all()
