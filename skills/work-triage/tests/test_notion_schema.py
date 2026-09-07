"""Canonical Notion naming tests for work-context collectors."""

import sys
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import common


def relation(*ids):
    return {"type": "relation", "relation": [{"id": value} for value in ids]}


class NotionSchemaTests(unittest.TestCase):
    def test_company_item_excludes_person_contact_sources(self):
        row = {"id": "company", "properties": {}}

        item = common.company_item(row)

        self.assertNotIn("google_contacts", item)
        self.assertNotIn("persons", item)

    def test_company_website_matches_current_schema(self):
        item = common.company_item({"properties": {"Website": {"type": "url", "url": "https://example.com"}}})
        self.assertEqual(item["website"], "https://example.com")

    def test_project_and_task_use_companies_relation(self):
        project = common.project_item({"id": "project", "properties": {
            "Companies": relation("company"),
        }})
        task = common.task_item({"id": "task", "properties": {
            "Companies": relation("company"),
        }})

        self.assertEqual(project["companies"], ["company"])
        self.assertEqual(task["companies"], ["company"])
        self.assertNotIn("customers", project)
        self.assertNotIn("customer", task)


if __name__ == "__main__":
    unittest.main()
