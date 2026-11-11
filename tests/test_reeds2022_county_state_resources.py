import numpy as np
import pytest

from energy_transition.reeds2022_county_state_resources import (
    STATES, parse_county_columns, validate_capacity_key_match,
    state_cf_from_county_resource_matrix, reject_uncertified_hour_energy_join
)

COLUMNS=[f"1|p{fips}001" for fips in STATES.values()]


def test_fips_parsing_and_capacity_key_reordering():
    table=validate_capacity_key_match(
        COLUMNS,list(reversed(COLUMNS)),[4,3,2,1],
        capacity_basis="ac",tech="wind")
    assert table.column.tolist()==COLUMNS
    assert table.capacity_mw.tolist()==[1,2,3,4]
    assert table.state_fips.tolist()==list(STATES.values())


def test_county_state_summation_not_ba_assignment():
    tab=validate_capacity_key_match(COLUMNS,COLUMNS,[1,2,3,4],
                                    capacity_basis="dc",tech="pv")
    matrix=np.array([[.1,.2,.3,.4],[.5,.6,.7,.8]])
    out=state_cf_from_county_resource_matrix(matrix,tab,tech="pv",
                                             pv_capacity_basis="dc")
    np.testing.assert_allclose(out.values,matrix)
    with pytest.raises(ValueError,match="above 1"):
        state_cf_from_county_resource_matrix(
            np.full((2,4),.9),tab,tech="pv",pv_capacity_basis="ac")


def test_pv_dc_and_ac_equivalent_power_if_installed_basis_consistent():
    # 1 MW AC nameplate corresponds to 1.34 MW DC array.
    tabdc=validate_capacity_key_match(COLUMNS,COLUMNS,[1.34]*4,
                                      capacity_basis="dc",tech="pv")
    tabac=validate_capacity_key_match(COLUMNS,COLUMNS,[1]*4,
                                      capacity_basis="ac",tech="pv")
    cf=np.full((1,4),.5)
    dc=state_cf_from_county_resource_matrix(cf,tabdc,tech="pv",
                                             pv_capacity_basis="dc")
    ac=state_cf_from_county_resource_matrix(cf,tabac,tech="pv",
                                             pv_capacity_basis="ac")
    np.testing.assert_allclose(dc.values*1.34,ac.values)


def test_missing_county_or_source_keys_and_unknown_denominator_fail():
    with pytest.raises(ValueError,match="county-resource"):
        parse_county_columns(["class|p28"])
    with pytest.raises(ValueError,match="do not match"):
        validate_capacity_key_match(COLUMNS,COLUMNS[:-1],[1]*3,
                                    capacity_basis="ac",tech="wind")
    with pytest.raises(ValueError,match="DC or AC"):
        validate_capacity_key_match(COLUMNS,COLUMNS,[1]*4,
                                    capacity_basis="unspecified",tech="pv")
    with pytest.raises(ValueError,match="BLOCK_PHYSICAL_JOIN"):
        reject_uncertified_hour_energy_join()
