import json
import os
import unittest
from pathlib import Path

from pydantic import ValidationError


for name, value in {
    "DB_HOST": "127.0.0.1", "DB_PORT": "15432", "DB_USER": "test",
    "DB_PASSWORD": "test", "DB_NAME": "test",
    "MINIO_ROOT_USER": "test", "MINIO_ROOT_PASSWORD": "test",
}.items():
    os.environ.setdefault(name, value)

from api.current_user import current_user_id
from main import app
from schemas.cost import CostLikeChange, CostPublish
from schemas.user import UserRegister


ROOT = Path(__file__).resolve().parents[1]


class Lab3ContractTests(unittest.TestCase):
    def test_ten_rest_routes_and_no_html_routes(self):
        paths = set()
        for included in app.routes:
            routes = (included.original_router.routes
                      if hasattr(included, "original_router") else [included])
            for route in routes:
                if hasattr(route, "path"):
                    for method in route.methods:
                        paths.add((method, route.path))
        expected = {
            ("GET", "/api/costs"), ("GET", "/api/costs/feed"),
            ("GET", "/api/costs/draft"), ("POST", "/api/costs"),
            ("PUT", "/api/costs/{cost_id}"),
            ("DELETE", "/api/costs/{cost_id}"),
            ("POST", "/api/costs/{cost_id}/likes"),
            ("POST", "/api/users"), ("POST", "/api/users/auth"),
            ("POST", "/api/users/logout"),
        }
        self.assertEqual(paths, expected)

    def test_system_fields_cannot_be_published_by_client(self):
        with self.assertRaises(ValidationError):
            CostPublish(cost_description="Example", cost_behavior="fixed",
                        cost_code=21, cost_status="published")
        with self.assertRaises(ValidationError):
            CostLikeChange(is_liked=2)
        with self.assertRaises(ValidationError):
            UserRegister(user_name="x", password="short")

    def test_singleton_user(self):
        self.assertEqual(current_user_id(), 101)
        self.assertEqual(current_user_id.cache_info().currsize, 1)

    def test_both_diagrams_are_in_one_staruml_file(self):
        model = json.loads((ROOT / "docs/costs_database.mdj").read_text(encoding="utf-8"))
        self.assertEqual([item["_type"] for item in model["ownedElements"]],
                         ["ERDDataModel", "UMLModel"])
        uml = model["ownedElements"][1]["ownedElements"]
        self.assertEqual(sum(item["_type"] == "UMLClassDiagram" for item in uml), 1)
        self.assertEqual(sum(item["_type"] == "UMLInterface" for item in uml), 2)
        self.assertEqual(sum(len(item.get("operations", [])) for item in uml), 10)
        names = {item.get("name") for item in uml}
        self.assertTrue({"CatalogPage", "FeedPage", "AddCostPage", "LoginPage"} <= names)


if __name__ == "__main__":
    unittest.main()
