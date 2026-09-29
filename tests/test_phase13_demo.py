from pathlib import Path
import tempfile
import unittest
from phase13_demo import run
from seed_service import load_seed_records

class Phase13DemoTests(unittest.TestCase):
 def test_seed_fallback_rebuilds_committed_candidates_without_output_pack(self):
  import os
  previous=os.getcwd()
  with tempfile.TemporaryDirectory() as temp:
   try:
    os.chdir(temp)
    records=load_seed_records()
   finally:
    os.chdir(previous)
  self.assertEqual(len(records),9245)
  self.assertEqual(records[0]['source_record_id'],'M000001')

 def test_complete_local_demo_and_no_overwrite(self):
  with tempfile.TemporaryDirectory() as temp:
   out=Path(temp)/'evidence'; result=run(out)
   self.assertEqual(result['status'],'passed')
   self.assertEqual(result['records_inserted'],9245)
   self.assertTrue(all(result['checks'].values()))
   self.assertTrue((out/'quality_pack.xlsx').is_file())
   with self.assertRaises(FileExistsError): run(out)

if __name__=='__main__': unittest.main()
