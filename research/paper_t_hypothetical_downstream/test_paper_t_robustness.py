import unittest
from paper_t_robustness import run, summarize, SOLAR_SCALES, EVENING_PEAK_HOURS
class TestGrid(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.rows=run()
    def test_60_cases(self): self.assertEqual(len(self.rows),60)
    def test_energy_conserved(self):
        for sc in SOLAR_SCALES:
            for hr in EVENING_PEAK_HOURS:
                x=[r for r in self.rows if r['solar_scale']==sc and r['evening_peak_hour']==hr]
                self.assertEqual(len(set(r['demand_energy_mwh'] for r in x)),1)
                self.assertEqual(len(set(r['solar_energy_mwh'] for r in x)),1)
    def test_zero_shift_controls(self):
        for r in self.rows:
            if r['lag_h']==0:
                self.assertAlmostEqual(r['peak_delta_pct'],0)
                self.assertAlmostEqual(r['overlap_delta_pp'],0)
    def test_summary(self):
        for r in summarize(self.rows):
            self.assertEqual(r['peak_increase']+r['peak_decrease']+r['peak_unchanged'],20)
if __name__=='__main__': unittest.main()
