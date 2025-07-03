import unittest
import sys
import os
from fastapi.testclient import TestClient

# Adjust sys.path for relative import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app

client = TestClient(app)

class TestSearchAPI(unittest.TestCase):

    def test_search_by_department(self):
        response = client.get("/resource/employees/search", params={
            "organization_id": 1,
            "department": "HR",
            "page": 1,
            "page_size": 10
        })
        self.assertEqual(response.status_code, 200)
        results = response.json()["results"]
        for emp in results:
            self.assertEqual(emp["department"], "HR")

    def test_search_by_multiple_filters(self):
        response = client.get("/resource/employees/search", params={
            "organization_id": 1,
            "department": "Engineering",
            "status": "Active",
            "page": 1,
            "page_size": 10
        })
        self.assertEqual(response.status_code, 200)
        results = response.json()["results"]
        for emp in results:
            self.assertEqual(emp["department"], "Engineering")
            self.assertEqual(emp["status"].lower(), "active")

    def test_search_by_status_multiple_values(self):
        response = client.get("/resource/employees/search", params={
            "organization_id": 1,
            "status": "Active,Not started",
            "page": 1,
            "page_size": 10
        })
        self.assertEqual(response.status_code, 200)
        results = response.json()["results"]
        for emp in results:
            self.assertIn(emp["status"].lower(), ["active", "not started"])

    def test_invalid_status_value(self):
        response = client.get("/resource/employees/search", params={
            "organization_id": 1,
            "status": "Paused",
            "page": 1,
            "page_size": 10
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid status value", response.json()["detail"])

    def test_missing_organization_id(self):
        response = client.get("/resource/employees/search", params={
            "department": "HR",
            "page": 1,
            "page_size": 10
        })
        self.assertEqual(response.status_code, 422)  # Missing required param

    def test_invalid_organization_id(self):
        response = client.get("/resource/employees/search", params={
            "organization_id": 9999,
            "department": "HR",
            "page": 1,
            "page_size": 10
        })
        self.assertEqual(response.status_code, 404)
        self.assertIn("Invalid organization ID", response.json()["detail"])

    def test_search_by_name_partial_match(self):
        # This assumes there's an employee like "David Brown" in org 1
        response = client.get("/resource/employees/search", params={
            "organization_id": 1,
            "search": "Aarav",
            "page": 1,
            "page_size": 10
        })
        self.assertEqual(response.status_code, 200)
        results = response.json()["results"]
        self.assertTrue(len(results) > 0)
        for emp in results:
            self.assertTrue("aarav" in emp["first_name"].lower() or "aarav" in emp["last_name"].lower())


if __name__ == '__main__':
    unittest.main()
