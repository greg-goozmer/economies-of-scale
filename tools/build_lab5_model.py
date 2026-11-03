"""Append editable React classes to a copy of the existing single StarUML project."""
import copy
import json
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def walk(value):
    if isinstance(value, dict):
        yield value
        for item in value.values():
            yield from walk(item)
    elif isinstance(value, list):
        for item in value:
            yield from walk(item)


def uid():
    return uuid.uuid4().hex[:22]


def ref(value):
    return {'$ref': value['_id']}


def build():
    project = json.loads((ROOT / 'docs/costs_database.mdj').read_text(encoding='utf-8'))
    template = next(x for x in walk(project) if x.get('_type') == 'UMLClassView')
    model = dict(_type='UMLModel', _id=uid(), _parent=ref(project), name='Lab5 React frontend', ownedElements=[])
    diagram = dict(_type='UMLClassDiagram', _id=uid(), _parent=ref(model), name='Lab5 React classes (A4)', showGrid=False, ownedViews=[])
    model['ownedElements'].append(diagram)
    project['ownedElements'].append(model)
    views = {}
    specs = [('App', 'costs state и передача props', 240, 20),
             ('CostTilesPage', 'Плитка издержек /costs', 20, 175),
             ('CostFeedPage', 'Лента издержек /costs/feed/:costId', 460, 175),
             ('CostCodeFilter', 'Числовые границы и submit', 20, 345),
             ('CostCard', 'Карточка издержки и Link', 460, 345),
             ('CostTabBar', 'Лента и Плитка доступны', 240, 505),
             ('CostImage', 'Локальная картинка по умолчанию', 20, 665),
             ('CostVideo', 'Локальное видео по умолчанию', 460, 665),
             ('COSTS_MOCK', 'Коллекция издержек без API', 240, 825)]
    for name, description, x, y in specs:
        cls = dict(_type='UMLClass', _id=uid(), _parent=ref(model), name=name, documentation=description, attributes=[], operations=[])
        model['ownedElements'].append(cls)
        view = copy.deepcopy(template)
        mapping = {v['_id']: uid() for v in walk(view) if '_id' in v}
        for value in walk(view):
            if '_id' in value:
                value['_id'] = mapping[value['_id']]
            if '$ref' in value and value['$ref'] in mapping:
                value['$ref'] = mapping[value['$ref']]
            if 'font' in value:
                value['font'] = 'Arial;18;0'
        view.update(_parent=ref(diagram), model=ref(cls), left=x, top=y, width=300, height=90,
                    suppressAttributes=False, suppressOperations=False, showShadow=False, wordWrap=True)
        for part in view.get('subViews', []):
            part.update(model=ref(cls), left=x, width=300)
            if part['_type'] == 'UMLNameCompartmentView':
                part.update(top=y, height=56)
                for label in part.get('subViews', []):
                    label.update(visible=False, text='')
                    if label['_id'] == part['nameLabel']['$ref']:
                        label.update(visible=True, text=name, left=x+8, top=y+12, width=284, height=28, font='Arial;18;1')
            else:
                part.update(top=y+(56 if part['_type'] == 'UMLAttributeCompartmentView' else 72), height=16,
                            visible=part['_type'] in ('UMLAttributeCompartmentView', 'UMLOperationCompartmentView'), subViews=[])
        diagram['ownedViews'].append(view)
        views[name] = view
    for source, target in [('App', 'CostTilesPage'), ('App', 'CostFeedPage'), ('App', 'CostTabBar'),
                           ('CostTilesPage', 'CostCodeFilter'), ('CostTilesPage', 'CostCard'),
                           ('CostCard', 'CostImage'), ('CostFeedPage', 'CostVideo'),
                           ('App', 'COSTS_MOCK')]:
        a, b = views[source], views[target]
        dep = dict(_type='UMLDependency', _id=uid(), _parent=ref(model), source=a['model'], target=b['model'])
        model['ownedElements'].append(dep)
        diagram['ownedViews'].append(dict(_type='UMLDependencyView', _id=uid(), _parent=ref(diagram),
            model=ref(dep), tail=ref(a), head=ref(b), lineStyle=1,
            points=f"{a['left']+150}:{a['top']+90};{b['left']+150}:{b['top']}"))
    ids = [v['_id'] for v in walk(project) if '_id' in v]
    assert len(ids) == len(set(ids))
    assert all(v['$ref'] in ids for v in walk(project) if '$ref' in v)
    destination = ROOT / 'frontend/docs/costs_database.mdj'
    destination.write_text(json.dumps(project, ensure_ascii=False, indent=2), encoding='utf-8')
    print(destination)


if __name__ == '__main__':
    build()
