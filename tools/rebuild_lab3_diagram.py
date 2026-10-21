"""Lay out the editable StarUML class diagram on one portrait sheet."""

import copy
import json
import uuid
from pathlib import Path


PATH = Path(__file__).resolve().parents[1] / "docs" / "costs_database.mdj"
project = json.loads(PATH.read_text(encoding="utf-8"))
uml = next(e for e in project["ownedElements"] if e["_type"] == "UMLModel")
diagram = next(e for e in uml["ownedElements"] if e["_type"] == "UMLClassDiagram")
old_models = {e["name"]: e for e in uml["ownedElements"] if e.get("name")}
old_views = {v["model"]["$ref"]: v for v in diagram["ownedViews"] if v.get("model") and v["_type"] in ("UMLClassView", "UMLInterfaceView")}
page_template = old_views[old_models["CatalogPage"]["_id"]]
interface_name = "CostApi" if "CostApi" in old_models else "API catalog"
operation_name = "CostApi" if "CostApi" in old_models else "CatalogDomain"
interface_template = old_views[old_models[interface_name]["_id"]]
operation_template = old_views[old_models[operation_name]["_id"]]["subViews"][2]["subViews"][0]


def uid():
    return uuid.uuid4().hex[:22]


def ref(identifier):
    return {"$ref": identifier}


def model(name, kind="UMLClass", stereotype=None, operations=()):
    item = {"_type": kind, "_id": uid(), "_parent": ref(uml["_id"]),
            "name": name, "visibility": "public", "attributes": [], "operations": []}
    if stereotype:
        item["stereotype"] = stereotype
    for method, url in operations:
        item["operations"].append({"_type": "UMLOperation", "_id": uid(),
                                   "_parent": ref(item["_id"]), "name": url,
                                   "documentation": method, "visibility": "public"})
    uml["ownedElements"].append(item)
    return item


def new_view(item, x, y, width, height, *, page=False, circle=False):
    template = interface_template if circle else page_template
    view = copy.deepcopy(template)
    id_map = {}

    def fresh_ids(value):
        if isinstance(value, dict):
            if "_id" in value:
                old = value["_id"]
                value["_id"] = id_map.setdefault(old, uid())
            for child in value.values():
                fresh_ids(child)
        elif isinstance(value, list):
            for child in value:
                fresh_ids(child)

    def refs(value):
        if isinstance(value, dict):
            if set(value) == {"$ref"} and value["$ref"] in id_map:
                value["$ref"] = id_map[value["$ref"]]
            else:
                for child in value.values():
                    refs(child)
        elif isinstance(value, list):
            for child in value:
                refs(child)

    fresh_ids(view)
    refs(view)
    view["_parent"] = ref(diagram["_id"])
    view["model"] = ref(item["_id"])
    view["_type"] = "UMLInterfaceView" if circle else "UMLClassView"
    view.update(left=x, top=y, width=width, height=height,
                stereotypeDisplay="icon-label" if circle else "label",
                showShadow=False, wordWrap=False)
    if circle:
        view.update(suppressAttributes=True, suppressOperations=True)
    name_part, attributes, methods, parameter_part = view["subViews"]
    name_height = 42 if page else 30
    name_part.update(left=x, top=y, width=width, height=name_height, model=ref(item["_id"]))
    for label in name_part["subViews"]:
        label.update(left=x + 5, width=width - 10, showShadow=False)
    stereotype_label, name_label = name_part["subViews"][:2]
    stereotype_label.update(text="«future frontend»" if page else ("«" + item.get("stereotype", "") + "»" if item.get("stereotype") else ""),
                            visible=bool(page or item.get("stereotype")), top=y + 5)
    name_label.update(text=item["name"], top=y + (18 if page else 8))
    attributes.update(left=x, top=y + name_height, width=width,
                      height=13 if page else 0, visible=page, model=ref(item["_id"]), subViews=[])
    methods.update(left=x, top=y + name_height + (13 if page else 0), width=width,
                   height=13 if page else max(0, height - name_height),
                   visible=page or bool(item["operations"]), model=ref(item["_id"]), subViews=[])
    parameter_part.update(visible=False, model=ref(item["_id"]))
    for index, op in enumerate(item["operations"]):
        ov = copy.deepcopy(operation_template)
        ov.update(_id=uid(), _parent=ref(methods["_id"]), model=ref(op["_id"]),
                  left=x + 7, top=y + name_height + 4 + index * 16,
                  width=width - 14, text=f"+{op['name']}()",
                  showShadow=False)
        methods["subViews"].append(ov)
    diagram["ownedViews"].append(view)
    return view


