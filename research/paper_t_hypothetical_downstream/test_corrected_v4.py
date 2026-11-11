import unittest
from paper_t_corrected_v4 import run,diagnose,profiles,SCALES,LAGS
class TestV4(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.old=run("legacy");cls.new=run("seasonal")
 def test_300_cases(self):self.assertEqual(len(self.new),300)
 def test_75_groups(self):self.assertEqual(len(diagnose(self.new)),75)
 def test_lags(self):self.assertEqual(set(x["demand_shift_h"] for x in self.new),set(LAGS))
 def test_annual_conservation(self):
  for h in (16,18,19,20,22):
   for ph in (-2,0,2):
    for sc in SCALES:
     r=[x for x in self.new if (x["evening_peak_hour"],x["solar_phase_h"],x["solar_scale"])==(h,ph,sc)]
     self.assertEqual(len(set(round(x["annual_demand_mwh"],4) for x in r)),1)
     self.assertEqual(len(set(round(x["annual_solar_mwh"],4) for x in r)),1)
 def test_zero_baseline(self):self.assertTrue(all(abs(x["peak_delta_mw"])<1e-8 for x in self.new if x["demand_shift_h"]==0))
 def test_legacy_defect(self):self.assertTrue(all(x["peak_spread_mw"]<1e-6 for x in diagnose(self.old)))
 def test_seasonal_scale(self):self.assertEqual(sum(x["peak_spread_mw"]>1e-6 for x in diagnose(self.new)),29)
 def test_seasonal_delta(self):self.assertEqual(sum(x["delta_spread_mw"]>1e-6 for x in diagnose(self.new)),37)
 def test_some_pv_at_peak(self):self.assertGreater(sum(x["any_pv_at_peak"] for x in diagnose(self.new)),0)
 def test_overlap_bounds(self):self.assertTrue(all(0<=x["overlap_pct"]<=100 for x in self.new))
 def test_no_negative_solar(self):
  d,p=profiles(19,1,0)
  self.assertTrue((p>=0).all())
if __name__=="__main__":unittest.main()
