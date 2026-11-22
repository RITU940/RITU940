import importlib.util
from pathlib import Path
import unittest
import datetime as dt

path=Path(__file__).resolve().parents[1]/'scripts'/'update_pr_graph.py'
spec=importlib.util.spec_from_file_location('activity',path)
a=importlib.util.module_from_spec(spec)
spec.loader.exec_module(a)

class TestGraph(unittest.TestCase):
    def test_month_range_across_new_year(self):
        months=a.months_last_year(dt.date(2027,1,31))
        self.assertEqual((len(months),months[0],months[-1]),(12,'2026-02','2027-01'))
    def test_pr_open_and_merge_dates_are_separate(self):
        months=['2026-10','2026-11']
        o=[{'id':'1','createdAt':'2026-10-28T09:00:00Z','mergedAt':'2026-11-10T09:00:00Z','repository':{'nameWithOwner':'OSGeo/grass'}}]
        merged=o+[{'id':'2','createdAt':'2025-10-28T09:00:00Z','mergedAt':'2026-11-12T09:00:00Z','repository':{'nameWithOwner':'opencv/opencv'}}]
        d=a.aggregate(o,merged,months)
        self.assertEqual(d['opened'],{'2026-10':1,'2026-11':0})
        self.assertEqual(d['merged'],{'2026-10':0,'2026-11':2})
        self.assertEqual(d['repos'],2)
    def test_deduplicates(self):
        p={'id':'1','createdAt':'2026-11-03T09:00:00Z','mergedAt':'2026-11-04T09:00:00Z','repository':{'nameWithOwner':'repo/A'}}
        d=a.aggregate([p,p],[p,p],['2026-11'])
        self.assertEqual(d['opened']['2026-11'],1)
        self.assertEqual(d['merged']['2026-11'],1)
    def test_placeholder_clearly_not_real(self):
        s=a.svg_chart(None,'')
        self.assertIn('no made-up numbers',s)
    def test_preview_clearly_watermarked(self):
        d={'months':['2026-11'],'opened':{'2026-11':1},'merged':{'2026-11':0},'repos':1}
        self.assertIn('SAMPLE DATA',a.svg_chart(d,'test',True))

if __name__=='__main__':unittest.main()
