import pytest

from energy_transition.naris2024_interface_intake import directional_link_records, inspect_csv

HEADER = "interface,r,rr,MW_f0,MW_r0,MW_f1,MW_r1\n"


def test_asymmetric_interface_creates_two_directed_links():
    data = (HEADER + "p1||p2,p1,p2,100,40,0,0\n").encode()
    report = inspect_csv(data)
    links = directional_link_records(data)
    assert report["asymmetric_base_directional_capacity"] == 1
    assert [(x["bus0"], x["bus1"], x["p_nom"]) for x in links] == [
        ("p1", "p2", 100.0), ("p2", "p1", 40.0)]
    assert all(x["p_min_pu"] == 0 for x in links)


def test_zero_capacity_directions_not_instantiated():
    data = (HEADER + "p1||p2,p1,p2,0,25,0,0\n"
                     + "p2||p3,p2,p3,0,0,0,0\n").encode()
    links = directional_link_records(data)
    assert len(links) == 1
    assert links[0]["bus0"] == "p2"
    assert links[0]["bus1"] == "p1"


@pytest.mark.parametrize("bad", [
    "p1||p2,p1,p2,-1,5,0,0",
    "p1||p2,p1,p2,nan,5,0,0",
    "p1||p2,p1,p2,inf,5,0,0",
])
def test_reject_bad_capacity(bad):
    with pytest.raises(ValueError):
        directional_link_records((HEADER + bad + "\n").encode())
