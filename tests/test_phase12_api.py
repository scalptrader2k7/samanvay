from pathlib import Path
import tempfile, unittest
from fastapi.testclient import TestClient
from api_service import Settings, create_app
from service_storage import LocalWorkspaceStorage

class Phase12ApiTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory(); self.storage=LocalWorkspaceStorage(Path(self.temp.name)/'s')
  self.storage.create_workspace('public-demo','owner',public_read=True)
  self.storage.create_workspace('private-demo','other',public_read=False)
  self.client=TestClient(create_app(settings=Settings(demo_token='secret',demo_subject='owner'),storage=self.storage))
 def tearDown(self): self.client.close(); self.temp.cleanup()
 def test_contract_examples_and_preview_are_read_only(self):
  base='/api/v1/workspaces/public-demo/integration'
  contract=self.client.get(base+'/contract'); self.assertEqual(contract.status_code,200); self.assertFalse(contract.json()['erp_writes'])
  data=self.client.get(base+'/examples').json()['items']; self.assertEqual(len(data),2)
  before=self.client.get('/api/v1/workspaces/public-demo/materials').json()['total']
  outputs=[]
  for example in data:
   response=self.client.post(base+'/validate-preview',json=example); self.assertEqual(response.status_code,200,response.text)
   body=response.json(); self.assertFalse(body['persisted']); self.assertFalse(body['erp_writes']); self.assertEqual(body['report']['input_rows'],2); outputs.append(body)
  self.assertEqual(self.client.get('/api/v1/workspaces/public-demo/materials').json()['total'],before)
  for i in range(2):
   self.assertEqual(outputs[0]['matching_records'][i]['source_record_id'],outputs[1]['matching_records'][i]['source_record_id'])
   self.assertEqual(outputs[0]['matching_records'][i]['description_normalized'],outputs[1]['matching_records'][i]['description_normalized'])
  self.assertIsNone(outputs[1]['canonical_records'][0]['legacy_material_code'])
 def test_access_limits_and_validation(self):
  self.assertEqual(self.client.get('/api/v1/workspaces/private-demo/integration/contract').status_code,403)
  example=self.client.get('/api/v1/workspaces/public-demo/integration/examples').json()['items'][0]
  example['rows'][0]['corpus_id']=7
  self.assertEqual(self.client.post('/api/v1/workspaces/public-demo/integration/validate-preview',json=example).status_code,422)
 def test_interface_exposes_preview_boundary(self):
  page=self.client.get('/').text; script=self.client.get('/static/app.js').text
  for value in ('CPSE / SAP integration preview','No SAP or ERP writes','Explicit field mapping'): self.assertIn(value,page)
  for value in ('/integration/contract','/integration/examples','/integration/validate-preview'): self.assertIn(value,script)
if __name__=='__main__': unittest.main()
