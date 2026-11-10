import numpy as np
import pytest
from energy_transition.efs_idaho_two_offset_falsification import (
    N, aligned, analyze, fit_weight, metrics,
)


def test_fits_known_convex_mixture():
    x = np.linspace(10, 20, 100)
    z = np.linspace(30, 50, 100)
    y = .7 * x + .3 * z
    assert fit_weight(y, x, z) == pytest.approx(.7)


def test_common_nonwrapping_support_and_direction():
    x = np.arange(N, dtype=float)
    idx, a, b, c = aligned(x, x, (-2, -3))
    assert len(idx) == N-3
    assert idx[0] == 0 and idx[-1] == N-4
    assert b[0] == 2 and c[0] == 3
    idx2, _, bb, cc = aligned(x, x, (2, 3))
    assert len(idx2) == N-3
    assert idx2[0] == 3 and idx2[-1] == N-1
    assert bb[0] == 1 and cc[0] == 0


def test_frozen_weight_generalizes_without_refit():
    b = 2000 + 100 * np.sin(np.arange(N) * .11) + np.arange(N) * .01
    a = .8 * np.roll(b, -2) + .2 * np.roll(b, -3)
    result = analyze({year: (a, b) for year in (2030, 2040, 2050)})
    target = result[(result.direction == "minus") & (result.window == "second_half")
                    & (result.model == "frozen_2030_firsthalf")]
    assert len(target) == 3
    assert (target.mae_mw < 1e-8).all()
    assert np.allclose(target.first_offset_weight, .8)


def test_metric_thresholds():
    got = metrics(np.array([1., 2., 3.]), np.zeros(3), np.zeros(3), .5)
    assert got["hours_over_1mw"] == 2
    assert got["compared_hours"] == 3


def test_reject_corrupted_series():
    x = np.ones(N)
    x[8] = np.nan
    with pytest.raises(ValueError):
        aligned(x, np.ones(N), (-2, -3))
