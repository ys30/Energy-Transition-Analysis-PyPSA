"""Tests for the hypothetical-only downstream clock sensitivity."""
import unittest
from paper_t_downstream_sensitivity import profiles, shift, run, N

class TestDownstreamSensitivity(unittest.TestCase):
    def test_shift_convention(self):
        self.assertEqual(shift([0,1,2,3,4], -2), [2,3,4,0,1])
    def test_full_year(self):
        d,s = profiles()
        self.assertEqual((len(d), len(s)), (N,N))
        self.assertTrue(all(x >= 0 for x in s))
    def test_conservation_and_sensitivity(self):
        rows = run()
        self.assertEqual([r["lag_h"] for r in rows], [0,-2,-3])
        self.assertEqual(len({r["demand_mwh"] for r in rows}), 1)
        self.assertEqual(len({r["solar_mwh"] for r in rows}), 1)
        self.assertEqual(len({r["peak_mw"] for r in rows}), 3)
        self.assertEqual(len({r["solar_overlap_fraction"] for r in rows}), 3)

if __name__ == "__main__":
    unittest.main()
