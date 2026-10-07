"""Apply the teacher's layout and schema corrections to the StarUML ER model."""

import json
import uuid
from pathlib import Path


PATH = Path(__file__).resolve().parents[1] / "docs" / "costs_database.mdj"
project = json.loads(PATH.read_text(encoding="utf-8"))
data_model = project["ownedElements"][0]
diagram = next(x for x in data_model["ownedElements"] if x["_type"] == "ERDDiagram")
entities = {x["name"]: x for x in data_model["ownedElements"] if x["_type"] == "ERDEntity"}

project["name"] = "Lab2 Costs ER"
data_model["name"] = "Costs Data Model"
diagram["name"] = "Costs database"
diagram["showGrid"] = False


def new_id():
    return uuid.uuid4().hex[:22]


def entity_view(entity):
    return next(v for v in diagram["ownedViews"] if v["_type"] == "ERDEntityView" and v["model"]["$ref"] == entity["_id"])


users = entities["users"]
if not any(c["name"] == "user_password_hash" for c in users["columns"]):
    column_id = new_id()
    users["columns"].append({
        "_type": "ERDColumn", "_id": column_id,
        "_parent": {"$ref": users["_id"]},
        "name": "user_password_hash", "type": "VARCHAR", "length": 255,
        "primaryKey": False, "foreignKey": False,
        "nullable": False, "unique": False,
    })
    view = entity_view(users)
    compartment = view["subViews"][1]
    compartment["subViews"].append({
        "_type": "ERDColumnView", "_id": new_id(),
        "_parent": {"$ref": compartment["_id"]},
        "model": {"$ref": column_id}, "font": "Arial;13;0",
        "parentStyle": True, "left": 0, "top": 0,
        "width": 0, "height": 13,
    })

for column in entities["costs"]["columns"]:
    if column["name"] in ("cost_image_url", "cost_video_url"):
        column["nullable"] = False

# Compact arrangement that fits on one portrait A4 sheet when exported.
layout = {
    "users": (40, 45, 295),
    "costs": (370, 40, 335),
    "cost_likes": (80, 310, 310),
}
for name, (left, top, width) in layout.items():
    entity = entities[name]
    view = entity_view(entity)
    count = len(entity["columns"])
    view.update(left=left, top=top, width=width, height=31 + 15 * count)
    title, compartment = view["subViews"][:2]
    title.update(left=left, top=top + 5, width=width)
    compartment.update(left=left, top=top + 23, width=width, height=8 + 15 * count)
    for index, column_view in enumerate(compartment["subViews"]):
        column_view.update(left=left + 5, top=top + 28 + 15 * index,
                           width=width - 10, height=13)

relationships = [v for v in diagram["ownedViews"] if v["_type"] == "ERDRelationshipView"]
routes = [
    "335:87;370:87",             # users -> costs
    "185:121;185:310",           # users -> cost_likes
    "537:236;537:349;390:349",   # costs -> cost_likes
]
for view, route in zip(relationships, routes):
    view["points"] = route
    for label in view.get("subViews", []):
        label.pop("text", None)
    view.pop("nameLabel", None)

for entity in entities.values():
    for element in entity.get("ownedElements", []):
        if element["_type"] == "ERDRelationship":
            element["name"] = ""

PATH.write_text(json.dumps(project, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