def dependency(source, target, *, start=None, end=None):
    element = {"_type": "UMLDependency", "_id": uid(), "_parent": ref(uml["_id"]),
               "source": ref(source["model"]["$ref"]), "target": ref(target["model"]["$ref"])}
    uml["ownedElements"].append(element)
    p1 = start or (source["left"] + source["width"] // 2, source["top"] + source["height"])
    p2 = end or (target["left"] + target["width"] // 2, target["top"])
    diagram["ownedViews"].append({"_type": "UMLDependencyView", "_id": uid(),
                                   "_parent": ref(diagram["_id"]), "model": ref(element["_id"]),
                                   "tail": ref(source["_id"]), "head": ref(target["_id"]),
                                   "lineStyle": 1,
                                   "points": f"{p1[0]}:{p1[1]};{p2[0]}:{p2[1]}"})


def realization(domain, interface):
    """The backend domain implements its API interface (lollipop notation)."""
    element = {"_type": "UMLInterfaceRealization", "_id": uid(),
               "_parent": ref(uml["_id"]),
               "source": ref(domain["model"]["$ref"]),
               "target": ref(interface["model"]["$ref"])}
    uml["ownedElements"].append(element)
    start = (domain["left"] + domain["width"] // 2, domain["top"])
    end = (interface["left"] + interface["width"] // 2,
           interface["top"] + interface["height"])
    diagram["ownedViews"].append({"_type": "UMLInterfaceRealizationView",
                                   "_id": uid(), "_parent": ref(diagram["_id"]),
                                   "model": ref(element["_id"]),
                                   "tail": ref(domain["_id"]), "head": ref(interface["_id"]),
                                   "lineStyle": 1,
                                   "points": f"{start[0]}:{start[1]};{end[0]}:{end[1]}"})


def label(text, x, y, width, *, size=13, bold=False):
    diagram["ownedViews"].append({"_type": "UMLTextView", "_id": uid(),
                                   "_parent": ref(diagram["_id"]),
                                   "left": x, "top": y, "width": width, "height": size + 5,
                                   "font": f"Arial;{size};{int(bold)}",
                                   "fontColor": "#000000", "text": text,
                                   "horizontalAlignment": 2,
                                   "verticalAlignment": 5})


# The ER model is untouched. Replace only the class-diagram content with
# editable views for the ten implemented HTTP routes and their layers.
uml["ownedElements"] = [e for e in uml["ownedElements"] if e["_type"] == "UMLClassDiagram"]
diagram["name"] = "Lab3 backend classes and future pages (A4)"
diagram["ownedViews"] = []
diagram["showGrid"] = False

pages = []
for name, x in (("CatalogPage", 20), ("DraftPage", 175),
                ("FeedPage", 330), ("LoginPage", 485)):
    pages.append(new_view(model(name, stereotype="future frontend"), x, 20, 135, 68, page=True))

postman = new_view(model("Postman", stereotype="API client"), 270, 140, 100, 43)

interfaces = []
for name, x in (("API catalog", 20), ("API draft", 175),
                ("API feed", 330), ("API profile", 485)):
    interfaces.append(new_view(model(name, kind="UMLInterface"), x, 230, 135, 44, circle=True))
    label(name, x, 276, 135, bold=True)

label("Бэкенд", 20, 312, 600, size=15, bold=True)

domains = [
    new_view(model("CatalogDomain", stereotype="backend domain", operations=[
        ("list_costs", "GET /api/costs")]), 20, 345, 290, 72),
    new_view(model("FeedDomain", stereotype="backend domain", operations=[
        ("get_feed", "GET /api/costs/feed"),
        ("change_like", "POST /api/costs/{id}/likes")]), 330, 345, 290, 92),
    new_view(model("DraftDomain", stereotype="backend domain", operations=[
        ("get_draft", "GET /api/costs/draft"),
        ("create", "POST /api/costs"),
        ("publish", "PUT /api/costs/{id}"),
        ("delete", "DELETE /api/costs/{id}")]), 20, 480, 290, 120),
    new_view(model("ProfileDomain", stereotype="backend domain", operations=[
        ("register", "POST /api/users"),
        ("authenticate", "POST /api/users/auth"),
        ("logout", "POST /api/users/logout")]), 330, 480, 290, 108),
]

label("Модель", 20, 656, 600, size=15, bold=True)
models = [new_view(model(name, stereotype="ORM model"), x, 690, 180, 45)
          for name, x in (("Cost", 20), ("CostLike", 220), ("User", 420))]
label("База данных", 20, 800, 600, size=15, bold=True)
tables = [new_view(model(name, stereotype="database table"), x, 835, 180, 45)
          for name, x in (("costs", 20), ("cost_likes", 220), ("users", 420))]

for page, interface in zip(pages, interfaces):
    dependency(page, interface)
for interface in interfaces:
    dependency(postman, interface, start=(320, 183))
for interface, domain in zip(interfaces, (domains[0], domains[2], domains[1], domains[3])):
    realization(domain, interface)
for domain, target in ((domains[0], models[0]), (domains[1], models[1]),
                       (domains[2], models[0]),
                       (domains[3], models[2])):
    dependency(domain, target)
for source, target in zip(models, tables):
    dependency(source, target)

PATH.write_text(json.dumps(project, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(PATH)
