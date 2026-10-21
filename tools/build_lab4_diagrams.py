"""Build editable Lab4 UML views; preserve the existing ER model verbatim."""
import copy
import json
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "docs/costs_database.mdj"


def uid():
    return uuid.uuid4().hex[:22]


def ref(item):
    return {"$ref": item if isinstance(item, str) else item["_id"]}


def walk(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)


def build():
    project = json.loads(PATH.read_text(encoding="utf-8"))
    uml = next(e for e in project["ownedElements"] if e["_type"] == "UMLModel")
    old_diagram = next(e for e in uml["ownedElements"] if e["_type"] == "UMLClassDiagram")
    template = next(v for v in old_diagram["ownedViews"] if v["_type"] == "UMLClassView")
    interface_template = next(v for v in old_diagram["ownedViews"] if v["_type"] == "UMLInterfaceView")
    uml["ownedElements"] = []
    diagram = dict(_type="UMLClassDiagram", _id=uid(), _parent=ref(uml),
                   name="Lab4 classes and pages (A4)", showGrid=False, ownedViews=[])
    uml["ownedElements"].append(diagram)

    def model(name, kind="UMLClass", operations=()):
        item = dict(_type=kind, _id=uid(), _parent=ref(uml), name=name,
                    visibility="public", attributes=[], operations=[])
        for method, url, function in operations:
            item["operations"].append(dict(_type="UMLOperation", _id=uid(),
                _parent=ref(item), name=f"{method} {url}", visibility="public",
                documentation=f"api: {function}"))
        uml["ownedElements"].append(item)
        return item

    def clone(source, item, parent):
        view = copy.deepcopy(source)
        mapping = {x["_id"]: uid() for x in walk(view) if "_id" in x}
        mapping[source["model"]["$ref"]] = item["_id"]
        for x in walk(view):
            if "_id" in x:
                x["_id"] = mapping[x["_id"]]
            if "$ref" in x and x["$ref"] in mapping:
                x["$ref"] = mapping[x["$ref"]]
            if "font" in x:
                x["font"] = "Arial;18;" + x["font"].split(";")[-1]
            x.pop("containerView", None)
        view["_parent"] = ref(parent)
        return view

    def class_view(item, x, y, w, h, page=False, interface=False):
        view = clone(interface_template if interface else template, item, diagram)
        view.update(left=x, top=y, width=w, height=h, showShadow=False, wordWrap=True,
                    suppressAttributes=interface, suppressOperations=interface)
        for part in view["subViews"]:
            kind = part["_type"]
            part.update(model=ref(item), left=x, width=w)
            if kind == "UMLNameCompartmentView":
                part.update(top=y, height=68 if page else 33)
                for label in part["subViews"]:
                    label.update(left=x+5, top=y+6, width=w-10)
                    if label["_type"] == "LabelView":
                        label["text"] = item["name"] if label["_id"] == view["nameCompartment"]["$ref"] else label.get("text", "")
                for field in ("stereotypeLabel", "namespaceLabel", "propertyLabel"):
                    if field in part:
                        for label in part["subViews"]:
                            if label["_id"] == part[field]["$ref"]:
                                label.update(visible=False, text="")
                for label in part["subViews"]:
                    if label["_id"] == part["nameLabel"]["$ref"]:
                        label.update(text=item["name"], visible=True, height=60 if page else 23,
                                     wordWrap=True, font="Arial;18;1")
            elif kind == "UMLAttributeCompartmentView":
                part.update(top=y+(68 if page else 33), height=12, visible=not interface, subViews=[])
            elif kind == "UMLOperationCompartmentView":
                part.update(top=y+(80 if page else 45), height=max(12, h-45),
                            visible=not interface, subViews=[])
                for i, op in enumerate(item["operations"]):
                    part["subViews"].append(dict(_type="UMLOperationView", _id=uid(),
                        _parent=ref(part), model=ref(op), font="Arial;18;0", fontColor="#000000",
                        left=x+6, top=y+49+i*23, width=w-12, height=23,
                        text="+"+op["name"]+"()", horizontalAlignment=0))
            else:
                part.update(visible=False, subViews=[])
        diagram["ownedViews"].append(view)
        return view

    def text(value, x, y, w, size=18):
        diagram["ownedViews"].append(dict(_type="UMLTextView", _id=uid(), _parent=ref(diagram),
            text=value, left=x, top=y, width=w, height=30, font=f"Arial;{size};1",
            fontColor="#000000", horizontalAlignment=2, verticalAlignment=5))

    def frame(y, h, title):
        diagram["ownedViews"].append(dict(_type="UMLRectView", _id=uid(), _parent=ref(diagram),
            left=15, top=y, width=790, height=h, fillColor="#ffffff", lineColor="#000000"))
        text(title, 20, y+7, 780)

    def edge(source, target, kind="UMLDependency", points=None, multiplicities=None):
        item = dict(_type=kind, _id=uid(), _parent=ref(uml))
        if kind == "UMLAssociation":
            for end, view, multi in zip(("end1", "end2"), (source, target), multiplicities):
                item[end] = dict(_type="UMLAssociationEnd", _id=uid(), _parent=ref(item),
                                 reference=view["model"], multiplicity=multi, navigable="unspecified")
        else:
            item.update(source=source["model"], target=target["model"])
        uml["ownedElements"].append(item)
        if points is None:
            points = [(source["left"]+source["width"]/2, source["top"]+source["height"]),
                      (target["left"]+target["width"]/2, target["top"])]
        diagram["ownedViews"].append(dict(_type=kind+"View", _id=uid(), _parent=ref(diagram),
            model=ref(item), tail=ref(source), head=ref(target), lineStyle=1,
            points=";".join(f"{x}:{y}" for x, y in points)))

    frame(340, 285, "Бэкенд")
    frame(665, 165, "Модель")
    frame(870, 225, "База данных")
    page_titles = ["Список издержек\nCostsPage", "Добавление издержки\nCostDraftPage",
                   "Лента издержек\nCostFeedPage", "Вход пользователя\nUserLoginPage"]
    pages = []
    for x, title in zip((20, 220, 420, 620), page_titles):
        pages.append(class_view(model(title), x, 20, 180, 94, page=True))
    # Stable code names, while human-readable names appear in the editable view.
    for v, name in zip(pages, ("CostsPage", "CostDraftPage", "CostFeedPage", "UserLoginPage")):
        m = next(m for m in uml["ownedElements"] if m.get("_id") == v["model"]["$ref"])
        m["documentation"] = m["name"].split("\n")[0] + ". Планируемая страница SPA."
        m["name"] = name
        m["stereotype"] = m["documentation"].split(".")[0]
    postman_model = model("Postman")
    postman = class_view(postman_model, 355, 150, 110, 58)
    cost_routes = [("GET", "/api/costs", "list_costs"), ("GET", "/api/costs/feed", "get_cost_feed"),
        ("GET", "/api/costs/draft", "get_cost_draft"), ("POST", "/api/costs", "create_cost"),
        ("PUT", "/api/costs/{cost_id}", "publish_cost"),
        ("DELETE", "/api/costs/{cost_id}", "delete_cost"),
        ("POST", "/api/costs/{cost_id}/likes", "change_cost_like")]
    user_routes = [("POST", "/api/users", "register_user"),
        ("POST", "/api/users/auth", "authenticate_user"),
        ("POST", "/api/users/logout", "logout_user")]
    cost_model, user_model = model("CostApi", operations=cost_routes), model("UserApi", operations=user_routes)
    cost_model["stereotype"], user_model["stereotype"] = "Домен costs", "Домен users"
    api_cost = class_view(model("API costs", "UMLInterface"), 240, 267, 32, 32, interface=True)
    api_user = class_view(model("API users", "UMLInterface"), 640, 267, 32, 32, interface=True)
    text("API costs", 175, 305, 160)
    text("API users", 575, 305, 160)
    costs = class_view(cost_model, 30, 390, 455, 220)
    users = class_view(user_model, 510, 390, 280, 125)
    models = [class_view(model(n), x, 735, w, 60) for n, x, w in
              (("Cost", 50, 185), ("CostLike", 310, 200), ("User", 590, 180))]
    tables = [class_view(model(n), x, 940, w, 60) for n, x, w in
              (("costs", 80, 130), ("cost_likes", 330, 160), ("users", 615, 130))]
    for p in pages[:3]:
        edge(p, api_cost, kind="UMLUsage")
    edge(pages[3], api_user, kind="UMLUsage")
    for api, domain in ((api_cost, costs), (api_user, users)):
        edge(postman, api, kind="UMLUsage")
        edge(domain, api, kind="UMLInterfaceRealization",
             points=[(domain["left"]+domain["width"]/2,390),(api["left"]+16,299)])
    for domain, target in ((costs, models[0]), (costs, models[1]), (users, models[2])):
        edge(domain, target)
    for source, target in zip(models, tables):
        edge(source, target)
    edge(tables[0], tables[1], "UMLAssociation", [(210,970),(330,970)], ("1", "0..*"))
    edge(tables[1], tables[2], "UMLAssociation", [(490,970),(615,970)], ("0..*", "1"))
    edge(tables[2], tables[0], "UMLAssociation", [(680,1000),(680,1055),(145,1055),(145,1000)], ("1", "0..*"))

    # Native sequence messages reference the SAME operations as the class diagram.
    scenario = model("Cost publication scenario")
    interaction = dict(_type="UMLInteraction", _id=uid(), _parent=ref(scenario),
        name="Публикация и просмотр издержки", participants=[], messages=[], ownedElements=[])
    scenario["ownedElements"] = [interaction]
    seq = dict(_type="UMLSequenceDiagram", _id=uid(), _parent=ref(interaction),
        name="Lab4 sequence (A4)", showGrid=False, showSequenceNumber=True,
        showSignature=True, showActivation=False, ownedViews=[])
    interaction["ownedElements"].append(seq)
    lifelines = []
    for name, classifier, x in (("users", user_model, 20), ("client", postman_model, 340), ("costs", cost_model, 660)):
        role = dict(_type="UMLAttribute", _id=uid(), _parent=ref(scenario), name=name, type=ref(classifier))
        scenario["attributes"].append(role)
        life = dict(_type="UMLLifeline", _id=uid(), _parent=ref(interaction), name=name, represent=ref(role))
        interaction["participants"].append(life)
        view = clone(template, life, seq)
        view.update(_type="UMLSeqLifelineView", left=x, top=20, width=140, height=1120)
        view["subViews"] = [p for p in view["subViews"] if p["_type"] == "UMLNameCompartmentView"]
        namepart = view["subViews"][0]
        namepart.update(model=ref(life), left=x, top=20, width=140, height=40)
        for label in namepart["subViews"]:
            label.update(visible=label["_id"] == namepart["nameLabel"]["$ref"], left=x+4, top=27,
                         width=132, height=24, text=f"{name}:{classifier['name']}", font="Arial;17;1")
        for key in ("attributeCompartment", "operationCompartment", "receptionCompartment", "templateParameterCompartment"):
            view.pop(key, None)
        linepart = dict(_type="UMLLinePartView", _id=uid(), _parent=ref(view), model=ref(life),
                        left=x+70, top=60, width=1, height=1080, font="Arial;17;0")
        view["linePart"] = ref(linepart)
        view["subViews"].append(linepart)
        seq["ownedViews"].append(view)
        lifelines.append((life, view, linepart, x+70))
    ops = {op["documentation"].split(": ")[1]: op for m in (cost_model,user_model) for op in m["operations"]}
    steps = [
        (0, "authenticate_user", 'user_name, password', '200; Set-Cookie: cost_session=…'),
        (2, "list_costs", 'min_cost_code=20, max_cost_code=40', '200; [{cost_id, cost_code, is_owner}]'),
        (2, "create_cost", 'cost_name; image:File; video:File', '201; cost_id=ID, status=draft'),
        (2, "get_cost_draft", 'Cookie: cost_session=…', '200; cost_id=ID, status=draft'),
        (2, "publish_cost", 'cost_id=ID; cost_description,\ncost_behavior, cost_code', '200; cost_status=published, cost_formed_at'),
        (2, "get_cost_feed", 'без cost_id', '200; cost_id, like_count, is_liked'),
        (2, "get_cost_feed", 'cost_id=ID, next=true', '200; следующая издержка, cost_id'),
        (2, "change_cost_like", 'cost_id=ID; is_liked=1', '200; like_count, is_liked=1'),
    ]
    for index, (target_index, function, arguments, result) in enumerate(steps):
        for reply in (False, True):
            src, dst = (lifelines[target_index], lifelines[1]) if reply else (lifelines[1], lifelines[target_index])
            message = dict(_type="UMLMessage", _id=uid(), _parent=ref(interaction),
                name="" if reply else function, source=ref(src[0]), target=ref(dst[0]),
                messageSort="reply" if reply else "synchCall", sequenceNumber=str(index+1),
                arguments=result if reply else arguments)
            if not reply:
                message["signature"] = ref(ops[function])
            interaction["messages"].append(message)
            y = 120 + index*125 + (56 if reply else 0)
            mv = dict(_type="UMLSeqMessageView", _id=uid(), _parent=ref(seq), model=ref(message),
                tail=ref(src[2]), head=ref(dst[2]), points=f"{src[3]}:{y};{dst[3]}:{y}",
                lineStyle=1, font="Arial;17;0", subViews=[], showType=True, showProperty=False)
            for field, typ in (("nameLabel","EdgeLabelView"),("stereotypeLabel","EdgeLabelView"),
                               ("propertyLabel","EdgeLabelView"),("activation","UMLActivationView")):
                sub = dict(_type=typ, _id=uid(), _parent=ref(mv), model=ref(message),
                    font="Arial;17;0", wordWrap=True, visible=field=="nameLabel", hostEdge=ref(mv),
                    edgePosition=1, alpha=1.5707963267948966, distance=14,
                    left=min(src[3],dst[3]), top=y-43, width=320, height=38,
                    text=result if reply else ops[function]["name"]+"("+arguments+")")
                mv[field] = ref(sub)
                mv["subViews"].append(sub)
            seq["ownedViews"].append(mv)

    nodes = list(walk(project))
    ids = [n["_id"] for n in nodes if "_id" in n]
    assert len(ids) == len(set(ids)), "Duplicate IDs"
    assert not {n["$ref"] for n in nodes if "$ref" in n} - set(ids), "Dangling references"
    PATH.write_text(json.dumps(project, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(PATH)


if __name__ == "__main__":
    build()
