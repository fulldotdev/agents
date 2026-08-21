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
    def test_company_item_keeps_google_contacts_separate_from_persons(self):
        row = {"id": "company", "properties": {
            "Google contacts": {"type": "multi_select", "multi_select": [{"name": "Sil"}]},
            "Persons": relation("person"),
        }}

        item = common.company_item(row)

        self.assertEqual(item["google_contacts"], ["Sil"])
        self.assertEqual(item["persons"], ["person"])
        self.assertNotIn("contacts", item)

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
