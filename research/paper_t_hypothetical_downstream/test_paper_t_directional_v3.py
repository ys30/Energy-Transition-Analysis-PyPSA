import unittest
from paper_t_directional_v3 import run,summary,LAGS,SOLAR_PHASE_SHIFTS
class TestDirectional(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.rows=run()
 def test_cases(self):
  self.assertEqual(len(self.rows),300)
  self.assertEqual({r['demand_shift_h'] for r in self.rows},set(LAGS))
 def test_annual_energy(self):
  for sc in (0.5,1.0,1.5,2.0):
   for h in (16,18,19,20,22):
    for phase in SOLAR_PHASE_SHIFTS:
     a=[r for r in self.rows if (r['solar_scale'],r['evening_peak_hour'],r['solar_phase_shift_h'])==(sc,h,phase)]
     self.assertEqual(len(a),5)
     self.assertEqual(len({r['demand_energy_mwh'] for r in a}),1)
     self.assertEqual(len({r['solar_energy_mwh'] for r in a}),1)
 def test_zero_controls(self):
  self.assertTrue(all(r['peak_delta_pct']==0 and r['overlap_delta_pp']==0 for r in self.rows if r['demand_shift_h']==0))
 def test_bounds(self):
  self.assertTrue(all(0<=r['solar_overlap_pct']<=100 for r in self.rows))
 def test_partition(self):
  self.assertTrue(all(r['peak_increase']+r['peak_decrease']+r['peak_unchanged']==60 for r in summary(self.rows)))
if __name__=='__main__':unittest.main()
