import unittest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

class TestMainAPI(unittest.TestCase):
    def test_debug_test(self):
        response = client.get("/debug/test")
        self.assertEqual(response.status_code, 200)
    
    def test_invalid_api_key(self):
        response = client.post("/grade", headers={"x-api-key": "wrong"}, json={})
        self.assertEqual(response.status_code, 401)
