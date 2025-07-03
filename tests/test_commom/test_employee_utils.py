import unittest
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from fastapi import HTTPException

from app.common.employee_utils import EmployeeSearchService


class TestEmployeeSearchService(unittest.TestCase):
    def setUp(self):
        json_path = Path(__file__).parent.parent / "mock_response/test_employees.json"
        with open(json_path) as f:
            data = json.load(f)
            self.employees = [SimpleNamespace(**e) for e in data]

        self.column_config = {
            1: ["first_name", "department", "last_name", "position", "contact_info", "location", "status"],
            2: ["first_name", "department", "last_name", "position", "status", "email"]
        }

        self.organizations = [
            SimpleNamespace(id=1, name="AcmeCorp"),
            SimpleNamespace(id=2, name="BetaTech")
        ]

    @patch("app.common.employee_utils.employees", new_callable=list)
    @patch("app.common.employee_utils.organizations", new_callable=list)
    @patch("app.config.organization_fields_config.org_column_config", new_callable=dict)
    def test_filter_by_department(self, mock_config, mock_orgs, mock_emps):
        mock_emps.extend(self.employees)
        mock_orgs.extend(self.organizations)
        mock_config.update(self.column_config)

        filters = {"department": "HR"}
        results, total = EmployeeSearchService(1, filters).run(page=1, page_size=10)

        self.assertGreater(total, 0)
        for emp in results:
            self.assertEqual(emp["department"], "HR")

    @patch("app.common.employee_utils.employees", new_callable=list)
    @patch("app.common.employee_utils.organizations", new_callable=list)
    @patch("app.config.organization_fields_config.org_column_config", new_callable=dict)
    def test_filter_by_multiple_status(self, mock_config, mock_orgs, mock_emps):
        mock_emps.extend(self.employees)
        mock_orgs.extend(self.organizations)
        mock_config.update(self.column_config)

        filters = {"status": "Active,Not Started"}
        results, total = EmployeeSearchService(1, filters).run(page=1, page_size=10)

        self.assertGreater(total, 0)
        for emp in results:
            self.assertIn(emp["status"].lower(), ["active", "not started"])

    @patch("app.common.employee_utils.employees", new_callable=list)
    @patch("app.common.employee_utils.organizations", new_callable=list)
    @patch("app.config.organization_fields_config.org_column_config", new_callable=dict)
    def test_invalid_organization_id(self, mock_config, mock_orgs, mock_emps):
        mock_emps.extend(self.employees)
        mock_orgs.extend(self.organizations)
        mock_config.update(self.column_config)

        with self.assertRaises(HTTPException) as ctx:
            EmployeeSearchService(999, {"department": "HR"}).run(page=1, page_size=10)
        self.assertEqual(ctx.exception.status_code, 404)
        self.assertIn("Invalid organization ID", ctx.exception.detail)

    @patch("app.common.employee_utils.employees", new_callable=list)
    @patch("app.common.employee_utils.organizations", new_callable=list)
    @patch("app.config.organization_fields_config.org_column_config", new_callable=dict)
    def test_invalid_filter_field(self, mock_config, mock_orgs, mock_emps):
        mock_emps.extend(self.employees)
        mock_orgs.extend(self.organizations)
        mock_config.update(self.column_config)

        with self.assertRaises(HTTPException) as ctx:
            EmployeeSearchService(1, {"unknown_field": "value"}).run(page=1, page_size=10)
        self.assertEqual(ctx.exception.status_code, 400)
        self.assertIn("Invalid filter field", ctx.exception.detail)

    @patch("app.common.employee_utils.employees", new_callable=list)
    @patch("app.common.employee_utils.organizations", new_callable=list)
    @patch("app.config.organization_fields_config.org_column_config", new_callable=dict)
    def test_no_results_for_valid_filter(self, mock_config, mock_orgs, mock_emps):
        mock_emps.extend(self.employees)
        mock_orgs.extend(self.organizations)
        mock_config.update(self.column_config)

        with self.assertRaises(HTTPException) as ctx:
            EmployeeSearchService(1, {"department": "NonExistent"}).run(page=1, page_size=10)
        self.assertEqual(ctx.exception.status_code, 404)
        self.assertIn("No employees found", ctx.exception.detail)

    @patch("app.common.employee_utils.employees", new_callable=list)
    @patch("app.common.employee_utils.organizations", new_callable=list)
    @patch("app.config.organization_fields_config.org_column_config", new_callable=dict)
    def test_search_by_name_partial_match(self, mock_config, mock_orgs, mock_emps):
        mock_emps.extend(self.employees)
        mock_orgs.extend(self.organizations)
        mock_config.update(self.column_config)

        filters = {"search": "ali"}  # Should match Alice
        results, total = EmployeeSearchService(1, filters).run(page=1, page_size=10)

        self.assertGreater(total, 0)
        for emp in results:
            self.assertTrue("ali" in emp["first_name"].lower() or "ali" in emp["last_name"].lower())


if __name__ == "__main__":
    unittest.main()
